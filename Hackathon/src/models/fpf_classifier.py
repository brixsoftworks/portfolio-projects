import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import os

class FalsePositiveFilter:
    def __init__(self, model_name="microsoft/codebert-base", num_labels=2, model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
        
        if model_path and os.path.exists(model_path):
            self.model = RobertaForSequenceClassification.from_pretrained(model_path, num_labels=num_labels)
        else:
            self.model = RobertaForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
            
        self.model.to(self.device)
        self.model.eval()

    def predict(self, code_snippet: str, alert_message: str) -> float:
        """
        Predicts the probability that the alert is a TRUE POSITIVE.
        Combines the alert message and the code snippet.
        """
        input_text = f"Alert: {alert_message}\nCode:\n{code_snippet}"
        
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            # Class 1 is True Positive
            tp_prob = probabilities[0][1].item()
            
        return tp_prob

    def is_true_positive(self, code_snippet: str, alert_message: str, threshold: float = 0.5) -> bool:
        """Returns True if the probability exceeds the threshold."""
        prob = self.predict(code_snippet, alert_message)
        return prob >= threshold

if __name__ == "__main__":
    # Quick test
    fpf = FalsePositiveFilter()
    code = "def sql_query(user_id):\n    db.execute(f'SELECT * FROM users WHERE id = {user_id}')"
    alert = "Potential SQL Injection detected."
    prob = fpf.predict(code, alert)
    print(f"True Positive Probability: {prob:.4f}")
