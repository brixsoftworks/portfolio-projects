import json
import random
import os

def generate_synthetic_dataset(num_samples: int = 200, output_path: str = "data/raw/synthetic_vulns.json"):
    """
    Generates a synthetic dataset of True Positive and False Positive static analysis alerts.
    """
    templates_tp = [
        ("def login(username, password):\n    db.execute(f'SELECT * FROM users WHERE user={username}')", "SQL Injection", 1),
        ("<div>{user_input}</div>", "Cross-Site Scripting (XSS)", 1),
        ("import os\nos.system('ping ' + user_ip)", "Command Injection", 1),
        ("with open(user_filename, 'r') as f:\n    data = f.read()", "Path Traversal", 1),
    ]

    templates_fp = [
        ("def login(username, password):\n    # TODO: remove db.execute(f'SELECT * FROM users WHERE user={username}')", "SQL Injection", 0),
        ("<div>{'Hello World'}</div>", "Cross-Site Scripting (XSS)", 0),
        ("import os\nos.system('ping 127.0.0.1')", "Command Injection", 0),
        ("with open('config.json', 'r') as f:\n    data = f.read()", "Path Traversal", 0),
        ("def safe_query(user_id):\n    return db.execute('SELECT * FROM users WHERE id=?', (user_id,))", "SQL Injection", 0)
    ]

    dataset = []
    for _ in range(num_samples):
        if random.choice([True, False]):
            code, alert, label = random.choice(templates_tp)
        else:
            code, alert, label = random.choice(templates_fp)
            
        # Add some random noise to make it slightly harder
        noise = f"\n# id: {random.randint(1000,9999)}\n"
        dataset.append({
            "code": code + noise,
            "alert": alert,
            "label": label
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=4)
    print(f"Generated {num_samples} samples at {output_path}")

if __name__ == "__main__":
    generate_synthetic_dataset()
