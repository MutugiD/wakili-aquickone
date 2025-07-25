import os
from typing import Iterator, List, Union
from pathlib import Path
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document as LCDocument

# Import docling (assume installed)
from docling.document_converter import DocumentConverter

class DoclingPDFLoader(BaseLoader):
    def __init__(self, file_path: Union[str, List[str]]):
        self._file_paths = [Path(f) for f in (file_path if isinstance(file_path, list) else [file_path])]
        self._converter = DocumentConverter()

    def lazy_load(self) -> Iterator[LCDocument]:
        for source in self._file_paths:
            dl_doc = self._converter.convert(source).document
            text = dl_doc.export_to_markdown()
            yield LCDocument(page_content=text)

    def load(self) -> List[LCDocument]:
        return list(self.lazy_load())

class DoclingDOCXLoader(BaseLoader):
    def __init__(self, file_path: Union[str, List[str]]):
        self._file_paths = [Path(f) for f in (file_path if isinstance(file_path, list) else [file_path])]
        self._converter = DocumentConverter()

    def lazy_load(self) -> Iterator[LCDocument]:
        for source in self._file_paths:
            dl_doc = self._converter.convert(source).document
            text = dl_doc.export_to_markdown()
            yield LCDocument(page_content=text)

    def load(self) -> List[LCDocument]:
        return list(self.lazy_load())

class DoclingOCRLoader(BaseLoader):
    def __init__(self, file_path: Union[str, List[str]]):
        self._file_paths = [Path(f) for f in (file_path if isinstance(file_path, list) else [file_path])]
        self._converter = DocumentConverter()

    def lazy_load(self) -> Iterator[LCDocument]:
        for source in self._file_paths:
            dl_doc = self._converter.convert(source).document
            # OCR is automatically applied by docling for images/scanned PDFs
            text = dl_doc.export_to_markdown()
            yield LCDocument(page_content=text)

    def load(self) -> List[LCDocument]:
        return list(self.lazy_load())

class DoclingLoader:
    """
    Unified loader that auto-selects the correct loader based on file extension.
    Supports PDF, DOCX, and image-based (OCR) documents.
    """
    @staticmethod
    def load(file_path: str) -> list[LCDocument]:
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            return DoclingPDFLoader(file_path).load()
        elif ext == ".docx":
            return DoclingDOCXLoader(file_path).load()
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            return DoclingOCRLoader(file_path).load()
        else:
            # Default: try PDF loader, fallback to OCR
            try:
                return DoclingPDFLoader(file_path).load()
            except Exception:
                return DoclingOCRLoader(file_path).load()