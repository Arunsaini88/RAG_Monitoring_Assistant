// frontend/app.js
import axios from "axios";
import readlineSync from "readline-sync";

const BASE = "http://localhost:8000";

// Create axios instance with longer timeout for first query (index building)
const api = axios.create({
  baseURL: BASE,
  timeout: 300000, // 5 minutes timeout for index building
  headers: {
    'Content-Type': 'application/json'
  }
});

console.log("=".repeat(60));
console.log("  AI License Monitoring Assistant");
console.log("=".repeat(60));
console.log("\nCommands:");
console.log("  - Ask any question about license usage");
console.log("  - 'health'  - Check system status");
console.log("  - 'refresh' - Reload data from source");
console.log("  - 'debug'   - Show detailed context (toggle)");
console.log("  - 'clear'   - Clear conversation history");
console.log("  - 'exit'    - Quit");
console.log("\nNote: First query may take 2-3 minutes if building index.\n");
console.log("🔄 Conversation mode enabled - I remember previous questions!\n");

let debugMode = false;
const sessionId = `session_${Date.now()}`; // Unique session ID for this conversation

(async function loop(){
  while(true){
    const q = readlineSync.question("\nAsk question> ");
    if(!q) continue;
    if(q.toLowerCase() === "exit") break;
    if(q.toLowerCase() === "refresh"){
      try {
        console.log("Refreshing data from source...");
        const startTime = Date.now();
        const res = await api.post('/refresh');
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

        console.log(`\n--- Refresh Complete (took ${elapsed}s) ---`);
        console.log(`Indexed records: ${res.data.indexed_records}`);
        console.log(`Data changed: ${res.data.data_changed ? 'Yes (rebuilt index)' : 'No (used cache)'}`);
        console.log(`Message: ${res.data.message}`);
      } catch (e) {
        console.error("Refresh error:", e.message);
      }
      continue;
    }
    if(q.toLowerCase() === "health"){
      try {
        const res = await api.get('/health');
        console.log("\n--- System Health ---");
        console.log(JSON.stringify(res.data, null, 2));
      } catch (e) {
        console.error("Health check error:", e.message);
      }
      continue;
    }
    if(q.toLowerCase() === "debug"){
      debugMode = !debugMode;
      console.log(`\n🔧 Debug mode: ${debugMode ? 'ON' : 'OFF'}`);
      console.log(debugMode ? "Will show detailed context data" : "Will show only AI responses");
      continue;
    }
    if(q.toLowerCase() === "clear"){
      try {
        console.log("Clearing conversation history...");
        const res = await api.post('/clear_history', { session_id: sessionId });
        console.log(`\n✅ ${res.data.message}`);
        console.log("Starting fresh conversation!");
      } catch (e) {
        console.error("Clear error:", e.message);
      }
      continue;
    }
    try {
      console.log("🤔 Thinking... (AI is processing your question)");
      const startTime = Date.now();
      const res = await api.post('/query', {
        query: q,
        session_id: sessionId
      });
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

      console.log(`\n💬 AI Assistant: ${res.data.answer}`);

      if (debugMode) {
        console.log(`\n🔍 Debug Info (${elapsed}s, ${res.data.context_count} records, ${res.data.conversation_length} messages in history):`);
        console.dir(res.data.top_context, { depth: 2 });
      } else {
        console.log(`\n⏱️  Response time: ${elapsed}s | 📊 Used ${res.data.context_count} records | 💭 ${res.data.conversation_length} msgs in history`);
      }
    } catch (e) {
      if (e.code === 'ECONNABORTED') {
        console.error("\n❌ Request timeout! The server is still processing (building index).");
        console.error("This happens on first query. Please wait and try again in 1-2 minutes.");
        console.error("Tip: Check server logs to see indexing progress.");
      } else if (e.code === 'ECONNRESET') {
        console.error("\n⚠️  Connection was reset. Retrying...");
        console.error("This can happen when Ollama is busy. Please try your question again.");
      } else if (e.response) {
        console.error("\n❌ Query error:", e.response.data);
      } else if (e.message) {
        console.error("\n❌ Connection error:", e.message);
        console.error("💡 Tip: Make sure the backend server and Ollama are running.");
      } else {
        console.error("\n❌ Unknown error occurred");
      }
    }
  }
  console.log("Goodbye!");
  process.exit(0);
})();
