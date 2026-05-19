# lifeVoice 🎮

A roleplay AI chatbot with RAG (Retrieval-Augmented Generation) and Agentic AI architecture, built with Streamlit.

## Features

### 🎭 Multi-Persona Chat
- **Professional** - Emotionally intelligent professional roleplay
- **Family** - Warm, familiar family member conversations
- **Friend** - 5 distinct friend personalities (Optimist, Pessimist, Youngstunna, Jejemon, Brainrot)
- **You** - Chat with your past or future self
- **Random** - Meet unpredictable realistic strangers

### 🤖 Advanced AI Architecture
- **RAG (Retrieval-Augmented Generation)** - FAISS vector database with persona-specific knowledge
- **Agentic AI** - Custom reasoning loop with 3 tools:
  - Web Search (DuckDuckGo)
  - Current Date/Time
  - Calculator
- **Prompt Defenses** - Protection against jailbreak attempts

### 🎨 Pixel-Art UI
- Streamlit-based interface with nostalgic pixel-art aesthetic
- Custom Stardew Valley font
- Personalized avatar selection
- Warm, cozy color scheme

## Installation

### Prerequisites
- Python 3.9+
- Git

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd lifeVoice
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

5. Build the vector index (if needed):
```bash
python build_index.py
```

## Usage

### Run the Application
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501` (or whatever port Streamlit uses).

### Onboarding Flow
1. Enter your name, age, and gender
2. Select your avatar
3. Choose a persona to chat with
4. Start conversing!

## Project Structure

```
lifeVoice/
├── app.py                      # Main Streamlit application
├── rag_engine.py              # FAISS vector database retrieval
├── agent_tools.py             # Agent tools (web search, time, calculator)
├── build_index.py             # Vector index builder
├── retrieve_context.py         # Context retrieval utilities
├── scraper.py                 # Data scraping utilities
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (gitignored)
├── .gitignore                # Git ignore rules
├── README.md                 # This file
├── vector_db/                # FAISS index and documents
│   ├── index.faiss
│   ├── labels.txt
│   └── docs.json
├── assets/                   # Images, fonts, and static assets
│   ├── avatars/
│   ├── lifevoice_logo.png
│   ├── Krobus.png
│   └── StardewValley.ttf
└── utils/                    # Utility modules
    ├── persona_prompts.py    # System prompts and prompt defenses
    ├── groq_client.py        # Groq LLM client
    ├── avatars.py            # Avatar management
    └── pixel_icons.py        # Pixel icon generation
```

## Tech Stack

### Models & APIs
- **LLM**: Groq API (fast inference)
- **Embeddings**: Sentence-BERT (`all-MiniLM-L6-v2`)
- **Vector Database**: FAISS (Facebook AI Similarity Search)

### Frameworks & Libraries
- **UI**: Streamlit
- **Agent Tools**: LangChain Core
- **Search**: DuckDuckGo Search
- **Vector Operations**: sentence-transformers, faiss-cpu
- **Environment**: python-dotenv

## Features in Detail

### RAG System
The RAG engine uses FAISS for efficient similarity search over persona-specific document chunks:
- Semantic search using Sentence-BERT embeddings
- Persona and sub-persona filtering
- Maximum context window management
- Fallback search when filtered results are insufficient

### Agent Tools
Three built-in tools extend the chatbot's capabilities:
1. **Web Search** - Current events and facts via DuckDuckGo
2. **Current Time** - Time-aware responses
3. **Calculator** - Basic math computations

### Prompt Defenses
Robust protection against prompt injection and jailbreak attempts:
- System instructions hidden from users
- Redirection of bypass attempts
- Character consistency maintained

## Development

### Adding New Personas
Edit `utils/persona_prompts.py` and add new persona configurations to the `PERSONAS` dictionary.

### Adding New Tools
Edit `agent_tools.py` and add new `@tool` decorated functions, then add them to the `tools` list.

### Rebuilding the Vector Index
```bash
python build_index.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| GROQ_API_KEY | Yes | Your Groq API key |

## Acknowledgments

- Stardew Valley for font inspiration
- Streamlit for the amazing UI framework
- Groq for fast LLM inference
- FAISS for vector search

## License

[Your License Here]

## Contributing

Feel free to open issues or submit pull requests!

---

**Made with ❤️ and pixel art**
