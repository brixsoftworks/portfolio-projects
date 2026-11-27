import { GoogleGenerativeAI } from '@google/generative-ai';
import dotenv from 'dotenv';
dotenv.config();

const apiKey = process.env.GEMINI_API_KEY;
let genAI = null;
if (apiKey) {
  genAI = new GoogleGenerativeAI(apiKey);
  console.log('[AI] Gemini API key loaded');
} else {
  console.warn('[AI] GEMINI_API_KEY is not set. AI features will be disabled.');
}

const MODEL_NAME = 'gemini-2.0-flash';

const SYSTEM_PROMPT = `You are "DealHunter AI", a friendly, knowledgeable shopping assistant for Indian e-commerce.

CORE RULES:
1. You are a CHATBOT first, shopping assistant second. Answer ANY question the user asks - shopping, general knowledge, jokes, advice, etc.
2. When the user says hello/greetings, greet them warmly.
3. When the user asks non-shopping questions (math, science, history, jokes, advice, definitions, etc.), answer them helpfully and briefly. Then optionally mention you can also help with shopping.
4. When the user mentions a product they want to buy, gather details through conversation:
   - Category, type, gender, budget, brand, size
5. Only set isSearchReady=true when you have ENOUGH details to find good products (at least category + some specificity).
6. NEVER set isSearchReady=true for greetings, chitchat, jokes, general knowledge, or vague inputs.
7. When isSearchReady=true, generate an optimized searchQuery string.
8. Keep responses concise and friendly.

OUTPUT - respond with ONLY valid JSON:
{"isSearchReady": boolean, "message": "your response", "searchQuery": "search terms" | null}

searchQuery MUST be null when isSearchReady is false.`;

