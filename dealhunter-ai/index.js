import 'dotenv/config';
import { onRequest } from "firebase-functions/v2/https";
import express from 'express';
import cors from 'cors';
import { AIService } from './services/ai.js';
import { ScraperService } from './services/scraper.js';

const app = express();
app.use(cors({ origin: true }));
app.use(express.json());

// Store active chat sessions in memory
// Note: In a real serverless app, this should be moved to Firestore or Redis!
const chatSessions = new Map();

// Generate a random session ID
app.get('/api/session', (req, res) => {
  const sessionId = Math.random().toString(36).substring(7);
  chatSessions.set(sessionId, { messages: [] });
  res.json({ sessionId });
});

// AI Chat Endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { sessionId, message } = req.body;
    
    if (!sessionId || !message) {
      return res.status(400).json({ error: 'sessionId and message are required' });
    }

    let session = chatSessions.get(sessionId);
    if (!session) {
      session = { messages: [] };
      chatSessions.set(sessionId, session);
    }

    session.messages.push({ role: 'user', content: message });

    // Let the AI analyze the chat history to either ask clarifying questions or extract a refined search query
    const aiResponse = await AIService.analyzeIntent(session.messages);
    
    session.messages.push({ role: 'assistant', content: aiResponse.message });

    res.json({
      reply: aiResponse.message,
      isSearchReady: aiResponse.isSearchReady,
      searchQuery: aiResponse.searchQuery
    });

  } catch (error) {
    console.error('[API] Chat error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Scraper Endpoint
app.post('/api/search', async (req, res) => {
  try {
    const { query } = req.body;
    
    if (!query) {
      return res.status(400).json({ error: 'query is required' });
    }

    console.log(`[API] Triggering scraper for query: "${query}"`);
    const results = await ScraperService.scrapeTop10Sites(query);
    
    // Generate AI summary of the results
    const summary = await AIService.summarizeResults(results, query);

    res.json({
      success: true,
      results,
      summary
    });

  } catch (error) {
    console.error('[API] Search error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Export the Express app as a Firebase HTTP Cloud Function
// 2GB Memory and 300s timeout are required for Puppeteer.
export const api = onRequest({ memory: "2GiB", timeoutSeconds: 300 }, app);
