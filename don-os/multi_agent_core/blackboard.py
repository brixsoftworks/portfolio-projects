"""
multi_agent_core/blackboard.py — Shared Knowledge Blackboard & Artifact Store

Enables specialized agents to exchange findings, deliverables, and structured pages
without polluting each other's individual conversation contexts.
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

@dataclass
class KnowledgePage:
    page_id: str
    author_agent: str
    role: str
    title: str
    content: str
    timestamp: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SharedBlackboard:
    """Central blackboard holding living knowledge pages, shared deliverables, and audit logs."""
    
    def __init__(self):
        self.pages: Dict[str, KnowledgePage] = {}
        self.artifacts: Dict[str, Any] = {}
        self.event_log: List[Dict[str, Any]] = []

    def publish_page(
        self,
        page_id: str,
        author_agent: str,
        role: str,
        title: str,
        content: str,
        tags: Optional[List[str]] = None
    ) -> KnowledgePage:
        """Publishes or updates a knowledge page in the blackboard."""
        page = KnowledgePage(
            page_id=page_id,
            author_agent=author_agent,
            role=role,
            title=title,
            content=content,
            tags=tags or []
        )
        self.pages[page_id] = page
        self.log_event("PAGE_PUBLISHED", f"Agent '{author_agent}' published page: '{title}'")
        return page

    def get_page(self, page_id: str) -> Optional[KnowledgePage]:
        return self.pages.get(page_id)

    def publish_artifact(self, name: str, data: Any, author: str):
        self.artifacts[name] = {
            "data": data,
            "author": author,
            "timestamp": time.time()
        }
        self.log_event("ARTIFACT_STORED", f"Agent '{author}' saved artifact: '{name}'")

    def get_context_summary(self, max_length: int = 4000) -> str:
        """Generates a concise markdown digest of all current blackboard deliverables."""
        if not self.pages and not self.artifacts:
            return "No previous agent outputs published yet."

        sections = []
        for p in self.pages.values():
            sections.append(f"### [Knowledge Page] {p.title} (by {p.role})\n{p.content.strip()}\n")
        
        for k, a in self.artifacts.items():
            sections.append(f"### [Artifact] {k} (by {a['author']})\n{str(a['data'])[:500]}\n")

        full = "\n".join(sections)
        return full[:max_length]

    def log_event(self, event_type: str, message: str):
        self.event_log.append({
            "timestamp": time.time(),
            "time_str": time.strftime("%H:%M:%S"),
            "event_type": event_type,
            "message": message
        })

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return list(self.event_log)
