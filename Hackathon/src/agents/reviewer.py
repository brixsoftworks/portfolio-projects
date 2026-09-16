import json
import os
from pydantic import BaseModel, Field
from typing import List, Optional
from src.models.llm_wrapper import LocalLLM
from src.models.fpf_classifier import FalsePositiveFilter
from src.agents.rag_engine import CodeRAGEngine

class ReviewerOutput(BaseModel):
    vulnerability_found: bool = Field(description="True if a vulnerability was found, False otherwise.")
    type: Optional[str] = Field(None, description="The type of vulnerability (e.g., SQL Injection, XSS).")
    explanation: Optional[str] = Field(None, description="Explanation of how the vulnerability works.")
    affected_lines: Optional[List[int]] = Field(None, description="Line numbers where the vulnerability occurs.")

class ReviewerAgent:
    def __init__(self, llm: LocalLLM, fpf: FalsePositiveFilter = None, rag: CodeRAGEngine = None):
        self.llm = llm
        self.fpf = fpf
        self.rag = rag

    def review(self, file_path: str, static_analysis_alerts: list = None) -> ReviewerOutput:
        """
        Reviews a specific file. 
        1. Uses FPF to filter static alerts.
        2. Queries RAG engine for cross-file context.
        3. Uses LLM to find the bug.
        """
        if not os.path.exists(file_path):
            return ReviewerOutput(vulnerability_found=False, explanation="File not found")
            
        with open(file_path, 'r') as f:
            code = f.read()

        # Step 1: False Positive Filter (Proprietary Component)
        filtered_alerts = []
        if static_analysis_alerts and self.fpf:
            for alert in static_analysis_alerts:
                if self.fpf.is_true_positive(code, alert):
                    filtered_alerts.append(alert)
        else:
            filtered_alerts = static_analysis_alerts or []

        # Step 2: RAG Context Retrieval
        rag_context = ""
        if self.rag:
            rag_context = self.rag.query_context(code)

        # Step 3: LLM Deep Analysis with RAG Context
        prompt = f"""
        You are the Reviewer Agent for a security auditor.
        Review the following code for vulnerabilities.
        
        Static analysis hints: {filtered_alerts}
        
        Code under review:
        {code}
        
        Cross-file RAG Context (Dependencies/Imports):
        {rag_context}
        
        Output JSON matching exactly this schema: {ReviewerOutput.schema_json()}
        """
        response = self.llm.generate(prompt)
        try:
            data = json.loads(response)
            return ReviewerOutput(**data)
        except Exception:
            return ReviewerOutput(vulnerability_found=False, explanation="Failed to parse LLM output.")

if __name__ == "__main__":
    llm = LocalLLM(dummy_mode=True)
    reviewer = ReviewerAgent(llm)
    print(reviewer.review("src/models/llm_wrapper.py").json())
