import streamlit as st
import sys
import os
import time

# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.orchestrator import SentinelOrchestrator

def main():
    st.set_page_config(page_title="Sentinel-Local Pro", layout="wide", page_icon="🛡️")
    
    st.sidebar.title("🛡️ Sentinel-Local")
    st.sidebar.markdown("### Air-Gapped Security Auditor")
    st.sidebar.markdown("---")
    
    repo_path = st.sidebar.text_input("Repository Path", value="demo_repo")
    use_dummy_llm = st.sidebar.checkbox("Use Dummy LLM (Fast Prototyping)", value=True)
    
    st.sidebar.markdown("---")
    run_audit = st.sidebar.button("🚀 Run Audit", type="primary")

    # Create Tabs
    tab_dashboard, tab_agent_brain, tab_settings = st.tabs(["📊 Dashboard", "🧠 Agent Brain", "⚙️ Settings"])
    
    # Initialize state
    if "metrics" not in st.session_state:
        st.session_state.metrics = {"files_scanned": 0, "alerts_filtered": 0, "vulns_verified": 0}
    if "results" not in st.session_state:
        st.session_state.results = []

    with tab_dashboard:
        st.title("Audit Dashboard")
        
        # KPIs
        col1, col2, col3 = st.columns(3)
        m1 = col1.metric("Files Scanned", st.session_state.metrics["files_scanned"])
        m2 = col2.metric("Alerts Filtered (FPF)", st.session_state.metrics["alerts_filtered"])
        m3 = col3.metric("Verified Vulnerabilities", st.session_state.metrics["vulns_verified"])
        
        st.markdown("---")
        st.subheader("Verified Vulnerability Report")
        
        report_container = st.empty()
        if not st.session_state.results and not run_audit:
            report_container.info("No audit has been run yet or repository is secure.")
        elif st.session_state.results:
            for res in st.session_state.results:
                with st.expander(f"🚨 {res['report'].get('type', 'Vulnerability')} in {res['file']}", expanded=True):
                    st.write(f"**Explanation:** {res['report'].get('explanation', 'N/A')}")
                    st.write(f"**Affected Lines:** {res['report'].get('affected_lines', 'N/A')}")
                    st.code(res['report'].get('proof', ''), language="markdown")

    with tab_agent_brain:
        st.title("Agentic Thought Process")
        st.markdown("Live streaming the internal state of the multi-agent system.")
        log_container = st.container()

    if run_audit:
        # Reset state
        st.session_state.metrics = {"files_scanned": 0, "alerts_filtered": 0, "vulns_verified": 0}
        st.session_state.results = []
        
        orchestrator = SentinelOrchestrator(use_dummy_llm=use_dummy_llm)
        
        with tab_agent_brain:
            with log_container:
                for event in orchestrator.run_audit(repo_path):
                    etype = event["type"]
                    msg = event.get("message", "")
                    
                    if etype == "status":
                        st.info(f"🔄 {msg}")
                    elif etype == "planner":
                        st.success(f"🗺️ **Planner Agent**: {msg}")
                        # Update metric (approx)
                        st.session_state.metrics["files_scanned"] = int(msg.split(' ')[1]) if 'Found' in msg else 0
                        m1.metric("Files Scanned", st.session_state.metrics["files_scanned"])
                    elif etype == "bandit":
                        st.warning(f"🔍 **Static Analysis (Bandit)**: {msg}")
                        alerts_found = int(msg.split(' ')[2]) if 'found' in msg else 0
                        st.session_state.metrics["alerts_filtered"] += alerts_found
                        m2.metric("Alerts Filtered (FPF)", st.session_state.metrics["alerts_filtered"])
                    elif etype == "reviewer":
                        if event.get("success"):
                            st.success(f"✅ **Reviewer Agent**: {msg}")
                        else:
                            st.error(f"⚠️ **Reviewer Agent**: {msg}")
                    elif etype == "verifier":
                        if event.get("success"):
                            st.success(f"✅ **Verifier Agent (Critic)**: {msg}")
                        else:
                            st.error(f"🚨 **Verifier Agent (Critic)**: {msg}")
                    elif etype == "complete":
                        st.session_state.results = event.get("results", [])
                        st.session_state.metrics["vulns_verified"] = len(st.session_state.results)
                        m3.metric("Verified Vulnerabilities", st.session_state.metrics["vulns_verified"])
                        st.balloons()
                    
                    time.sleep(0.5) # Slight delay for visual effect of agents thinking
        
        # Update Dashboard Report after run
        with tab_dashboard:
            report_container.empty()
            if not st.session_state.results:
                report_container.success("Audit complete. Repository is secure.")
            else:
                for res in st.session_state.results:
                    with report_container.expander(f"🚨 {res['report'].get('type', 'Vulnerability')} in {res['file']}", expanded=True):
                        st.write(f"**Explanation:** {res['report'].get('explanation', 'N/A')}")
                        st.write(f"**Affected Lines:** {res['report'].get('affected_lines', 'N/A')}")
                        st.code(res['report'].get('proof', ''), language="markdown")

if __name__ == "__main__":
    main()
