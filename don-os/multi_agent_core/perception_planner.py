"""
multi_agent_core/perception_planner.py — Task Perception & DAG Decomposition Engine

Analyzes high-level user goals, determines domain competencies, and constructs
a Directed Acyclic Graph (DAG) for concurrent or sequential multi-agent execution.
"""

import json
import asyncio
from typing import List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

PLANNER_SYSTEM_PROMPT = """
You are the Master Task Perception & Planning Engine for an autonomous AI fleet.
Your job is to examine a high-level user goal, analyze its domains, and decompose it into 1 to 4 specialized atomic sub-tasks.

Available Specialist Agent Roles:
1. "researcher" - Information gathering, web searching, documentation reading, data synthesis.
2. "coder" - Writing code, creating files, refactoring, modifying logic.
3. "auditor" - Running verification, checking security, executing tests, reviewing output.
4. "architect" - High-level system design, schema specification, component architecture.

RULES FOR PARALLEL EXECUTION:
- If two tasks are independent (e.g. Researching references AND inspecting local code), set "run_parallel": true.
- If a task depends on outputs from a prior step (e.g. writing a patch based on research), set "run_parallel": false.

Output FORMAT (Respond with ONLY valid JSON, no markdown fences, no conversational filler):
[
  {
    "id": "task_1",
    "role": "researcher",
    "title": "Short descriptive title",
    "directive": "Detailed actionable instructions for this specialist",
    "run_parallel": true
  }
]
"""

def _clean_content(content: Any) -> str:
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)

class TaskPerceptionEngine:
    """Perception and task decomposition engine."""

    def __init__(self, planner_model: Any):
        self.model = planner_model

    async def decompose_goal(self, user_goal: str) -> List[Dict[str, Any]]:
        """Decomposes a user goal into an executable multi-agent DAG."""
        prompt = f"USER GOAL TO DECOMPOSE:\n\"{user_goal}\""
        
        try:
            response = await asyncio.to_thread(
                self.model.invoke,
                [
                    SystemMessage(content=PLANNER_SYSTEM_PROMPT),
                    HumanMessage(content=prompt)
                ]
            )
            raw = _clean_content(response.content if hasattr(response, "content") else str(response)).strip()

            # Strip markdown if present
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()

            parsed = json.loads(raw)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed
        except Exception as e:
            # Fallback heuristic decomposition if model returns non-json
            pass

        # Smart heuristic fallback based on intent keywords
        goal_lower = user_goal.lower()
        plan = []

        if any(w in goal_lower for w in ["research", "search", "cve", "find", "check"]):
            plan.append({
                "id": "task_1",
                "role": "researcher",
                "title": "Domain Research & Intelligence",
                "directive": f"Gather critical data and context for: {user_goal}",
                "run_parallel": True
            })
            plan.append({
                "id": "task_2",
                "role": "coder",
                "title": "Implementation & Synthesis",
                "directive": f"Implement or synthesize solution based on research findings for: {user_goal}",
                "run_parallel": False
            })
        else:
            plan.append({
                "id": "task_1",
                "role": "coder",
                "title": "Core Implementation",
                "directive": f"Execute implementation tasks for: {user_goal}",
                "run_parallel": False
            })
            plan.append({
                "id": "task_2",
                "role": "auditor",
                "title": "Quality & Verification Audit",
                "directive": f"Verify correctness, integrity, and test output for: {user_goal}",
                "run_parallel": False
            })

        return plan
