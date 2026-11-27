"""
brix_sales_os/agents/__init__.py
================================
Exports all 12 Brix Sales OS Agents.
"""

from brix_sales_os.agents.agent01_lead_discovery import agent01_discovery
from brix_sales_os.agents.agent02_website_intelligence import agent02_intelligence
from brix_sales_os.agents.agent03_lead_scoring import agent03_scoring
from brix_sales_os.agents.agent04_solution_matching import agent04_matching
from brix_sales_os.agents.agent05_demo_generator import agent05_demo
from brix_sales_os.agents.agent06_outreach_copywriter import agent06_copywriter
from brix_sales_os.agents.agent07_campaign_manager import agent07_campaign
from brix_sales_os.agents.agent08_inbox_manager import agent08_inbox
from brix_sales_os.agents.agent09_meeting_booking import agent09_meeting
from brix_sales_os.agents.agent10_proposal_generator import agent10_proposal
from brix_sales_os.agents.agent11_closing_assistant import agent11_closing
from brix_sales_os.agents.agent12_onboarding import agent12_onboarding

ALL_AGENTS = [
    agent01_discovery,
    agent02_intelligence,
    agent03_scoring,
    agent04_matching,
    agent05_demo,
    agent06_copywriter,
    agent07_campaign,
    agent08_inbox,
    agent09_meeting,
    agent10_proposal,
    agent11_closing,
    agent12_onboarding,
]
