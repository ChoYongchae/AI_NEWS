# Daily AI Paper Agent

An automated agent that collects, summarizes, and emails you the latest AI papers every morning.

## Features
- **Auto-Collection**: Fetches papers from ArXiv (filtered by topic) and Hugging Face Trending Papers.
- **LLM Summarization**: Uses OpenAI (or other providers) to generate "Morning News" style summaries.
- **Email Notification**: Sends a beautifully formatted HTML email digest.
- **Configurable**: Easy setup via `.env` and `config.yaml`.

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/junprocess/AI_NEWS
   cd AI_NEWS
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   Copy `.env.example` to `.env` and fill in your details:
   ```bash
   cp .env.example .env
   ```
   *Required: `LLM_API_KEY`*
   *Optional: Email settings (if you want the email feature)*

4. **Customize Topics**
   Edit `config.yaml` to change topics or agent personality.

5. **Run**
   ```bash
   python main.py
   ```

## Contributing
Feel free to open issues or PRs to add more collectors (e.g., specific conferences) or notifiers (Slack, Discord).
