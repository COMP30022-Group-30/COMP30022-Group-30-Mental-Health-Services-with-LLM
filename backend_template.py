import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.chains import RetrievalQA
import numpy as np

# -----------------------------
# (1) Load environment variables
# -----------------------------
load_dotenv()  # reads .env file in project root
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# -----------------------------
# (2) Connect to Supabase
# -----------------------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# (3) Embeddings setup
# -----------------------------
USE_MOCK = True  # toggle True for testing without hitting OpenAI

if USE_MOCK:
    class MockEmbeddings:
        def embed_query(self, text):
            return np.random.rand(1536).tolist()
        def embed_documents(self, texts):
            return [np.random.rand(1536).tolist() for _ in texts]

    embeddings = MockEmbeddings()
else:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# -----------------------------
# (4) Initialize vectorstore
# -----------------------------
vectorstore = SupabaseVectorStore(
    client=supabase,
    embedding=embeddings,
    table_name="services",
    query_name="search_services"  # your SQL function
)

# -----------------------------
# (5) Test retrieval
# -----------------------------
user_query = "Mental health support for youth"
docs = vectorstore.similarity_search(user_query, k=3)

print(f"Top {len(docs)} results for query: '{user_query}'\n")
for i, d in enumerate(docs, start=1):
    print(f"[{i}] {d.page_content}\n")