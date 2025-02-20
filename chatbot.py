import os
from typing import Dict, List
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import intercom
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables
load_dotenv()

class ChatbotService:
    def __init__(self):
        # Initialize OpenAI and Intercom clients
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-4"
        )
        self.intercom_client = intercom.Client(
            personal_access_token=os.getenv('INTERCOM_ACCESS_TOKEN')
        )
        
        # Initialize embeddings and vector store
        self.embeddings = OpenAIEmbeddings()
        self.initialize_knowledge_base()
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize the conversation chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            memory=self.memory,
            return_source_documents=True
        )

    def initialize_knowledge_base(self):
        """Initialize and load the knowledge base from company data"""
        # Load documents from the data directory
        loader = DirectoryLoader(
            './data',
            glob="**/*.*",
            show_progress=True
        )
        documents = loader.load()
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_documents(documents)
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )

    async def get_response(self, user_message: str, conversation_id: str) -> Dict:
        """Get response from the chatbot"""
        try:
            # Get response from LangChain
            response = self.qa_chain({"question": user_message})
            
            # Extract answer and sources
            answer = response['answer']
            sources = [doc.metadata for doc in response.get('source_documents', [])]
            
            return {
                "response": answer,
                "sources": sources,
                "conversation_id": conversation_id
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def handle_intercom_webhook(self, webhook_data: Dict) -> None:
        """Handle incoming Intercom webhooks"""
        try:
            if webhook_data.get('topic') == 'conversation.user.created':
                conversation_id = webhook_data['data']['item']['id']
                user_message = webhook_data['data']['item']['conversation_message']['body']
                
                # Get chatbot response
                response = await self.get_response(user_message, conversation_id)
                
                # Send response back to Intercom
                self.intercom_client.conversations.reply(
                    conversation_id=conversation_id,
                    type='admin',
                    message_type='comment',
                    body=response['response']
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Initialize FastAPI app
app = FastAPI()
chatbot_service = ChatbotService()

class Message(BaseModel):
    text: str
    conversation_id: str

@app.post("/chat")
async def chat_endpoint(message: Message):
    """Endpoint for direct chat interactions"""
    return await chatbot_service.get_response(message.text, message.conversation_id)

@app.post("/intercom-webhook")
async def intercom_webhook(webhook_data: Dict):
    """Endpoint for Intercom webhooks"""
    await chatbot_service.handle_intercom_webhook(webhook_data)
    return {"status": "success"}
