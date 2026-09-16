import os
import json

class LocalLLM:
    def __init__(self, model_path=None, dummy_mode=True):
        self.dummy_mode = dummy_mode
        self.model_path = model_path
        
        if not dummy_mode and model_path:
            # In a real environment, we'd initialize llama.cpp here
            # from llama_cpp import Llama
            # self.llm = Llama(model_path=model_path, n_ctx=4096)
            pass

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.1) -> str:
        """Generates a response from the local LLM."""
        if self.dummy_mode:
            return self._dummy_generate(prompt)
            
        # Real local generation would go here
        # return self.llm(prompt, max_tokens=max_tokens, temperature=temperature)["choices"][0]["text"]
        return "Not implemented."

    def _dummy_generate(self, prompt: str) -> str:
        """Returns canned responses for rapid prototyping."""
        prompt_lower = prompt.lower()
        if "plan" in prompt_lower:
            return json.dumps({
                "files_to_scan": ["src/auth.py", "src/db.py"],
                "reason": "These files contain authentication and database queries, which are high-risk."
            })
        elif "review" in prompt_lower:
            return json.dumps({
                "vulnerability_found": True,
                "type": "SQL Injection",
                "explanation": "The user input is concatenated directly into the SQL query string.",
                "affected_lines": [4, 5]
            })
        elif "verify" in prompt_lower:
            return json.dumps({
                "verified": True,
                "proof": "I constructed a payload `' OR 1=1 --` which successfully modifies the query logic."
            })
        return "I am a local LLM. I have analyzed your request."

if __name__ == "__main__":
    llm = LocalLLM()
    print("Planner response:", llm.generate("Please plan the security review."))