export class AIService {
  static async analyzeIntent(messages) {
    if (!genAI) {
      return this.fallbackIntent(messages);
    }

    console.log('[AI] Calling Gemini for intent analysis,', messages.length, 'messages');

    const model = genAI.getGenerativeModel({ model: MODEL_NAME });

    const conversationHistory = messages.map(m => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content }]
    }));

    const lastMessage = conversationHistory.pop();

    try {
      const chat = model.startChat({
        systemInstruction: { role: 'system', parts: [{ text: SYSTEM_PROMPT }] },
        history: conversationHistory,
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 300,
        }
      });

      const result = await chat.sendMessage(lastMessage.parts[0].text);
      const response = await result.response;
      let text = response.text().trim();
      text = text.replace(/```json/gi, '').replace(/```/gi, '').trim();
      const parsed = JSON.parse(text);
      if (typeof parsed.isSearchReady !== 'boolean') throw new Error('Invalid response shape');
      if (parsed.isSearchReady && !parsed.searchQuery) {
        parsed.searchQuery = messages[messages.length - 1].content;
      }
      return parsed;
    } catch (err) {
      console.error("[AI] Gemini API error:", err.message);
      return this.fallbackIntent(messages);
    }
  }

  static fallbackIntent(messages) {
    const lastMsg = messages[messages.length - 1].content.toLowerCase().trim();
    const originalMsg = messages[messages.length - 1].content.trim();
    const messageCount = messages.length;

    const greetings = /^(hi|hello|hey|yo|sup|hola|namaste|good\s*(morning|afternoon|evening)|howdy|what'?s up|how are you|how'?s it going)/i;
    const thanks = /^(thank|thanks|thx|ty|appreciate|cheers|ok|okay)/i;

    if (greetings.test(lastMsg)) {
      if (messageCount <= 1) {
        return {
          isSearchReady: false,
          message: "Hey there! Welcome to DealHunter AI! I'm your personal shopping assistant.\n\nI can help you find the best deals across Amazon, Flipkart, Myntra, Ajio and more. I can also answer general questions!\n\nWhat are you looking for today?",
          searchQuery: null
        };
      }
      return {
        isSearchReady: false,
        message: "Hey! I'm here to help. What would you like to know or buy?",
        searchQuery: null
      };
    }

    if (thanks.test(lastMsg)) {
      return {
        isSearchReady: false,
        message: "You're welcome! Let me know if you need anything else.",
        searchQuery: null
      };
    }

    const generalKnowledge = /^(what is|what are|what can|what do|what does|what was|what were|who is|who are|who was|who were|where is|where are|when is|when was|how do|how does|how can|how to|how is|how was|how are|why do|why does|why is|why are|why was|which is|which are|waht|wat is|wat are|wat can|hu is|hwta|whast|hat is|define|explain|tell me|meaning of|difference between|can you|could you|would you|is it true|do you know|what do you think|how many|how much|how far|how old|what time|what day|what month|what year|calculate|convert|translate|spell|write|list|name|give me|send me|show me|help me with|solve|answer|describe|compare|recommend|suggest|should I|what does)/i;
    const mathPattern = /\b(calculate|solve|what is|compute)\b.*\d|[\d+\-*/().]+\s*[=]/;
    const jokePattern = /\b(joke|funny|laugh|hilarious|make me laugh|tell me a)\b/i;
    const factPattern = /\b(did you know|fun fact|interesting fact|tell me a fact|random fact|trivia)\b/i;
    const howAreYou = /\b(how are you|how'?s it going|how have you been|what'?s up|what's new|how do you do|how r u)\b/i;
    const whoAreYou = /\b(who are you|what are you|your name|what can you do|your capabilities|what do you do|what can i do with you|what can i do here|how do you work|how can you help|what is this|tell me about yourself|what should i ask|waht can i do|what should i do|what is your purpose|why are you here)\b/i;

    if (generalKnowledge.test(lastMsg) || mathPattern.test(lastMsg) || jokePattern.test(lastMsg) || factPattern.test(lastMsg) || howAreYou.test(lastMsg) || whoAreYou.test(lastMsg)) {
      let answer;
      if (mathPattern.test(lastMsg)) {
        const nums = lastMsg.match(/[\d.]+/g);
        if (nums && nums.length >= 2) {
          const a = parseFloat(nums[0]), b = parseFloat(nums[1]);
          if (lastMsg.includes('+')) answer = `The answer is ${a + b}.`;
          else if (lastMsg.includes('-') || lastMsg.includes('minus')) answer = `The answer is ${a - b}.`;
          else if (lastMsg.includes('*') || lastMsg.includes('times') || lastMsg.includes('x')) answer = `The answer is ${a * b}.`;
          else if (lastMsg.includes('/') || lastMsg.includes('divided')) answer = b !== 0 ? `The answer is ${(a / b).toFixed(2)}.` : "Cannot divide by zero!";
          else answer = `The answer is ${a + b}.`;
        } else if (lastMsg.includes('2+2') || lastMsg.includes('2 + 2')) {
          answer = "The answer is 4.";
        } else {
          answer = "I'd be happy to help with math! Please provide the numbers and operation (e.g., 'calculate 15 * 3').";
        }
      } else if (jokePattern.test(lastMsg)) {
        const jokes = [
          "Why don't scientists trust atoms? Because they make up everything!",
          "Why did the scarecrow win an award? He was outstanding in his field!",
          "What do you call a fake noodle? An impasta!",
          "Why don't eggs tell jokes? They'd crack each other up!",
          "I told my wife she was drawing her eyebrows too high. She looked surprised."
        ];
        answer = jokes[Math.floor(Math.random() * jokes.length)];
      } else if (factPattern.test(lastMsg)) {
        const facts = [
          "Honey never spoils. Archaeologists found 3,000-year-old honey in Egyptian tombs that was still edible!",
          "Octopuses have three hearts and blue blood.",
          "A group of flamingos is called a 'flamboyance'.",
          "Bananas are berries, but strawberries aren't!",
          "The Eiffel Tower can be 15 cm taller during summer due to thermal expansion."
        ];
        answer = facts[Math.floor(Math.random() * facts.length)];
      } else if (howAreYou.test(lastMsg)) {
        answer = "I'm doing great, thanks for asking! I'm ready to help you find amazing deals or answer any questions you have. What's on your mind?";
      } else if (whoAreYou.test(lastMsg)) {
        answer = "I'm DealHunter AI! I can help you find the best deals across Indian e-commerce sites like Amazon, Flipkart, Myntra, and Ajio. I can also answer general questions, tell jokes, and help with math. Just ask me anything!";
      } else {
        answer = `That's an interesting question! Here's what I know:\n\nWhile I'm primarily a shopping assistant, I can try to help with general questions too. For the most accurate answer, I'd recommend checking a reliable source.\n\nIs there anything shopping-related I can help you find today?`;
      }
      return {
        isSearchReady: false,
        message: answer,
        searchQuery: null
      };
    }

    const veryVague = /^(shoes|laptop|phone|shirt|dress|watch|bag|headphones|earphones|clothes|clothing|fashion|electronics|accessories|sneakers|jeans|tshirt|t-shirt|top|jean|shorts|jacket|hoodie|kurta|saree|boot|sandal|slipper|speaker|camera|tablet|monitor|keyboard|mouse|tv)$/i;
    if (veryVague.test(lastMsg)) {
      return {
        isSearchReady: false,
        message: `Great choice! Let me help you find the perfect ${lastMsg}. Can you tell me more?\n\n- What type? (e.g., running shoes, formal shoes, gaming laptop)\n- For men, women, or kids?\n- Budget range?\n- Any brand preference?`,
        searchQuery: null
      };
    }

    const isShoppingQuery = this.detectShoppingIntent(lastMsg);
    if (isShoppingQuery.isProduct) {
      if (isShoppingQuery.score >= 2) {
        const searchQuery = this.buildSearchQuery(lastMsg);
        return {
          isSearchReady: true,
          message: `Great! Let me search for the best ${searchQuery} deals across top stores.`,
          searchQuery
        };
      }

      let missing = [];
      if (!isShoppingQuery.hasGender) missing.push("gender (men's/women's/kids)");
      if (!isShoppingQuery.hasType) missing.push("specific style or type");
      if (!isShoppingQuery.hasPrice) missing.push("budget");

      if (missing.length > 0) {
        return {
          isSearchReady: false,
          message: `I see you're looking for ${originalMsg}! Could you tell me a bit more?\n- ${missing.join("\n- ")}`,
          searchQuery: null
        };
      }

      const searchQuery = this.buildSearchQuery(lastMsg);
      return {
        isSearchReady: true,
        message: `Let me search for the best ${searchQuery} deals!`,
        searchQuery
      };
    }

    const nonShoppingPattern = /\b(what|who|where|when|why|how|meaning|define|explain|tell|joke|funny|think|feel|opinion|thoughts|advice|suggest|recommend|help|can you|could you|would you|is it|are they|do you|does it|have you|has it|will it|should i|should we|did you)\b/i;
    const hasQuestionMark = lastMsg.includes('?');
    const isNonShopping = (hasQuestionMark || nonShoppingPattern.test(lastMsg)) && !this.detectShoppingIntent(lastMsg).isProduct;

    if (isNonShopping) {
      return {
        isSearchReady: false,
        message: `That's an interesting question! While I'm a shopping assistant specialized in finding deals across Indian e-commerce sites, I'll do my best to help.\n\nFor more detailed information, I'd suggest checking a reliable source. In the meantime, feel free to ask me about products you'd like to buy — I can search Amazon, Flipkart, Myntra, and more for the best prices!`,
        searchQuery: null
      };
    }

    const searchQuery = this.buildSearchQuery(lastMsg);
    return {
      isSearchReady: true,
      message: `Let me search for the best deals on "${searchQuery}" across top stores!`,
      searchQuery
    };
  }

  static detectShoppingIntent(msg) {
    const productKeywords = /(shirt|tshirt|t-shirt|shoe|sneaker|running|formal|casual|laptop|phone|headphone|earphone|watch|bag|dress|jean|jacket|hoodie|shorts|top|kurta|saree|boot|sandal|slipper|sunglasses|cap|wallet|belt|speaker|camera|tablet|monitor|keyboard|mouse|charger|cable|case|cover|gpu|cpu|ram|ssd|fan|cooler|fridge|microwave|oven|tv|led|headset|printer|projector)/i;
    const hasProduct = productKeywords.test(msg);
    const hasGender = /\b(men|women|men's|women's|mens|womens|boy|girl|kids|unisex|male|female)\b/i.test(msg);
    const hasSize = /\b(xs|s|m|l|xl|xxl|\d+(\s*(inch|in|cm|mm|gb|tb|mb|ml|l))?|size\s*\d+|petite|plus|big|small|large|medium)\b/i.test(msg);
    const hasPrice = /(\u20b9|rs\.?|under|below|budget|price|less than|around|approx)\s*\d/i.test(msg);
    const hasBrand = /\b(nike|adidas|puma|reebok|asics|new balance|samsung|apple|oneplus|xiaomi|redmi|realme|boat|jbl|sony|lg|hp|dell|lenovo|asus|acer|msi|macbook|iphone|galaxy|pixel)\b/i.test(msg);
    const hasType = /\b(running|formal|casual|sports|athletic|gaming|wireless|bluetooth|noise.?cancelling|oversized|slim|fit|loose|straight|skinny|wide|narrow|lightweight|heavy|premium|budget|cheap|best|top|popular|trending|new|latest)\b/i.test(msg);
    const hasBuy = /\b(buy|purchase|order|get|shop|find|search|looking for|want|need)\b/i.test(msg);

    let score = 0;
    if (hasProduct) score++;
    if (hasGender) score++;
    if (hasSize || hasType) score++;
    if (hasPrice) score++;
    if (hasBrand) score++;
    if (hasBuy) score++;

    return {
      isProduct: hasProduct,
      score,
      hasGender,
      hasType: hasSize || hasType,
      hasPrice,
      hasBrand,
    };
  }

  static buildSearchQuery(msg) {
    let q = msg.toLowerCase();
    q = q.replace(/\b(i want|i'm looking for|i need|buy me|get me|find me|search for|show me|looking for|want to buy|please get|can you find)\b/gi, '');
    q = q.replace(/\b(a|an|the|some|any|good|best|nice|great|cool|new|cheap|affordable)\b/gi, '');
    q = q.replace(/\b(for|of|in|at|with|from|and|or|but)\b/gi, ' ');
    q = q.replace(/\b(mens|men's|man's|male)\b/gi, 'men');
    q = q.replace(/\b(womens|women's|womans|female)\b/gi, 'women');
    q = q.replace(/\b(kids|child|children|boy|girl|boys|girls)\b/gi, 'kids');
    q = q.replace(/\s+/g, ' ').trim();
    if (q.length < 3) q = msg.replace(/[^\w\s]/g, '').trim();
    return q;
  }

  static async summarizeResults(results, query) {
    if (!results || results.length === 0) return "I couldn't find any compelling deals right now.";

    if (!genAI) {
      return this.fallbackSummary(results, query);
    }

    const model = genAI.getGenerativeModel({ model: MODEL_NAME });
    const productList = results.slice(0, 5).map(p => `${p.name} - ₹${p.price} on ${p.retailer}`).join('\n');

    try {
      const result = await model.generateContent(`You are DealHunter AI. Summarize these search results for "${query}" in 1-2 sentences. Be concise and enthusiastic:\n\n${productList}`);
      const response = await result.response;
      return response.text().trim();
    } catch (err) {
      console.error("[AI] Summary error:", err.message);
      return this.fallbackSummary(results, query);
    }
  }

  static fallbackSummary(results, query) {
    const retailers = [...new Set(results.map(r => r.retailer))];
    const prices = results.filter(r => r.price > 0).map(r => r.price);

    if (prices.length === 0) {
      return `Found ${results.length} products for "${query}" across ${retailers.join(', ')}. Click on any product to view details and buy.`;
    }

    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const cheapest = results.find(r => r.price === minPrice);

    let summary = `Found ${results.length} products for "${query}" across ${retailers.join(', ')}.`;
    if (cheapest) {
      summary += ` Best deal: ${cheapest.name.substring(0, 40)} at ₹${minPrice.toLocaleString()} on ${cheapest.retailer}.`;
    }
    summary += ` Prices range from ₹${minPrice.toLocaleString()} to ₹${maxPrice.toLocaleString()}.`;
    return summary;
  }
}
