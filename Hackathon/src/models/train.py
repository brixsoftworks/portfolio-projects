import json
import torch
import os
from torch.utils.data import Dataset, DataLoader
from transformers import RobertaTokenizer, RobertaForSequenceClassification, get_linear_schedule_with_warmup
from torch.optim import AdamW
from sklearn.metrics import accuracy_score, precision_score
import random

class VulnDataset(Dataset):
    def __init__(self, data_list, tokenizer, max_length=512):
        self.data = data_list
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = f"Alert: {item['alert']}\nCode:\n{item['code']}"
        inputs = self.tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        inputs = {k: v.squeeze(0) for k, v in inputs.items()}
        inputs['labels'] = torch.tensor(item['label'], dtype=torch.long)
        return inputs

def train_model(data_path="data/raw/synthetic_vulns.json", output_dir="models/proprietary/fpf_mini", epochs=3, batch_size=8):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Using device: {device}")
    
    # 1. Load Data and Split (80/20)
    with open(data_path, 'r') as f:
        full_data = json.load(f)
    random.shuffle(full_data)
    split_idx = int(len(full_data) * 0.8)
    train_data = full_data[:split_idx]
    val_data = full_data[split_idx:]
    
    print(f"[*] Training samples: {len(train_data)} | Validation samples: {len(val_data)}")

    # 2. Initialize CodeBERT Model
    model_name = "microsoft/codebert-base"
    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    model = RobertaForSequenceClassification.from_pretrained(model_name, num_labels=2)
    model.to(device)

    train_dataset = VulnDataset(train_data, tokenizer)
    val_dataset = VulnDataset(val_data, tokenizer)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # 3. Professional Optimizer and Scheduler Setup
    optimizer = AdamW(model.parameters(), lr=2e-5)
    total_steps = len(train_loader) * epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, 
        num_warmup_steps=int(total_steps * 0.1), 
        num_training_steps=total_steps
    )

    best_val_loss = float('inf')
    
    for epoch in range(epochs):
        # --- Training Loop ---
        model.train()
        total_train_loss = 0
        for batch in train_loader:
            optimizer.zero_grad()
            
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0) # Gradient clipping
            
            optimizer.step()
            scheduler.step()
            total_train_loss += loss.item()
            
        avg_train_loss = total_train_loss / len(train_loader)
        
        # --- Validation Loop ---
        model.eval()
        total_val_loss = 0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                
                outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
                total_val_loss += outputs.loss.item()
                
                preds = torch.argmax(outputs.logits, dim=-1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                
        avg_val_loss = total_val_loss / len(val_loader)
        acc = accuracy_score(all_labels, all_preds)
        
        print(f"Epoch {epoch+1}/{epochs}")
        print(f"  Train Loss: {avg_train_loss:.4f}")
        print(f"  Val Loss:   {avg_val_loss:.4f} | Val Accuracy: {acc:.4f}")
        
        # Model Checkpointing
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            os.makedirs(output_dir, exist_ok=True)
            model.save_pretrained(output_dir)
            tokenizer.save_pretrained(output_dir)
            print(f"  --> Model improved! Checkpoint saved to {output_dir}")

if __name__ == "__main__":
    train_model()
