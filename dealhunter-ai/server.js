import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { AIService } from './services/ai.js';
import { ScraperService } from './services/scraper.js';

const app = express();
app.use(cors({ origin: true }));
app.use(express.json());

const PORT = process.env.PORT || 3001;

// Bounded in-memory sessions: this server keeps state per chat session, which
// is fine for a single demo instance but will not scale horizontally.
// Sessions evicted after 30 minutes of inactivity or when the map is full
// (oldest first). Each session also caps its transcript length.
const SESSION_TTL_MS = 30 * 60 * 1000;
const MAX_SESSIONS = 500;
const MAX_MESSAGES_PER_SESSION = 40;
const chatSessions = new Map();

function sweepExpiredSessions() {
  const now = Date.now();
  for (const [id, s] of chatSessions) {
    if (now - s.lastSeen > SESSION_TTL_MS) chatSessions.delete(id);
  }
  while (chatSessions.size >= MAX_SESSIONS) {
    const oldest = chatSessions.keys().next().value; // insertion order = oldest
    chatSessions.delete(oldest);
  }
}
setInterval(sweepExpiredSessions, 5 * 60 * 1000).unref();

app.get('/api/session', (req, res) => {
  sweepExpiredSessions();
  const sessionId = Math.random().toString(36).substring(7);
  chatSessions.set(sessionId, { messages: [], lastSeen: Date.now() });
  console.log(`[Session] Created: ${sessionId} (active: ${chatSessions.size})`);
  res.json({ sessionId });
});

app.post('/api/chat', async (req, res) => {
  try {
    const { sessionId, message } = req.body;
    if (!sessionId || !message) {
      return res.status(400).json({ error: 'sessionId and message are required' });
    }

    let session = chatSessions.get(sessionId);
    if (!session) {
      session = { messages: [], lastSeen: Date.now() };
      chatSessions.set(sessionId, session);
    }
    session.lastSeen = Date.now();

    session.messages.push({ role: 'user', content: message });
    // Keep transcripts bounded — only the recent window matters for intent.
    if (session.messages.length > MAX_MESSAGES_PER_SESSION) {
      session.messages.splice(0, session.messages.length - MAX_MESSAGES_PER_SESSION);
    }

    const aiResponse = await AIService.analyzeIntent(session.messages);

    session.messages.push({ role: 'assistant', content: aiResponse.message });

    console.log(`[Chat] ${sessionId}: isSearchReady=${aiResponse.isSearchReady}`);

    res.json({
      reply: aiResponse.message,
      isSearchReady: aiResponse.isSearchReady,
      searchQuery: aiResponse.searchQuery
    });
  } catch (error) {
    console.error('[API] Chat error:', error.message);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

app.post('/api/search', async (req, res) => {
  try {
    const { query } = req.body;
    if (!query) {
      return res.status(400).json({ error: 'query is required' });
    }

    console.log(`[Search] Scraping for: "${query}"`);
    const results = await ScraperService.scrapeTop10Sites(query);

    const summary = await AIService.summarizeResults(results, query);

    console.log(`[Search] Returning ${results.length} results`);
    res.json({ success: true, results, summary });
  } catch (error) {
    console.error('[API] Search error:', error.message);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`[Server] DealHunter AI running on port ${PORT}`);
  console.log('Gemini API Key:', process.env.GEMINI_API_KEY ? 'SET' : 'NOT SET');
  console.log(`[Server] Chromium: ${process.env.PUPPETEER_EXECUTABLE_PATH || 'not set'}`);
});
