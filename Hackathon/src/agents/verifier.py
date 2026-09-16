import json
from pydantic import BaseModel, Field
from src.models.llm_wrapper import LocalLLM
from src.agents.reviewer import ReviewerOutput

class VerifierOutput(BaseModel):
    verified: bool = Field(description="True if the vulnerability is verified and exploitable, False if hallucination.")
    proof: str = Field(description="A logical proof, explanation, or mock payload demonstrating the exploit.")

class VerifierAgent:
    def __init__(self, llm: LocalLLM):
        self.llm = llm

    def verify(self, code: str, reviewer_output: ReviewerOutput) -> VerifierOutput:
        """
        Takes the Reviewer's output and independently verifies if the bug is real.
        Acts as a strict critic to prevent hallucinations.
        """
        if not reviewer_output.vulnerability_found:
            return VerifierOutput(verified=True, proof="No vulnerability reported to verify.")
            
        prompt = f"""
        You are the Verifier Agent for a security auditor.
        The Reviewer Agent found a vulnerability:
        {reviewer_output.model_dump_json(indent=2)}
        
        Code:
        {code}
        
        Can you construct a logical proof or a mock payload to exploit this?
        If yes, it's verified. If it relies on assumptions not in the code, reject it.
        Output JSON matching exactly this schema: {json.dumps(VerifierOutput.model_json_schema())}
        """
        response = self.llm.generate(prompt)
        try:
            data = json.loads(response)
            return VerifierOutput(**data)
        except Exception:
            return VerifierOutput(verified=False, proof="Failed to parse verification output.")

if __name__ == "__main__":
    llm = LocalLLM(dummy_mode=True)
    verifier = VerifierAgent(llm)
    rev_out = ReviewerOutput(vulnerability_found=True, type="Test")
    print(verifier.verify("print('test')", rev_out).json())
