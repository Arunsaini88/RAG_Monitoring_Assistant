# Installation Guide - Offline RAG System

Complete step-by-step installation instructions for the Offline RAG License Monitoring System.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Step 1: Install Ollama](#step-1-install-ollama)
3. [Step 2: Install Python](#step-2-install-python)
4. [Step 3: Install Node.js](#step-3-install-nodejs)
5. [Step 4: Setup Project](#step-4-setup-project)
6. [Step 5: Verify Installation](#step-5-verify-installation)
7. [Step 6: First Run](#step-6-first-run)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: 8 GB (16 GB recommended)
- **Storage**: 10 GB free space
- **CPU**: Modern multi-core processor (Intel i5/i7, AMD Ryzen 5/7, or Apple Silicon)
- **Internet**: Required for initial setup only

### Software Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Ollama (for local LLM)
- Git (optional, for version control)

---

## Step 1: Install Ollama

Ollama is required to run the local LLM (Llama 3.2:1b).

### Windows

1. **Download Ollama for Windows**
   - Visit: https://ollama.ai/download
   - Click "Download for Windows"
   - Run the installer: `OllamaSetup.exe`

2. **Verify Installation**
   ```cmd
   ollama --version
   ```
   Should show version like: `ollama version 0.x.x`

3. **Pull Llama 3.2:1b Model**
   ```cmd
   ollama pull llama3.2:1b
   ```
   This downloads ~1.3 GB. Wait for completion.

4. **Verify Model**
   ```cmd
   ollama list
   ```
   Should show `llama3.2:1b` in the list.

### macOS

1. **Download Ollama for macOS**
   - Visit: https://ollama.ai/download
   - Click "Download for macOS"
   - Open the `.dmg` file and drag Ollama to Applications

2. **Verify Installation**
   ```bash
   ollama --version
   ```

3. **Pull Llama 3.2:1b Model**
   ```bash
   ollama pull llama3.2:1b
   ```

4. **Verify Model**
   ```bash
   ollama list
   ```

### Linux

1. **Install Ollama**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Verify Installation**
   ```bash
   ollama --version
   ```

3. **Pull Llama 3.2:1b Model**
   ```bash
   ollama pull llama3.2:1b
   ```

4. **Verify Model**
   ```bash
   ollama list
   ```

---

## Step 2: Install Python

### Windows

1. **Download Python**
   - Visit: https://www.python.org/downloads/
   - Download Python 3.11 or 3.12 (recommended)
   - Run the installer

2. **IMPORTANT: During Installation**
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install pip"
   - Click "Install Now"

3. **Verify Installation**
   ```cmd
   python --version
   pip --version
   ```

4. **Upgrade pip (optional but recommended)**
   ```cmd
   python -m pip install --upgrade pip
   ```

### macOS

1. **Using Homebrew (Recommended)**
   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   # Install Python
   brew install python@3.11
   ```

2. **Verify Installation**
   ```bash
   python3 --version
   pip3 --version
   ```

### Linux (Ubuntu/Debian)

1. **Install Python**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3-pip python3-venv
   ```

2. **Verify Installation**
   ```bash
   python3 --version
   pip3 --version
   ```

---

## Step 3: Install Node.js

### Windows

1. **Download Node.js**
   - Visit: https://nodejs.org/
   - Download LTS version (e.g., 20.x.x)
   - Run the installer: `node-vxx.x.x-x64.msi`

2. **Verify Installation**
   ```cmd
   node --version
   npm --version
   ```

### macOS

1. **Using Homebrew**
   ```bash
   brew install node
   ```

2. **Or Download Installer**
   - Visit: https://nodejs.org/
   - Download macOS installer
   - Run the `.pkg` file

3. **Verify Installation**
   ```bash
   node --version
   npm --version
   ```

### Linux

1. **Using NodeSource Repository**
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

2. **Verify Installation**
   ```bash
   node --version
   npm --version
   ```

---

## Step 4: Setup Project

### 4.1 Navigate to Project Directory

```bash
cd d:\assignments\AI_Projects\freelance_RAG\First_RAG
```

### 4.2 Setup Python Virtual Environment (Recommended)

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### 4.3 Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- fastapi
- uvicorn[standard]
- sentence-transformers
- faiss-cpu
- requests
- numpy
- python-multipart

**Expected output:**
```
Successfully installed fastapi-0.x.x uvicorn-0.x.x ...
```

**Note:** First-time installation may take 2-5 minutes as it downloads sentence-transformers models.

### 4.4 Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

This installs:
- axios
- readline-sync

**Expected output:**
```
added 52 packages in 3s
```

### 4.5 Generate Sample Data (Optional)

If you don't have license data yet, generate sample data:

```bash
cd ..
python data.py
```

**Expected output:**
```
✅ Sample dataset with 10,000 records created: license_data_sample.json
```

Then copy the sample data to backend:
```bash
# Windows
copy license_data_sample.json backend\data.json

# macOS/Linux
cp license_data_sample.json backend/data.json
```

---

## Step 5: Verify Installation

### 5.1 Check Python Packages

```bash
cd backend
pip list
```

Verify these packages are installed:
- fastapi
- uvicorn
- sentence-transformers
- faiss-cpu
- numpy
- requests

### 5.2 Check Node.js Packages

```bash
cd ../frontend
npm list --depth=0
```

Verify these packages:
- axios
- readline-sync

### 5.3 Check Ollama Service

```bash
ollama serve
```

Should show:
```
Ollama is running
```

Keep this terminal open or press Ctrl+C and Ollama will run in background.

---

## Step 6: First Run

### Option 1: Using the Launcher (Windows Only)

Simply double-click `start_offline_rag.bat`

This will:
1. Start Ollama server
2. Start FastAPI backend (port 8000)
3. Start Node.js frontend CLI

### Option 2: Manual Start (All Platforms)

**Terminal 1 - Start Ollama:**
```bash
ollama serve
```

**Terminal 2 - Start Backend:**
```bash
cd backend
python main.py
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 3 - Start Frontend:**
```bash
cd frontend
node app.js
```

Expected output:
```
============================================================
  AI License Monitoring Assistant
============================================================

Commands:
  - Ask any question about license usage
  - 'health'  - Check system status
  - 'refresh' - Reload data from source
  - 'debug'   - Show detailed context (toggle)
  - 'clear'   - Clear conversation history
  - 'exit'    - Quit

Note: First query may take 2-3 minutes if building index.

🔄 Conversation mode enabled - I remember previous questions!

Ask question>
```

### 6.1 Test the System

1. **Check Health**
   ```
   Ask question> health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "indexed_records": 10000,
     "index_initialized": true,
     "embedding_model": "paraphrase-MiniLM-L3-v2",
     "ollama_endpoint": "http://127.0.0.1:11434"
   }
   ```

2. **Ask a Question**
   ```
   Ask question> which software has the highest usage?
   ```

   First query will take 2-3 minutes (building FAISS index). You'll see:
   ```
   🤔 Thinking... (AI is processing your question)
   ```

   Then get a response like:
   ```
   💬 AI Assistant: Based on the data, Autodesk has the highest usage with an average of 75% across all licenses.

   ⏱️  Response time: 9.2s | 📊 Used 4 records | 💭 2 msgs in history
   ```

3. **Test Conversation**
   ```
   Ask question> what about MATLAB?
   ```

   The AI remembers previous context!

---

## Troubleshooting

### Issue 1: "Python is not recognized"

**Windows:**
1. Reinstall Python with "Add to PATH" checked
2. Or manually add to PATH:
   - Search "Environment Variables"
   - Edit "Path" variable
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311`

**macOS/Linux:**
Use `python3` instead of `python`

### Issue 2: "ollama: command not found"

**Solution:**
- Restart terminal after installation
- Check Ollama is installed: Try running Ollama app manually

**Windows:**
- Check `C:\Users\YourName\AppData\Local\Programs\Ollama\ollama.exe` exists

**macOS:**
- Open Ollama from Applications folder first

### Issue 3: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
1. Activate virtual environment:
   ```bash
   # Windows
   .venv\Scripts\activate

   # macOS/Linux
   source .venv/bin/activate
   ```

2. Reinstall dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Issue 4: "ECONNREFUSED" when starting frontend

**Cause:** Backend not running

**Solution:**
1. Start backend first: `cd backend && python main.py`
2. Wait for "Uvicorn running on http://0.0.0.0:8000"
3. Then start frontend

### Issue 5: Slow First Query (>3 minutes)

**This is normal!** The system is:
1. Downloading embedding model (~90 MB) - first time only
2. Building FAISS index for 10,000 records (~1-2 minutes)
3. Caching the index for future use

Subsequent queries will be 8-12 seconds.

### Issue 6: "Port 8000 already in use"

**Solution:**

**Option 1 - Kill existing process:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

**Option 2 - Change port:**
Edit `backend/config.py`:
```python
PORT = 8001  # Change to different port
```

### Issue 7: Out of Memory During Installation

**Solution:**
1. Close other applications
2. Install packages one by one:
   ```bash
   pip install fastapi
   pip install uvicorn[standard]
   pip install sentence-transformers
   pip install faiss-cpu
   pip install requests numpy python-multipart
   ```

### Issue 8: SSL Certificate Error During pip install

**Solution:**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## Post-Installation

### Optional: Create Desktop Shortcut (Windows)

1. Right-click `start_offline_rag.bat`
2. Send to > Desktop (create shortcut)
3. Rename to "AI License Assistant"

### Optional: Set up as System Service (Linux)

Create systemd service for auto-start:

```bash
sudo nano /etc/systemd/system/rag-backend.service
```

```ini
[Unit]
Description=RAG Backend Service
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/First_RAG/backend
ExecStart=/path/to/.venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable rag-backend
sudo systemctl start rag-backend
```

---

## Next Steps

1. ✅ Installation complete!
2. 📖 Read [README.md](README.md) for usage guide
3. ⚡ Review [SPEED_OPTIMIZATIONS.md](SPEED_OPTIMIZATIONS.md) for performance tuning
4. 💬 Start asking questions about your license data!

---

## Getting Help

If you encounter issues not covered here:

1. Check backend logs in Terminal 2
2. Check Ollama logs: `ollama logs`
3. Verify all services are running:
   - Ollama: `http://localhost:11434`
   - Backend: `http://localhost:8000/health`
4. Review error messages carefully
5. Ensure all prerequisites are installed

---

## Quick Reference Card

### Start System (Windows)
```cmd
start_offline_rag.bat
```

### Start System (Manual)
```bash
# Terminal 1
ollama serve

# Terminal 2
cd backend && python main.py

# Terminal 3
cd frontend && node app.js
```

### Stop System
- Close all terminal windows
- Or press Ctrl+C in each terminal

### Update Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt --upgrade

# Frontend
cd frontend
npm update
```

### Rebuild Index
```bash
# Delete cached index files
rm backend/faiss_index.index
rm backend/metadata_store.json
rm backend/data_hash.txt

# Restart backend - will rebuild automatically
```

---

**Installation Time:** 15-30 minutes (including downloads)

**First Query Time:** 2-3 minutes (building index)

**Subsequent Queries:** 8-12 seconds

---

Happy querying! 🚀
