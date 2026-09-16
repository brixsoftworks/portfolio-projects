import json
import os
from pydantic import BaseModel, Field
from typing import List
from src.models.llm_wrapper import LocalLLM

class PlannerOutput(BaseModel):
    files_to_scan: List[str] = Field(description="List of file paths that are high-risk and should be scanned.")
    reason: str = Field(description="Explanation of why these files were selected.")

class PlannerAgent:
    def __init__(self, llm: LocalLLM):
        self.llm = llm

    def plan(self, repo_path: str) -> PlannerOutput:
        """
        Analyzes the repository and creates a plan of files to scan.
        """
        files = []
        for root, _, filenames in os.walk(repo_path):
            for filename in filenames:
                if filename.endswith(".py") or filename.endswith(".js"):
                    files.append(os.path.join(root, filename))
        
        prompt = f"""
        You are the Planner Agent for a security auditor.
        Below is a list of files in the repository:
        {files}
        
        Which files are highest risk and should be scanned first?
        Output JSON matching exactly this schema: {json.dumps(PlannerOutput.model_json_schema())}
        """
        response = self.llm.generate(prompt)
        try:
            data = json.loads(response)
            return PlannerOutput(**data)
        except Exception:
            return PlannerOutput(files_to_scan=files[:2], reason="Fallback to first few files due to LLM parse error.")

if __name__ == "__main__":
    llm = LocalLLM(dummy_mode=True)
    planner = PlannerAgent(llm)
    print(planner.plan(".").json())
