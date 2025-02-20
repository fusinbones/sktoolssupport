# Company Chatbot with LangChain and Intercom Integration

This chatbot integrates with your company's data using LangChain and provides customer service through Intercom.

## Features

- LangChain-based conversational AI
- Integration with Intercom for customer service
- Vector store for efficient knowledge retrieval
- Support for multiple document formats
- Real-time responses through FastAPI

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your data:
   - Create a `data` directory in the project root
   - Add your company's documents (PDFs, TXTs, etc.) to the data directory

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key
   - Add your Intercom access token

5. Run the server:
```bash
uvicorn chatbot:app --host 0.0.0.0 --port 8000 --reload
```

## Intercom Setup

1. In your Intercom dashboard, go to Settings → Webhooks
2. Add a new webhook with the URL: `https://your-domain.com/intercom-webhook`
3. Subscribe to the following topics:
   - conversation.user.created

## API Endpoints

- POST `/chat`: Direct chat endpoint
- POST `/intercom-webhook`: Webhook endpoint for Intercom integration

## Usage

The chatbot will automatically:
1. Load and process your company's data
2. Create embeddings for efficient searching
3. Respond to customer inquiries through Intercom
4. Provide relevant information from your knowledge base

## Directory Structure

```
company-chatbot/
├── data/                  # Your company's documents
├── chroma_db/            # Vector store database
├── chatbot.py            # Main application
├── requirements.txt      # Dependencies
├── .env                  # Configuration
└── README.md            # Documentation
```
