# Multi-Channel Outbound Sales & Campaign Pack (AgentSDR Ready)

This pack provides ready-to-launch multi-channel outreach sequences (Cold Email, LinkedIn InMail/Connection Notes, and WhatsApp follow-ups) calibrated to sell the top solutions identified from the projects directory.

Paired with the CSV lead list at [`/home/mullainathan/Documents/Coding/Projects/AgentSDR/outreach_leads_packaged.csv`](file:///home/mullainathan/Documents/Coding/Projects/AgentSDR/outreach_leads_packaged.csv).

---

##  How to Launch in AgentSDR

1. Open **[http://localhost:3000](http://localhost:3000)** (AgentSDR Workspace).
2. Go to **Tables** &rarr; Click **Import CSV** &rarr; Select `outreach_leads_packaged.csv`.
3. Map the fields:
   - `first_name` &rarr; First Name
   - `last_name` &rarr; Last Name
   - `email` &rarr; Email
   - `company_name` &rarr; Company Name
   - `target_offering` &rarr; Custom Variable `{{offering}}`
   - `custom_pain_point` &rarr; Custom Variable `{{pain_point}}`
4. Create a new Campaign under **Email Campaigns** or **LinkedIn Campaigns**, paste the corresponding sequence below, and set the daily sending window.

---

##  Sequence 1: WhatsApp Business Booking Agent ($750 Setup + $150/mo)

**Target:** Salons, Aesthetics Clinics, MedSpas, Dental Practices, Real Estate Agencies, Gyms.

### Step 1: Cold Email (Day 1)
**Subject:** 24/7 appointment bookings for {{company_name}}?

```text
Hi {{first_name}},

I noticed that {{company_name}} handles a high volume of client inquiries, but front-desk teams often spend 2-3 hours daily answering routine pricing questions and rebooking cancellations.

We deploy a 24/7 autonomous WhatsApp Concierge that integrates directly with your booking calendar and Google Sheets:
- Automatically qualifies incoming patient/client inquiries in under 2 seconds.
- Reserves real appointment slots directly inside WhatsApp without human friction.
- Notifies your staff instantly when an urgent consultation or human escalation is needed.

Typical setup is completely turnkey in 3 to 5 business days ($750 one-time + $150/mo).

Would you be open to a 2-minute video walkthrough showing how the bot handles bookings in real time?

Best regards,
Mullai Nathan
Senior Automation Architect | Discord: cybermunna4
```

### Step 2: LinkedIn Connection Request Note (Day 2)
```text
Hi {{first_name}}, love the work you're doing at {{company_name}}. We built an autonomous WhatsApp booking assistant for clinics & salons that captures after-hours appointments on autopilot. Would love to connect and share notes!
```

### Step 3: Follow-Up Email (Day 4)
**Subject:** Re: 24/7 appointment bookings for {{company_name}}?

```text
Hi {{first_name}},

Following up on my note from Tuesday. Most clinics lose 20-30% of high-intent bookings simply because potential clients message after closing hours and bounce before morning.

Our WhatsApp agent captures those slots 24/7. 

Happy to send over a sample workflow JSON or test number you can message right now to test the booking flow.

Best,
Mullai Nathan
```

---

##  Sequence 2: Air-Gapped Private Local AI & Automation Hub ($2,500 Setup + $350/mo)

**Target:** Law Firms, Wealth Management, Private Healthcare Practices.

### Step 1: Cold Email (Day 1)
**Subject:** Private, air-gapped AI infrastructure for {{company_name}}

```text
Hi {{first_name}},

Law firms and healthcare practices face a critical dilemma: the productivity gains of AI document search and automation are undeniable, but uploading sensitive client files or patient notes to third-party public cloud LLMs creates unacceptable compliance and confidentiality exposure.

We design and deploy 100% air-gapped, on-premises AI automation servers using self-hosted n8n and dedicated local GPU models:
- 0% cloud data leakage: Ingestion and vector search run entirely on your private hardware/VPS.
- Instant RAG semantic search across internal case PDFs, briefs, and internal SOPs.
- Automatic triage, summarization, and task routing directly into your database.

We handle the full turnkey installation ($2,500 implementation + $350/mo maintenance).

Are you available for a brief 10-minute briefing on how local AI can safeguard {{company_name}}'s data?

Sincerely,
Mullai Nathan
Senior AI & Automation Architect
```

---

##  Sequence 3: Lumina — White-Label Private Social Media Platform ($5,000 / $99/mo)

**Target:** Private Creator Communities, Alumni Networks, High-End Clubs, DAOs.

### Step 1: Cold Email (Day 1)
**Subject:** Own your community platform (goodbye Circle/Discord fees)

```text
Hi {{first_name}},

If {{company_name}} is currently paying hundreds of dollars every month to platforms like Circle, Mighty Networks, or Discord, you're renting your audience and locked into their branding.

We built Lumina — a production-grade, cinematic private social networking platform designed for exclusive communities:
- Full-screen 24h stories (with interactive polls, Q&A, and emoji reactions).
- End-to-end real-time chat with GIFs, media attachments, and read receipts.
- Complete admin suite with shadow-banning, member moderation, and audit logs.
- Installable PWA for iOS & Android with zero app store fees.

You can inspect the live working demo right here:
https://social-platform-mvp-demo.web.app

We offer full source code ownership / turnkey deployment ($5,000 one-time buyout) or hosted white-label ($99/mo).

Would you like access to an admin test account to test the moderation and story feed?

Best regards,
Mullai Nathan
Founder, Brix Softworks
```

---

##  Sequence 4: Camera CV — Commercial AI Video Surveillance ($1,500 + $150/mo)

**Target:** Retail Stores, Warehouses, Logistics Hubs, Schools.

### Step 1: Cold Email (Day 1)
**Subject:** Upgrading {{company_name}}'s cameras with AI intrusion & foot-traffic analytics

```text
Hi {{first_name}},

Most standard IP camera systems are purely passive: they record footage that is only reviewed after a theft or incident has already happened.

Camera CV transforms your existing IP/ONVIF cameras into an active intelligence system:
- YOLOv8 real-time object tracking (distinguishes people, vehicles, and assets).
- Polygon intrusion alarms: triggers instant alerts to Telegram/Discord when unauthorized areas are entered.
- Tripwire counting & heatmaps: tracks customer foot traffic and peak congestion zones.
- Smart auto-recording: records high-frame clips only when motion/activity occurs.

We deploy this as a plug-and-play local NVR server on your existing network ($1,500 setup + $150/mo).

Could I show you a 60-second clip demonstrating the intrusion detection and heatmap analytics in action?

Best regards,
Mullai Nathan
```
