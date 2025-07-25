import os
from dotenv import load_dotenv
load_dotenv()
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.document_extraction.loaders import DoclingLoader
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from backend.prompts.extraction_prompts import structured_extraction_prompt

class LegalDocExtractionSchema(BaseModel):
    parties: List[str] = Field(..., description="Names of all parties involved")
    effective_date: str = Field(None, description="Effective date of the agreement")
    termination_date: str = Field(None, description="Termination date of the agreement")
    clauses: List[str] = Field(..., description="Summaries of all clauses or sections")

class ExtractionAgent:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

    def extract(self, file_path: str) -> List[Dict[str, Any]]:
        docs = DoclingLoader.load(file_path)
        splits = self.text_splitter.split_documents(docs)
        return [{"chunk": i, "text": doc.page_content} for i, doc in enumerate(splits)]

    def extract_structured(self, file_path: str) -> List[Dict[str, Any]]:
        docs = DoclingLoader.load(file_path)
        splits = self.text_splitter.split_documents(docs)
        prompt = ChatPromptTemplate.from_template(structured_extraction_prompt)
        results = []
        for i, doc in enumerate(splits):
            formatted_prompt = prompt.format(chunk=doc.page_content)
            response = self.llm.invoke(formatted_prompt)
            # Strip triple backticks and whitespace from LLM output
            content = response.content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            try:
                parsed = LegalDocExtractionSchema.model_validate_json(content)
                results.append(parsed.model_dump())
            except Exception as e:
                results.append({"error": str(e), "raw": response.content})
        return results

# Test function (can be run as __main__)
def test_extraction_agent():
    sample_pdf = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../docs/samples/TENANCY_AGREEMENT_CICULATED _JULY_2020.pdf'))
    print(f"Resolved sample file path: {sample_pdf}")
    if not Path(sample_pdf).exists():
        print(f"ERROR: File does not exist at {sample_pdf}")
        return
    agent = ExtractionAgent()
    structured = agent.extract_structured(sample_pdf)
    print(f"Structured extraction results (first chunk):\n{structured[0] if structured else 'No content'}")

if __name__ == "__main__":
    test_extraction_agent()