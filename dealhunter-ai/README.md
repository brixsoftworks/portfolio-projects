# DealHunter AI: Real-Time Parallel E-Commerce Intelligence Backend

**Lead Systems Architect:** Mullainathan (`mullainathan95@gmail.com`)  
**Organization:** Brix Softworks  
**Role:** Principal Systems Architect & Senior Software Engineer  
**Stack:** Node 20 (Express 5 ESM), React 19, Google Gemini 1.5/2.0 API, Docker  
**Repository Status:** Production / Fully Functional  

---

## Executive Summary

DealHunter AI is a high-concurrency e-commerce deal extraction and semantic search engine designed for real-time price intelligence across multi-vendor retail platforms (Amazon, Flipkart, Myntra, Ajio, TataCliq, Nykaa).

The platform coordinates an asynchronous query pipeline: natural language intent extraction via Google Gemini converts user constraints (budget, category, brand, attributes) into structured query vectors, which are fanned out in parallel across retail endpoints using `Promise.allSettled`. Failed or throttled retailer scrapers degrade gracefully, allowing the system to aggregate, normalize, and summarize the best available offers without blocking the client response.

All session states are strictly bounded in memory with 30-minute Time-To-Live (TTL) eviction, ensuring predictable memory footprints during traffic surges.

---

## System Architecture

```text
  [ Client Application ] (React 19 + Vite, Vercel Edge)
             │
             │  POST /api/chat · POST /api/search
             ▼
  [ Backend Gateway ] (Express 5 ESM, Node 20)
             │
             ├── [ Intent Extraction Pipeline ]
             │      - Google Gemini LLM API (Structured Intent Extraction)
             │      - Fast Regex fallback parser for zero-key offline execution
             │
             ├── [ Parallel Extraction Engine ]
             │      - High-concurrency fan-out via Promise.allSettled
             │      - Per-retailer User-Agent rotation (Desktop, Mobile, Googlebot)
             │      - Exponential backoff retry logic and socket timeout guards
             │      - Graceful degradation: individual scraper failure does not fail request
             │
             └── [ Session & Memory Management ]
                    - Bounded in-memory store (30-minute TTL, 500-session capacity)
                    - 40-message sliding transcript window
```

---

## Technical Specifications

- **Backend Runtime:** Node.js 20 LTS, Express 5.0 (ECMAScript Modules).
- **Frontend Architecture:** React 19, Vite, Tailwind CSS.
- **AI Intent Pipeline:** Google Gemini Generative AI SDK with structured JSON output parsing.
- **Concurrency Pattern:** Asynchronous non-blocking fan-out (`Promise.allSettled`) isolating individual vendor latency spikes.
- **Resilience:** Automatic fallback regex parsing engine when upstream API keys are absent or rate-limited.
- **Containerization:** Production multi-stage `Dockerfile`.

---

## Installation & Execution

### 1. Backend Server Setup

```bash
cd dealhunter-ai

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Launch API service (:3001)
npm start
```

### 2. Frontend Web Interface

```bash
cd frontend
npm install
npm run dev
```

### 3. Containerized Deployment

```bash
docker build -t dealhunter-ai:latest .
docker run -p 3001:3001 dealhunter-ai:latest
```

---

## Authorship & Intellectual Property

- **Lead Systems Architect:** Mullainathan
- **Email:** mullainathan95@gmail.com
- **Organization:** Brix Softworks
- **License:** Proprietary - All rights reserved by Mullainathan
