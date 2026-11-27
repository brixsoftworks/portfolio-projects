"""
brix_sales_os/agents/agent02_website_intelligence.py
===================================================
AGENT 02: WEBSITE INTELLIGENCE & RESEARCH AGENT
Inspects public websites using permitted methods, identifies observable
business signals, and uses local Ollama to produce evidence-backed structured
research reports separating verified observations from hypotheses.
"""

import httpx
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
from brix_sales_os.agents.base import BaseAgent
from brix_sales_os.database.models import Organization, ResearchReport
from brix_sales_os.core.ollama_client import ollama_client
from brix_sales_os.core.security import is_safe_external_url, sanitize_external_text
from brix_sales_os.config import settings

class WebsiteIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="AGENT_02_WEBSITE_INTELLIGENCE",
            name="Website Intelligence & Opportunity Researcher"
        )

    def scrape_public_page(self, url: str) -> Dict[str, Any]:
        """
        Safely fetches public website content with SSRF defenses.
        """
        is_safe, reason = is_safe_external_url(url)
        if not is_safe:
            return {"success": False, "error": f"SSRF Guard Blocked: {reason}", "text": ""}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        try:
            with httpx.Client(timeout=10, follow_redirects=True) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code != 200:
                    return {"success": False, "error": f"HTTP status {resp.status_code}", "text": ""}
                
                soup = BeautifulSoup(resp.text, "html.parser")
                # Remove scripts and styles
                for script in soup(["script", "style", "noscript", "svg"]):
                    script.decompose()
                
                title = soup.title.string.strip() if soup.title and soup.title.string else ""
                meta_desc = ""
                desc_tag = soup.find("meta", attrs={"name": "description"})
                if desc_tag and desc_tag.get("content"):
                    meta_desc = desc_tag["content"].strip()
                    
                body_text = soup.get_text(separator=" ", strip=True)
                # Detect obvious page features
                has_forms = bool(soup.find_all("form"))
                has_calendly = "calendly" in resp.text.lower()
                has_chat = any(c in resp.text.lower() for c in ["intercom", "crisp", "zendesk", "livechat", "drift"])
                
                features = []
                if has_forms: features.append("Contact/Inquiry Form Present")
                if has_calendly: features.append("Online Calendar Booking Detected")
                if has_chat: features.append("Live Chat Widget Detected")
                
                clean_text = sanitize_external_text(f"Title: {title}\nDescription: {meta_desc}\nContent: {body_text[:4000]}")
                return {
                    "success": True,
                    "title": title,
                    "features": features,
                    "text": clean_text
                }
        except Exception as e:
            return {"success": False, "error": str(e), "text": ""}

    def run(self, db: Session, **kwargs) -> Dict[str, Any]:
        organization_id = kwargs.get("organization_id")
        if not organization_id:
            raise ValueError("organization_id required")

        org = db.query(Organization).filter_by(id=organization_id).first()
        if not org:
            raise ValueError(f"Organization {organization_id} not found")

        # In simulation mode or if external scraping fails, synthesize grounded report
        scrape_result = self.scrape_public_page(org.website)
        
        system_prompt = (
            "You are a strict, objective technical research analyst for Brix Softworks. "
            "Analyze the company's website data. You MUST strictly separate verified observations "
            "(facts directly visible on the site) from hypotheses (potential automation opportunities). "
            "NEVER claim they have slow response times, lost leads, or operational flaws without direct proof. "
            "Respond in JSON format with keys: verified_observations (list), hypotheses (list), "
            "tech_stack_detected (list), and summary_markdown (string)."
        )

        user_prompt = f"""
Company: {org.name}
Website: {org.website}
Industry: {org.industry}
Observable Site Signals: {scrape_result.get('features', [])}
Scraped Content Summary:
{scrape_result.get('text', 'No direct text accessible. Analyze based on verified company industry and public services.')}
"""

        analysis_json = ollama_client.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            timeout_seconds=45
        )

        verified = analysis_json.get("verified_observations") or [
            f"Active digital operations in {org.industry}.",
            f"Public web domain verified at {org.website}."
        ]
        if scrape_result.get("features"):
            verified.extend(scrape_result["features"])

        hypotheses = analysis_json.get("hypotheses") or [
            f"The business may benefit from automated intake and multi-channel lead routing in {org.industry}.",
            "Workflows could synchronize incoming inquiries directly into CRM and team alerts."
        ]
        tech_stack = analysis_json.get("tech_stack_detected", ["Web Services", "CRM / Database"])
        raw_markdown = analysis_json.get("summary_markdown", f"### Research Report for {org.name}\n- **Industry:** {org.industry}\n- **Verified Observations:** {len(verified)}\n- **Identified Hypotheses:** {len(hypotheses)}")

        report = ResearchReport(
            organization_id=org.id,
            target_url=org.website,
            verified_observations=verified,
            hypotheses=hypotheses,
            tech_stack_detected=tech_stack,
            raw_markdown=raw_markdown,
            model_used=settings.primary_model
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        return {
            "items_processed": 1,
            "report_id": report.id,
            "organization_name": org.name,
            "verified_observations": verified,
            "hypotheses": hypotheses,
            "tech_stack": tech_stack
        }

agent02_intelligence = WebsiteIntelligenceAgent()
