"""
tests/test_database.py
======================
Unit tests for Brix Sales OS database models, relationships, and constraints.
"""

import pytest
from brix_sales_os.database.session import SessionLocal, init_db
from brix_sales_os.database.models import (
    Organization, Contact, Deal, WorkflowRegistryItem, SuppressionEntry,
    OutreachMessage, Invoice, Payment, Project
)

def test_database_initialization():
    init_db()
    db = SessionLocal()
    try:
        wf_count = db.query(WorkflowRegistryItem).count()
        assert wf_count == 60, f"Expected 60 seeded workflows, found {wf_count}"
    finally:
        db.close()

def test_organization_and_contact_creation():
    db = SessionLocal()
    try:
        test_domain = "testagency_unit.com"
        # Cleanup if exists
        existing = db.query(Organization).filter_by(domain=test_domain).first()
        if existing:
            db.delete(existing)
            db.commit()

        org = Organization(
            name="Test Agency Unit",
            domain=test_domain,
            website="https://testagency_unit.com",
            industry="Marketing",
            country="United States"
        )
        db.add(org)
        db.commit()
        db.refresh(org)

        contact = Contact(
            organization_id=org.id,
            first_name="Jane",
            last_name="Doe",
            full_name="Jane Doe",
            email="jane@testagency_unit.com",
            role="CEO"
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)

        assert contact.id is not None
        assert contact.organization.name == "Test Agency Unit"

        # Cleanup
        db.delete(contact)
        db.delete(org)
        db.commit()
    finally:
        db.close()

def test_suppression_list():
    db = SessionLocal()
    try:
        test_email = "optout_user@testdomain.com"
        sup = db.query(SuppressionEntry).filter_by(email=test_email).first()
        if not sup:
            sup = SuppressionEntry(email=test_email, domain="testdomain.com", reason="UNSUBSCRIBE_TEST")
            db.add(sup)
            db.commit()

        found = db.query(SuppressionEntry).filter_by(email=test_email).first()
        assert found is not None
        assert found.reason == "UNSUBSCRIBE_TEST"

        # Cleanup
        db.delete(found)
        db.commit()
    finally:
        db.close()
