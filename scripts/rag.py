from langchain_core.documents import Document
from langchain_together import ChatTogether, TogetherEmbeddings
from langchain_core.prompts import  PromptTemplate
from langchain.chains import LLMChain
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv # type: ignore
from pathlib import Path
import json 
import os
from tqdm import tqdm

load_dotenv()
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT")
langchain_tracking = os.getenv("LANGCHAIN_TRACKING")
together_api_key = os.getenv("TOGETHER_API_KEY")
langchain_endpoint = os.getenv("LANGCHAIN_ENDPOINT")

llm = ChatTogether(
    model = "mistralai/Mistral-7B-Instruct-v0.3",
    together_api_key= os.getenv("TOGETHER_API_KEY"), # type: ignore
    temperature=0
)

def vectorise_configs(path):

    documents = []


    for file in path.rglob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for block in data["structure"].values():
            chunk_text = f"{block['purpose']}\n\n{block['content']}"
            documents.append(
                Document(
                    page_content=chunk_text,
                    metadata={
                        "repo_name": data.get("repo_name"),
                        "path": block.get("path"),
                        "language": block.get("language"),
                        "dependencies": block.get("dependencies"),
                    },
                )
            )

    embeddings = TogetherEmbeddings(
    model="togethercomputer/m2-bert-80M-32k-retrieval",  # Example embedding model
    api_key=os.getenv("TOGETHER_API_KEY")
    )

    vectorstore = Chroma.from_documents(documents, embeddings, persist_directory="/Users/krishiv/Desktop/Projects/config-assistant/data/vector_store")

    return vectorstore
    print(f"[+] Stored {len(documents)} documents in vectorstore")

def main():
    PATH = Path("/Users/krishiv/Desktop/Projects/config-assistant/data/configs/annotated_json")
    vectorstore = vectorise_configs(PATH)
    vectorstore.persist()
    retriever = vectorstore.as_retriever()

if __name__ == '__main__':
    main()