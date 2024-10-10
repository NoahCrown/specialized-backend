import os
import json
from typing import Dict, List
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from flask import current_app
import csv
import shutil

load_dotenv()

class JobDescriptionVectorStore:
    def __init__(self, save_path: str = "job_descriptions_index"):
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        self.embeddings = OpenAIEmbeddings()
        self.save_path = save_path
        self.vectorstore = self.load_or_create_vectorstore()
        self.llm = OpenAI(temperature=0)
        self.qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=self.vectorstore.as_retriever())

    def load_or_create_vectorstore(self) -> FAISS:
        if os.path.exists(self.save_path):
            return FAISS.load_local(self.save_path, self.embeddings, allow_dangerous_deserialization=True)
        return FAISS.from_texts(["placeholder"], self.embeddings)

    def is_empty(self):
        return len(self.vectorstore.docstore._dict) <= 1

    def clear_vectorstore(self):
        if os.path.exists(self.save_path):
            shutil.rmtree(self.save_path)
        self.vectorstore = FAISS.from_texts(["placeholder"], self.embeddings)
        self.save_vectorstore()
        print("Vector store has been cleared and reinitialized.")

    def add_job_descriptions_from_csv(self, csv_file_path: str, language: str = "en"):
        if not self.is_empty():
            print("Vector store already contains data. Skipping CSV import.")
            return

        documents = []
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ai_generated_content = row.get("English Tone / Condense 2 API Output", "")
                polished_content = row.get("Approved English Version", "")

                if ai_generated_content:
                    metadata = {
                        "language": language,
                        "source": "ai_generated",
                        **row
                    }
                    document = Document(page_content=ai_generated_content, metadata=metadata)
                    documents.append(document)

                if polished_content:
                    metadata = {
                        "language": language,
                        "source": "polished",
                        **row
                    }
                    document = Document(page_content=polished_content, metadata=metadata)
                    documents.append(document)

        if documents:
            self.vectorstore.add_documents(documents)
            self.save_vectorstore()
            print(f"Added {len(documents)} documents from {csv_file_path}")
        else:
            print("No valid documents found in the CSV file.")

    def save_vectorstore(self):
        self.vectorstore.save_local(self.save_path)

    def query(self, question: str) -> str:
        return self.qa.run(question)

    def get_all_documents(self):
        documents = []
        for doc_id in self.vectorstore.docstore._dict:
            doc = self.vectorstore.docstore.search(doc_id)
            if doc.page_content != "placeholder":
                documents.append({
                    "id": doc_id,
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
        return documents

    def save_results(self, job_id: str, results: Dict[str, str]):
        """
        Save the analysis results back to the vector store.
        
        :param job_id: A unique identifier for the job description
        :param results: A dictionary containing JobDescription, Changes, Analysis, and RecruiterRecommendations
        """
        content = json.dumps(results)
        metadata = {
            "type": "analysis_results",
            "job_id": job_id
        }
        document = Document(page_content=content, metadata=metadata)
        self.vectorstore.add_documents([document])
        self.save_vectorstore()
        print(f"Saved analysis results for job ID: {job_id}")

    def get_analysis_results(self, job_id: str) -> Dict[str, str]:
        """
        Retrieve the analysis results for a specific job ID.
        
        :param job_id: The unique identifier for the job description
        :return: A dictionary containing the analysis results, or None if not found
        """
        documents = self.vectorstore.similarity_search(
            f"analysis_results for job ID {job_id}", 
            k=1, 
            filter={"type": "analysis_results", "job_id": job_id}
        )
        if documents:
            return json.loads(documents[0].page_content)
        return None

def load_job_descriptions_from_csv(csv_file_path: str, vector_store: JobDescriptionVectorStore, language: str = "en"):
    try:
        vector_store.add_job_descriptions_from_csv(csv_file_path, language)
        
        documents = vector_store.get_all_documents()
        print(f"Current documents in the vector store: {len(documents)}")
        for doc in documents[:5]:
            print(f"ID: {doc['id']}")
            print(f"Content: {doc['content'][:100]}...")
            print(f"Metadata: {doc['metadata']}")
            print("---")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def get_store():
    if 'vector_store' not in current_app.extensions:
        current_app.extensions['vector_store'] = JobDescriptionVectorStore()
    return current_app.extensions['vector_store']