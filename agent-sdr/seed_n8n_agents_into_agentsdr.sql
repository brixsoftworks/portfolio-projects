-- seed_n8n_agents_into_agentsdr.sql
-- Direct connection of n8n agent offerings, target accounts, campaigns, and leads into AgentSDR

DO $$
DECLARE
    org_id uuid := '8f613d93-6e40-4777-b827-4165812ee754'; -- Brix Softworks
    pipeline_id uuid := gen_random_uuid();
    
    -- Companies
    comp_flowpulse uuid := gen_random_uuid();
    comp_aiguild uuid := gen_random_uuid();
    comp_nexa uuid := gen_random_uuid();
    comp_vance uuid := gen_random_uuid();
    comp_apex uuid := gen_random_uuid();
    comp_swiss uuid := gen_random_uuid();
    comp_indie uuid := gen_random_uuid();

    -- People
    p_alex uuid := gen_random_uuid();
    p_sarah uuid := gen_random_uuid();
    p_karan uuid := gen_random_uuid();
    p_elena uuid := gen_random_uuid();
    p_david uuid := gen_random_uuid();
    p_luca uuid := gen_random_uuid();
    p_marcus uuid := gen_random_uuid();

    -- Campaigns
    c_whatsapp uuid := gen_random_uuid();
    c_private_ai uuid := gen_random_uuid();
    c_retainer uuid := gen_random_uuid();
    c_pack uuid := gen_random_uuid();
