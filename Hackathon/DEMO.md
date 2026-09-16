# Live Demo Instructions

The live demo is designed to run completely offline (airplane mode).

1. Ensure the `.venv` is activated.
2. Run `streamlit run src/ui/app.py`.
3. The UI will default to scanning the `demo_repo` folder.
4. `demo_repo/auth.py` contains a deliberate SQL Injection vulnerability.
5. Click **Run Audit**.
6. Observe the Planner, Reviewer, and Verifier agents discussing the code and producing a final verified proof-of-concept payload.
