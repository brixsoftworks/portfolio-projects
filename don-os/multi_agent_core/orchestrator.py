"""
multi_agent_core/orchestrator.py — Master Fleet Orchestrator

The central supervisor coordinating task perception, agent fleet deployment,
concurrent execution, shared blackboard knowledge exchange, and synthesis.
"""

import time
import asyncio
from typing import List, Dict, Any, Optional, Callable

from langchain_core.messages import SystemMessage, HumanMessage
from multi_agent_core.blackboard import SharedBlackboard
from multi_agent_core.action_gateway import GovernedActionGateway
from multi_agent_core.specialist_dot import SpecialistDot
from multi_agent_core.perception_planner import TaskPerceptionEngine

SYNTHESIS_SYSTEM_PROMPT = """
You are the Executive Supervisor for DON OS. 
Multiple specialized agents have executed their assigned sub-tasks to achieve the user's objective.
Your job is to synthesize all deliverables into a cohesive, beautifully structured final response.
Highlight the work completed by each specialist agent, key insights, and final deliverables.
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

class FleetOrchestrator:
    """Master supervisor orchestrating the autonomous multi-agent fleet."""

    def __init__(self, model_instance: Any, all_tools: Optional[List[Any]] = None):
        self.model = model_instance
        self.all_tools = all_tools or []
        self.blackboard = SharedBlackboard()
        self.gateway = GovernedActionGateway()
        self.perception_engine = TaskPerceptionEngine(self.model)

    async def execute_mission(
        self,
        user_goal: str,
        event_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """Runs the entire multi-agent lifecycle for a user goal."""
        mission_id = f"mission-{int(time.time()*1000) % 100000}"
        start_time = time.time()

        if event_callback:
            event_callback({
                "type": "mission_started",
                "mission_id": mission_id,
                "goal": user_goal,
                "timestamp": start_time
            })

        # Stage 1: Task Perception & DAG Planning
        if event_callback:
            event_callback({
                "type": "planning_started",
                "message": "Analyzing goal and synthesizing multi-agent DAG execution plan..."
            })

        plan = await self.perception_engine.decompose_goal(user_goal)

        if event_callback:
            event_callback({
                "type": "plan_created",
                "mission_id": mission_id,
                "plan": plan,
                "total_agents": len(plan)
            })

        # Stage 2: Fleet Deployment & Concurrent Execution
        executed_agents = []
        parallel_batch = []

        async def run_single_dot(step_info: Dict[str, Any]):
            agent_id = f"{step_info['role']}-{step_info['id']}"
            dot = SpecialistDot(
                agent_id=agent_id,
                role_key=step_info["role"],
                directive=step_info["directive"],
                model_instance=self.model,
                all_tools=self.all_tools,
                blackboard=self.blackboard,
                gateway=self.gateway
            )

            if event_callback:
                event_callback({
                    "type": "agent_spawned",
                    "agent_id": agent_id,
                    "role": dot.role_info["title"],
                    "title": step_info.get("title", step_info["id"]),
                    "directive": step_info["directive"]
                })

            result = await dot.run(progress_callback=event_callback)
            return {
                "step_id": step_info["id"],
                "agent_id": agent_id,
                "role": dot.role_info["title"],
                "directive": step_info["directive"],
                "output": result
            }

        for step in plan:
            if step.get("run_parallel", False):
                parallel_batch.append(step)
            else:
                # If there are accumulated parallel tasks, execute them together first
                if parallel_batch:
                    if event_callback:
                        event_callback({
                            "type": "parallel_batch_started",
                            "batch_size": len(parallel_batch),
                            "message": f"Deploying {len(parallel_batch)} agents concurrently..."
                        })
                    batch_results = await asyncio.gather(*[run_single_dot(s) for s in parallel_batch])
                    executed_agents.extend(batch_results)
                    parallel_batch = []

                # Execute sequential task
                res = await run_single_dot(step)
                executed_agents.append(res)

        # Flush any remaining parallel batch
        if parallel_batch:
            if event_callback:
                event_callback({
                    "type": "parallel_batch_started",
                    "batch_size": len(parallel_batch),
                    "message": f"Deploying {len(parallel_batch)} agents concurrently..."
                })
            batch_results = await asyncio.gather(*[run_single_dot(s) for s in parallel_batch])
            executed_agents.extend(batch_results)

        # Stage 3: Master Synthesis
        if event_callback:
            event_callback({
                "type": "synthesis_started",
                "message": "Synthesizing fleet deliverables into final executive response..."
            })

        knowledge_digest = self.blackboard.get_context_summary()
        synthesis_prompt = (
            f"User Objective:\n\"{user_goal}\"\n\n"
            f"Deliverables from Fleet Agents:\n"
            f"{knowledge_digest}\n\n"
            f"Synthesize the complete findings, implementations, and verification notes into a structured report."
        )

        try:
            synthesis_res = await asyncio.to_thread(
                self.model.invoke,
                [
                    SystemMessage(content=SYNTHESIS_SYSTEM_PROMPT),
                    HumanMessage(content=synthesis_prompt)
                ]
            )
            final_response = _clean_content(synthesis_res.content) if hasattr(synthesis_res, "content") else str(synthesis_res)
        except Exception as ex:
            final_response = f"Fleet execution completed successfully.\n\nSummary:\n{knowledge_digest}"

        total_elapsed = round(time.time() - start_time, 2)

        mission_result = {
            "status": "success",
            "mission_id": mission_id,
            "user_goal": user_goal,
            "response": final_response,
            "elapsed_seconds": total_elapsed,
            "agents_deployed": len(executed_agents),
            "agent_details": executed_agents,
            "blackboard_pages": [p.to_dict() for p in self.blackboard.pages.values()],
            "audit_trail": self.gateway.action_history
        }

        if event_callback:
            event_callback({
                "type": "mission_completed",
                "mission_id": mission_id,
                "elapsed_seconds": total_elapsed,
                "agents_count": len(executed_agents)
            })

        return mission_result