BEGIN
    -- 1. Create Default CRM Pipeline
    INSERT INTO crm_pipelines (id, name, is_default, active, organization_id, created_at, updated_at)
    VALUES (pipeline_id, 'n8n Client Acquisition Pipeline', true, true, org_id, now(), now())
    ON CONFLICT (organization_id, name) DO NOTHING;

    -- 2. Insert Target Companies
    INSERT INTO companies (id, name, domain, source, organization_id, created_at, updated_at, custom, raw)
    VALUES
        (comp_flowpulse, 'FlowPulse', 'flowpulse.io', 'n8n_community', org_id, now(), now(), '{"budget": 1200, "industry": "B2B SaaS"}'::jsonb, '{}'::jsonb),
        (comp_aiguild, 'AI Automation Guild', 'aiautomationguild.com', 'discord_radar', org_id, now(), now(), '{"budget": 2000, "industry": "AI & Research"}'::jsonb, '{}'::jsonb),
        (comp_nexa, 'Nexa Consultancy', 'thenexaconsultancy.com', 'n8n_community', org_id, now(), now(), '{"budget": 1500, "industry": "RevOps & Consulting"}'::jsonb, '{}'::jsonb),
        (comp_vance, 'Vance & Associates Legal', 'vancelegal.com', 'outbound_prospect', org_id, now(), now(), '{"budget": 2500, "industry": "Legal Services"}'::jsonb, '{}'::jsonb),
        (comp_apex, 'Apex MedSpa & Aesthetics', 'apexmedspa.com', 'outbound_prospect', org_id, now(), now(), '{"budget": 750, "industry": "Healthcare / MedSpa"}'::jsonb, '{}'::jsonb),
        (comp_swiss, 'Swiss Digital Ventures', 'swissdigital.ch', 'n8n_forum', org_id, now(), now(), '{"budget": 1500, "industry": "Digital Projects"}'::jsonb, '{}'::jsonb),
        (comp_indie, 'Indie SaaS Hub', 'indiesaas.co', 'discord_radar', org_id, now(), now(), '{"budget": 650, "industry": "E-commerce & SaaS"}'::jsonb, '{}'::jsonb)
    ON CONFLICT DO NOTHING;

    -- 3. Insert People (Qualified Leads)
    INSERT INTO people (id, first_name, last_name, full_name, email, title, company_id, organization_id, source, custom, raw, created_at, updated_at)
    VALUES
        (p_alex, 'Alex', 'Vance', 'Alex Vance', 'alex@flowpulse.io', 'CTO', comp_flowpulse, org_id, 'n8n_community', '{"matched_offering": "WhatsApp & Lead Intake n8n Agent", "deal_value": 1200}'::jsonb, '{}'::jsonb, now(), now()),
        (p_sarah, 'Sarah', 'K.', 'Sarah K.', 'sarah@aiautomationguild.com', 'Founder', comp_aiguild, org_id, 'discord_radar', '{"matched_offering": "Air-Gapped Private Local AI Hub", "deal_value": 2000}'::jsonb, '{}'::jsonb, now(), now()),
        (p_karan, 'Karan', 'Verma', 'Karan Verma', 'karan@thenexaconsultancy.com', 'Managing Director', comp_nexa, org_id, 'n8n_community', '{"matched_offering": "Dedicated n8n Developer Retainer", "deal_value": 1500}'::jsonb, '{}'::jsonb, now(), now()),
        (p_elena, 'Elena', 'Vance', 'Elena Vance', 'elena@vancelegal.com', 'Senior Partner', comp_vance, org_id, 'outbound_prospect', '{"matched_offering": "Air-Gapped Private Local AI Hub", "deal_value": 2500}'::jsonb, '{}'::jsonb, now(), now()),
        (p_david, 'David', 'Ross', 'David Ross', 'david.ross@apexmedspa.com', 'Clinic Director', comp_apex, org_id, 'outbound_prospect', '{"matched_offering": "WhatsApp Business Booking Agent", "deal_value": 750}'::jsonb, '{}'::jsonb, now(), now()),
        (p_luca, 'Luca', 'Bernardi', 'Luca Bernardi', 'luca@swissdigital.ch', 'Founder', comp_swiss, org_id, 'n8n_forum', '{"matched_offering": "Dedicated n8n Developer Retainer", "deal_value": 1500}'::jsonb, '{}'::jsonb, now(), now()),
        (p_marcus, 'Marcus', 'B.', 'Marcus B.', 'marcus@indiesaas.co', 'Founder', comp_indie, org_id, 'discord_radar', '{"matched_offering": "60 n8n Agents Complete Pack", "deal_value": 650}'::jsonb, '{}'::jsonb, now(), now())
    ON CONFLICT DO NOTHING;

    -- 4. Create the 4 n8n Outreach Campaigns with Sequences
    INSERT INTO outreach_campaigns (id, name, status, organization_id, sequence, created_at, updated_at)
    VALUES
        (c_whatsapp, 'WhatsApp Business n8n Booking Bot ($750 + $150/mo)', 'active', org_id,
        '[
            {"stepNumber": 1, "waitDays": 0, "subject": "24/7 appointment bookings for {{company}}?", "body": "Hi {{firstName}},\n\nI noticed front-desk teams at {{company}} spend 2-3 hours daily answering routine pricing questions and rebooking appointments.\n\nWe deploy a 24/7 autonomous WhatsApp Concierge on n8n that handles patient inquiries, checks calendar availability, and logs confirmed bookings into Google Sheets and your CRM in real time.\n\nWould you be open to a 2-minute video showing the bot booking a live slot?\n\nBest,\nMullai Nathan\nSenior Automation Architect"},
            {"stepNumber": 2, "waitDays": 3, "subject": "", "body": "Hi {{firstName}},\n\nFollowing up on my note. Most clinics lose 20-30% of high-intent bookings because leads message after closing hours.\n\nOur WhatsApp n8n workflow captures those appointments 24/7 with instant human escalation if needed.\n\nHappy to share a live test number you can message right now to test the booking flow.\n\nBest,\nMullai"}
        ]'::jsonb, now(), now()),

        (c_private_ai, 'Air-Gapped Private Local AI & n8n Hub ($2,500 + $350/mo)', 'active', org_id,
        '[
            {"stepNumber": 1, "waitDays": 0, "subject": "Private, air-gapped AI automation for {{company}}", "body": "Hi {{firstName}},\n\nPractices in regulated sectors cannot upload sensitive client case files or patient notes to public cloud LLMs.\n\nWe deploy private, self-hosted n8n automation servers running local GPU models (Ollama / Qwen) on dedicated hardware:\n- 0% cloud data leakage: Ingestion and RAG search stay 100% on-premises.\n- Instant semantic search across case PDFs and client files.\n- Turnkey setup in 7 business days ($2,500 implementation + $350/mo maintenance).\n\nAre you available for a brief 10-minute briefing on how local AI can safeguard {{company}}s data?\n\nSincerely,\nMullai Nathan"},
            {"stepNumber": 2, "waitDays": 4, "subject": "", "body": "Hi {{firstName}},\n\nQuick follow-up. I put together a one-page architecture summary of how our local n8n engine indexes internal documents without a single byte leaving your firewall.\n\nWould you like me to send that over?\n\nBest,\nMullai"}
        ]'::jsonb, now(), now()),

        (c_retainer, 'Dedicated n8n Automation Developer Retainer ($1,500/mo)', 'active', org_id,
        '[
            {"stepNumber": 1, "waitDays": 0, "subject": "Fractional senior n8n automation engineer for {{company}}", "body": "Hi {{firstName}},\n\nSaw that {{company}} is scaling operations and dealing with multi-system integrations across CRMs, Stripe, and webhooks.\n\nI offer a dedicated fractional n8n developer retainer (25-30 dedicated hours/week for $1,500/month):\n- Multi-step webhook engineering with automatic exponential backoff error retries.\n- Bi-directional sync between GoHighLevel, HubSpot, Slack, and PostgreSQL.\n- Priority 4-hour SLA on any production webhook failure.\n\nWould love to hop on a quick call or share my recent n8n production workflow JSONs.\n\nBest regards,\nMullai Nathan"},
            {"stepNumber": 2, "waitDays": 3, "subject": "", "body": "Hi {{firstName}},\n\nChecking back on this. Here is a link to our live hardware cockpit running 60 production n8n workflows: http://localhost:3850/sales\n\nLet me know if you would like to run a trial workflow this week.\n\nBest,\nMullai"}
        ]'::jsonb, now(), now()),

        (c_pack, 'Complete 60 n8n AI Agents Digital Bundle ($297)', 'active', org_id,
        '[
            {"stepNumber": 1, "waitDays": 0, "subject": "60 production n8n AI agents (instant download)", "body": "Hi {{firstName}},\n\nInstead of building automations from scratch for weeks, you can deploy our complete library of 60 production-tested n8n agents:\n- Customer support, sales outreach, CRM sync, and WhatsApp bots.\n- Full commercial license with complete JSON files and setup documentation.\n\nYou can preview the full catalog here: http://localhost:3850/sales\n\nInstant digital download is available today for $297 one-time.\n\nBest,\nMullai Nathan"}
        ]'::jsonb, now(), now())
    ON CONFLICT DO NOTHING;

    -- 5. Add Outreach Leads to Campaigns
    INSERT INTO outreach_leads (id, campaign_id, person_id, email, first_name, last_name, company, sequence_status, current_step, custom_fields, created_at, updated_at)
    VALUES
        (gen_random_uuid(), c_whatsapp, p_david, 'david.ross@apexmedspa.com', 'David', 'Ross', 'Apex MedSpa & Aesthetics', 'pending', 0, '{"offering": "WhatsApp Booking Bot", "deal": "$750"}'::jsonb, now(), now()),
        (gen_random_uuid(), c_whatsapp, p_alex, 'alex@flowpulse.io', 'Alex', 'Vance', 'FlowPulse', 'pending', 0, '{"offering": "Lead Intake & CRM Pipeline", "deal": "$1,200"}'::jsonb, now(), now()),
        (gen_random_uuid(), c_private_ai, p_sarah, 'sarah@aiautomationguild.com', 'Sarah', 'K.', 'AI Automation Guild', 'pending', 0, '{"offering": "Private Local AI Hub", "deal": "$2,000"}'::jsonb, now(), now()),
        (gen_random_uuid(), c_private_ai, p_elena, 'elena@vancelegal.com', 'Elena', 'Vance', 'Vance & Associates Legal', 'pending', 0, '{"offering": "Air-Gapped Local LLM", "deal": "$2,500"}'::jsonb, now(), now()),
        (gen_random_uuid(), c_retainer, p_karan, 'karan@thenexaconsultancy.com', 'Karan', 'Verma', 'Nexa Consultancy', 'pending', 0, '{"offering": "Dedicated n8n Retainer", "deal": "$1,500/mo"}'::jsonb, now(), now()),
        (gen_random_uuid(), c_retainer, p_luca, 'luca@swissdigital.ch', 'Luca', 'Bernardi', 'Swiss Digital Ventures', 'pending', 0, '{"offering": "Dedicated n8n Retainer", "deal": "$1,500/mo"}'::jsonb, now(), now()),
        (gen_random_uuid(), c_pack, p_marcus, 'marcus@indiesaas.co', 'Marcus', 'B.', 'Indie SaaS Hub', 'pending', 0, '{"offering": "60 n8n Agents Pack", "deal": "$297"}'::jsonb, now(), now())
    ON CONFLICT DO NOTHING;

    -- 6. Insert CRM Records
    INSERT INTO crm_records (id, person_id, pipeline_id, organization_id, workflow_state, active_channel, created_at, updated_at)
    VALUES
        (gen_random_uuid(), p_alex, pipeline_id, org_id, 'action_required', 'email', now(), now()),
        (gen_random_uuid(), p_sarah, pipeline_id, org_id, 'action_required', 'email', now(), now()),
        (gen_random_uuid(), p_karan, pipeline_id, org_id, 'waiting', 'email', now(), now()),
        (gen_random_uuid(), p_elena, pipeline_id, org_id, 'waiting', 'email', now(), now()),
        (gen_random_uuid(), p_david, pipeline_id, org_id, 'waiting', 'email', now(), now()),
        (gen_random_uuid(), p_luca, pipeline_id, org_id, 'action_required', 'email', now(), now()),
        (gen_random_uuid(), p_marcus, pipeline_id, org_id, 'waiting', 'email', now(), now())
    ON CONFLICT DO NOTHING;

END $$;
