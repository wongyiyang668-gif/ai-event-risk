# AI Event Risk System

Enterprise AI Risk Scoring & Traceability System.

## Architecture

- **Backend**: FastAPI (Python)
- **Database**: SQLite + SQLAlchemy
- **Interface**: Discord Bot (ChatOps) / API Ingestion
- **AI Engine**: 
  - Deterministic Scoring
  - Semantic Risk Classification
  - RAG-based Similarity Search
  - LLM Summarization

## Getting Started

### Backend

1. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Run the API:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. Access API docs at `http://localhost:8000/docs`

## Features

- **Multi-channel Ingestion**: Telegram, Email, WhatsApp, Discord
- **Risk Analysis Pipeline**: Scoring -> Semantics -> Explanations -> RAG -> LLM
- **Agent Orchestration**: LangChain-based risk agent

## Discord ChatOps Integration

The system uses Discord as the primary UI layer for all user interactions.

### Setup

1. **Discord Bot**:
   - Create a bot in [Discord Developer Portal](https://discord.com/developers/applications).
   - Enable `Message Content Intent`.
   - Copy the `Bot Token`.
   - Setup a `Webhook` in a private channel for high-risk alerts.

2. **Environment Variables**:
   - `DISCORD_TOKEN`: Bot token from portal.
   - `DISCORD_WEBHOOK_URL`: Webhook URL for alerts.
   - `INGESTION_CHANNEL_ID`: (Optional) ID of a channel for automatic message ingestion.

3. **Run Discord Bot**:
   ```bash
   cd discord_bot
   pip install -r requirements.txt
   python main.py
   ```

### Slash Commands
- `/analyze [text]`: Instant AI risk analysis with Embed output.
- `/stats`: View system health, total events, and status.
- `/recent`: Fetch a list of recent event IDs and snippets.
- `/review [id] [note]`: Submit manual audit feedback directly to the DB.

### Proactive Alerts
The backend `NotificationService` automatically monitors all ingested events. If any event score exceeds the **0.6 (High Risk)** threshold, a detailed alert is pushed to the Discord Webhook in real-time, independent of the bot process.