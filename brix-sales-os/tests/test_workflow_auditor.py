"""
tests/test_workflow_auditor.py
==============================
Unit tests for the Workflow Capability Registry auditor.
"""

from pathlib import Path
from brix_sales_os.registry.workflow_auditor import run_full_audit, REGISTRY_OUTPUT_FILE

def test_workflow_audit_execution():
    registry = run_full_audit()
    assert len(registry) == 60, f"Expected 60 audited workflows, got {len(registry)}"
    assert REGISTRY_OUTPUT_FILE.exists()

    # Check structure of first workflow
    w1 = registry[0]
    assert w1["id"] == "WF-01"
    assert "node_count" in w1
    assert "input_schema" in w1
    assert "output_schema" in w1
    assert "operational_status" in w1
    assert "suggested_price" in w1
    assert w1["suggested_price"]["setup_usd"] > 0
