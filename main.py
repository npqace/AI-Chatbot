from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from tqdm.auto import tqdm
from uuid import uuid4
from time import sleep
import tiktoken

# Initialize the FastAPI app
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 for templates
templates = Jinja2Templates(directory="templates")

# Define a function to return a description of the app
def get_app_description():
    return (
        "Welcome to the Q&A Bot API!"
        "This API processes documents and answers queries based on the content of those documents."
        "Use the '/process/' endpoint with a POST request to load and process documents."
        "Use the '/query/' endpoint with a POST request to ask questions."
    )

# Modify the root endpoint to serve a template
@app.get("/")
async def root(request: Request):
    # Example of passing dynamic content to your template
    return templates.TemplateResponse("index.html", {"request": request, "app_description": get_app_description()})


# Pydantic model for document processing
class DocumentProcessingRequest(BaseModel):
    directory: str

# Pydantic model for query
class QueryRequest(BaseModel):
    query: str

# Initialize the OpenAI API client
api_key = 'your-api-key-here'
client = OpenAI(api_key=api_key)

# Initialize the Qdrant client
vector_db = QdrantClient(":memory:") # In-memory instance for testing

vector_db.create_collection(
    collection_name="paracel_collection",
    vectors_config=VectorParams(size=1536, distance=Distance.DOT),
)

# Load and process documents
@app.post("/process/")
async def process_documents(request: DocumentProcessingRequest):
    loader = DirectoryLoader(request.directory, glob="**/*.html")
    docs = loader.load()

    data = []
    for doc in docs:
        data.append({
            'url': doc.metadata['source'].replace('rtdocs/', 'https://'),
            'text': doc.page_content
        })

    tokenizer = tiktoken.get_encoding('p50k_base')

    def tiktoken_len(text):
        tokens = tokenizer.encode(text, disallowed_special=())
        return len(tokens)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=20,
        length_function=tiktoken_len,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = []
    for idx, record in enumerate(tqdm(data)):
        texts = text_splitter.split_text(record['text'])
        chunks.extend([{
            'id': str(uuid4()),
            'text': texts[i],
            'chunk': i,
            'url': record['url']
        } for i in range(len(texts))])

    batch_size = 100
    for i in tqdm(range(0, len(chunks), batch_size)):
        i_end = min(len(chunks), i + batch_size)
        meta_batch = chunks[i:i_end]
        ids_batch = [x['id'] for x in meta_batch]
        texts = [x['text'] for x in meta_batch]

        try:
            res = client.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            )
        except:
            done = False
            while not done:
                sleep(5)
                try:
                    res = client.embeddings.create(
                        input=texts,
                        model="text-embedding-3-small"
                    )
                    done = True
                except:
                    pass

        embeds = [record.embedding for record in res.data]
        meta_batch = [{'text': x['text'], 'chunk': x['chunk'], 'url': x['url']} for x in meta_batch]
        list_batch = list(zip(ids_batch, embeds, meta_batch))
        points_list = [PointStruct(id=p[0], vector=p[1], payload=p[2]) for p in list_batch]

        vector_db.upsert(
            collection_name="paracel_collection",
            wait=True,
            points=points_list
        )

    return {"message": "Documents processed successfully"}

# Query the processed documents
@app.post("/query/")
async def query_documents(request: QueryRequest):
    response = client.embeddings.create(
        input=[request.query],
        model="text-embedding-3-small"
    )
    xq = response.data[0].embedding

    search_result = vector_db.search(
        collection_name="paracel_collection", query_vector=xq, limit=10
    )

    contexts = [point.payload['text'] for point in search_result]
    contexts = ' '.join(contexts)

    primer = (
        "You are Q&A bot. A highly intelligent system that answers user queries based on the contexts. "
        "If the information cannot be found, you truthfully say 'I don't know'."
    )

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": primer}, {"role": "user", "content": request.query}, {"role": "assistant", "content": contexts}]
    )

    return {"response": chat_completion.choices[0].message.content}
