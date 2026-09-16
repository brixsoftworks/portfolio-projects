import os
import subprocess
import json
from src.models.llm_wrapper import LocalLLM
from src.models.fpf_classifier import FalsePositiveFilter
from src.agents.planner import PlannerAgent
from src.agents.reviewer import ReviewerAgent
from src.agents.verifier import VerifierAgent
from src.agents.rag_engine import CodeRAGEngine

class SentinelOrchestrator:
    def __init__(self, use_dummy_llm=True):
        self.llm = LocalLLM(dummy_mode=use_dummy_llm)
        
        # Load the actual trained model if it exists
        model_path = "models/proprietary/fpf_mini"
        if os.path.exists(model_path):
            self.fpf = FalsePositiveFilter(model_path=model_path)
        else:
            self.fpf = FalsePositiveFilter() # Fallback
            
        self.rag = CodeRAGEngine()
            
        self.planner = PlannerAgent(self.llm)
        self.reviewer = ReviewerAgent(self.llm, self.fpf, self.rag)
        self.verifier = VerifierAgent(self.llm)

    def run_bandit(self, file_path: str) -> list:
        """Runs Bandit on a file and returns alert messages."""
        try:
            result = subprocess.run(
                [".venv/bin/bandit", "-f", "json", file_path],
                capture_output=True, text=True
            )
            # Bandit returns non-zero if issues are found
            if not result.stdout:
                return []
                
            data = json.loads(result.stdout)
            alerts = []
            for issue in data.get("results", []):
                alerts.append(f"{issue['issue_severity']} severity: {issue['issue_text']} (Line {issue['line_number']})")
            return alerts
        except Exception as e:
            return [f"Bandit execution error: {str(e)}"]

    def run_audit(self, repo_path: str, max_retries: int = 3):
        """
        Runs the full agentic loop over the repository as a generator for UI streaming.
        """
        yield {"type": "status", "message": f"Starting Sentinel-Local Audit on {repo_path}"}
        
        # 0. RAG Ingestion
        yield {"type": "status", "message": "Ingesting codebase into ChromaDB Vector Store for RAG..."}
        self.rag.ingest_repository(repo_path)
        yield {"type": "status", "message": "Codebase RAG ingestion complete."}
        
        # 1. Plan
        plan = self.planner.plan(repo_path)
        files_to_scan = plan.files_to_scan
        yield {"type": "planner", "message": f"Found {len(files_to_scan)} files. Reason: {plan.reason}"}
        
        results = []
        
        # 2. Execute & Verify Loop
        for file_path in files_to_scan:
            yield {"type": "status", "message": f"Auditing: {file_path}"}
            
            # Run Bandit
            static_alerts = self.run_bandit(file_path)
            yield {"type": "bandit", "message": f"Bandit found {len(static_alerts)} raw alerts."}
            
            attempt = 0
            verified = False
            final_report = None
            
            while attempt < max_retries and not verified:
                attempt += 1
                yield {"type": "status", "message": f"Attempt {attempt}/{max_retries}"}
                
                # Review
                review_out = self.reviewer.review(file_path, static_alerts)
                if not review_out.vulnerability_found:
                    yield {"type": "reviewer", "message": "No vulnerability found.", "success": True}
                    break
                    
                yield {"type": "reviewer", "message": f"Found: {review_out.type}\n{review_out.explanation}", "success": False}
                
                # Verify
                with open(file_path, 'r') as f:
                    code = f.read()
                verify_out = self.verifier.verify(code, review_out)
                
                if verify_out.verified:
                    yield {"type": "verifier", "message": f"VULNERABILITY VERIFIED.\nProof: {verify_out.proof}", "success": False}
                    final_report = review_out.model_dump()
                    final_report["proof"] = verify_out.proof
                    verified = True
                else:
                    yield {"type": "verifier", "message": f"REJECTED. Hallucination detected.\nReason: {verify_out.proof}", "success": True}
            
            if final_report:
                results.append({"file": file_path, "report": final_report})
                
        yield {"type": "complete", "results": results}

if __name__ == "__main__":
    orchestrator = SentinelOrchestrator(use_dummy_llm=True)
    for event in orchestrator.run_audit("demo_repo"):
        print(event)
