import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.chains import RetrievalQA

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Set up embeddings + vector store
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectorstore = SupabaseVectorStore(
    client=supabase_client,
    embedding=embeddings,
    table_name="documents",  # Supabase table for storing vectors
)

# LLM
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)

# RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    return_source_documents=True,
)

def get_chatbot_response(query: str):
    """Takes user query, returns chatbot answer + sources."""
    response = qa_chain.invoke({"query": query})
    return {
        "answer": response["result"],
        "sources": [doc.metadata for doc in response["source_documents"]],
    }
