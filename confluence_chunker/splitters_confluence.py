from copy import deepcopy
import re
from typing import (
    Any,
    List,
)
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter

from langchain_text_splitters import MarkdownHeaderTextSplitter, MarkdownTextSplitter
import logging

logging.basicConfig(level=logging.INFO)  # Set logging level
logger = logging.getLogger()

class ConfluenceMarkdownChunker:
    """
    Attempts to split the text along Markdown-formatted headings. 
    It keeps the headings in the `.page_content` and also adds `sub-title` tag
    to the metadata.

    Returns: List of Langchain Documents
    """

    def __init__(
            self, 
            markdown_text_splitter: MarkdownTextSplitter,
            markdown_header_splitter: MarkdownHeaderTextSplitter,
            table_separator: str = '|',
        ):
        self._table_separator = table_separator
        self._markdown_text_splitter = markdown_text_splitter
        self._markdown_header_splitter = markdown_header_splitter
    
    def chunker(self, documents):

        final = []
        for doc in documents:
            docs_splitted_by_header = self._markdown_header_splitter.split_text(doc.page_content)
                
            text_documents = []
            table_documents = []
            for header_doc in docs_splitted_by_header:

                text, tables = self._extract_text_tables_from_doc(header_doc)

                if header_doc.metadata:
                    subtitle = list(header_doc.metadata.values())[0]
                else:
                    subtitle = doc.metadata["title"]
                
                header_doc.metadata["sub-title"] = subtitle

                if text:
                    text_documents.append(
                        Document(
                            page_content=text, 
                            metadata=header_doc.metadata
                        )
                    )

                if tables:
                    metadata = deepcopy(doc.metadata)
                    metadata["sub-title"] = subtitle
                    for table in tables:
                        table_documents.append(
                            Document(
                                page_content=subtitle + " " + table,
                                metadata=metadata
                            )
                        )
            
            splitted = self._recursively_split_docs( # self._recursiveTextSplitter( #self._recursively_split_docs(
                text_documents, doc.metadata, 
                self._markdown_text_splitter._chunk_size, 
                list()
            )
            final.extend(splitted)
            final.extend(table_documents)
        
        return final

    def _recursively_split_docs(self, documents, page_metadata, chunk_size, all_docs):
        all_docs = all_docs or []

        for item in documents:
            subtitle = item.metadata["sub-title"]
            if len(item.page_content) <= chunk_size:
                item.page_content = subtitle + " " + item.page_content
                item.metadata = deepcopy(page_metadata)
                item.metadata["sub-title"] = subtitle
                all_docs.append(item)
            else:
                new_docs = self._markdown_text_splitter.split_documents([item])
                self._recursively_split_docs(new_docs, page_metadata, chunk_size, all_docs)
        
        return all_docs
    
    #def _recursiveTextSplitter(self, documents, page_metadata, chunk_size, all_docs):
    #    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=10)
    #    splitted_docs = splitter.split_documents(documents)
    #    print("+"*20)
    #    print(splitted_docs)
    #    return splitted_docs
            
    def _extract_text_tables_from_doc(self, doc: str):

        table_chunks = {}
        text_chunks  = []
        table_num = 0
        stripped = doc.page_content.strip()
        for line in stripped.splitlines():
            if line.strip().startswith(self._table_separator):
                if table_num in table_chunks.keys():
                    table_chunks[table_num].append(line.strip()) 
                else:
                    table_chunks[table_num]=[line.strip()] 
            else:
                table_num +=1
                text_chunks.append(line.strip())
        if table_chunks:
            final_tables = ["\n".join(table_chunks[i]) for i in table_chunks.keys()]
        else:
            final_tables = []
        
        final_texts= "\n".join(text_chunks)

        return final_texts, final_tables



