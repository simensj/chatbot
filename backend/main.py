import os
import json
import re
import constants
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chat_models import init_chat_model

# Set environment variables for API keys
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = constants.LANGSMITH_API_KEY
os.environ["LANGSMITH_PROJECT"] = "euChatbot"
os.environ["OPENAI_API_KEY"] = constants.APIKEY

llm = init_chat_model("gpt-4o-mini", model_provider="openai", temperature=0.3, max_tokens=250)
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Load JSON file and extract chunks
with open("chunked_legal_document.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    chunks = data  # Assuming JSON contains a "chunks" key with list of dictionaries

docs = [Document(page_content=chunk["text"], metadata={"id": chunk["id"]}) for chunk in chunks]

# Create FAISS vector store
vector_store = FAISS.from_documents(docs, embeddings)

prompt = PromptTemplate.from_template(
    "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
)

# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    for doc in retrieved_docs:
            print(doc.metadata.get("id", "No ID"))  # Print the ID of each retrieved doc
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    formatted_prompt = prompt.format(question=state["question"], context=docs_content)
    messages = [
        {"role": "system", "content": 
            "Du er en profesjonell og presis AI-assistent som er ekspert i jus og EU-regelverk angående KI-forordningen."
            "Du har tilgang til et dokument som inneholder informasjon om EU-regelverk. "
            "Svar på spørsmålet basert på informasjonen i dokumentet."
            "Svar på en tydelig og profesjonell måte, uavhengig av dokumentets struktur."
            "Hvis dokumentet inneholder stikkord eller ufullstendige setninger, omskriv svaret ditt til en sammenhengende og velstrukturert tekst."
            "Hvis spørsmålet er om et annet emne enn det som er dekket i dokumentet, svar kort og høflig om at du kun kan svare på spørsmål relatert til KI-forordningen."
            },
        {"role": "user", "content": formatted_prompt}
    ]
    
    response = llm.invoke(messages)
    return {"answer": response.content}

# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

query = str(input("Enter your query: "))

response = graph.invoke({"question": query})
cleaned_answer = re.sub(r"\*\*(.*?)\*\*", r"\1", response["answer"])
#print(response["answer"])
print(f'Answer: {cleaned_answer}')