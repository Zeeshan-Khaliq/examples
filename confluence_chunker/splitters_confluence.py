from copy import deepcopy
import re
from typing import (
    Any,
    List,
)
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

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

        #print(documents[0].page_content)
        #print(documents[0].metadata)
        final = []
        for doc in documents:
            docs_splitted_by_header = self._markdown_header_splitter.split_text(doc.page_content)

            for item in docs_splitted_by_header:
                print(item.page_content)
                print(item.metadata)

            text_documents = []
            table_documents = []
            for header_doc in docs_splitted_by_header:

                text, table = self._split_tables_and_text(header_doc)
        
                if text: 
                    text_documents.append(Document(page_content=text[0], metadata=header_doc.metadata))

                if table:
                    metadata = deepcopy(doc.metadata)
                    metadata["sub-title"] = list(header_doc.metadata.values())[0]
                    table_documents.append(
                        Document(
                            page_content=list(header_doc.metadata.values())[0] + " " + table[0],
                            metadata=metadata
                        )
                    )
            
        
            final.extend(
                self.process_header_splitted_docs(
                    text_documents, doc.metadata, 
                    self._markdown_text_splitter._chunk_size, 
                    list()
                )
            )
            final.extend(table_documents)
        return final
    
    def chunker_2(self, documents):

        final = []
        for doc in documents:
            docs_splitted_by_header = self._markdown_header_splitter.split_text(doc.page_content)

            #for item in docs_splitted_by_header:
            #    print("~"*10)
            #    print(item.page_content)
            #    print("item.metadata: ", item.metadata)
                
            text_documents = []
            table_documents = []
            for header_doc in docs_splitted_by_header:

                text, tables = self._split_tables_2(header_doc)

                # print("#"*20)
                # print(header_doc.metadata)
                # print(text)
                # print("type: ", type(text))
                # print("#"*20)

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
            
            #print(len(text_documents))
            splitted = self.process_header_splitted_docs_2(
                    text_documents, doc.metadata, 
                    self._markdown_text_splitter._chunk_size, 
                    list()
                )
            final.extend(
                splitted   
            )
            #for d in splitted:
            #    print("*"*10)
            #    print("splitted:")
            #    print(d.page_content)
            #    print(d.metadata)

            final.extend(table_documents)
        
        return final


    def process_header_splitted_docs_2(self, documents, page_metadata, chunk_size, all_docs):
        all_docs = all_docs or []
        #print(all_docs)
        for item in documents:
            #print("+"*20)
            #print(item)
            subtitle = item.metadata["sub-title"]
            if len(item.page_content) <= chunk_size:
                item.page_content = subtitle + " " + item.page_content
                item.metadata = deepcopy(page_metadata)
                item.metadata["sub-title"] = subtitle
                #print(item)
                all_docs.append(item)
            else:
                new_docs = self._markdown_text_splitter.split_documents([item])
                #print("here::::::")
                #print(new_docs)
                self.process_header_splitted_docs(new_docs, page_metadata, chunk_size, all_docs)
        
        return all_docs
            
    def process_header_splitted_docs(self, documents, page_metadata, chunk_size, all_docs):
        all_docs = all_docs or []
        for item in documents:
            subtitle = list(item.metadata.values())[0]
            if len(item.page_content) <= chunk_size:
                item.page_content = subtitle + " " + item.page_content
                item.metadata = deepcopy(page_metadata)
                item.metadata["sub-title"] = subtitle
                all_docs.append(item)
            else:
                new_docs = self._markdown_text_splitter.split_documents([item])
                self.process_header_splitted_docs(new_docs, page_metadata, chunk_size, all_docs)
        
        return all_docs  

    
    def _split_tables_2(self, doc: str):

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

        # print("*"*20)
        # print(len(final_texts))
        # print(final_texts)
        
        # final_table_docs = []
        # if final_tables:
        #     for table in final_tables:
        #         final_table_docs.append(
        #             Document(
        #                 page_content=table,
        #                 metadata=doc.metadata
        #             )
        #         )
        # final_text_docs = []
        # if final_texts:
        #     for text in final_texts:
        #         final_text_docs.append(
        #             Document(
        #                 page_content=text,
        #                 metadata=doc.metadata
        #             )
        #         )

        return final_texts, final_tables


    def _split_tables_and_text(self, doc: str):
        all_table_chunks = []
        all_text_chunks = []
        stripped = doc.page_content.strip()
        if stripped:                                                            
            text_chunks, table_chunks = self._split_tables(stripped)
            if table_chunks:
                all_table_chunks.extend(table_chunks)
            all_text_chunks.append(text_chunks)
                        
        return all_text_chunks, all_table_chunks

    def _split_tables(self, text: str):
        table_chunks = {}
        text_chunks  = []
        table_num = 0
        for line in text.splitlines():
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

        return "\n".join(text_chunks), final_tables


if __name__ == "__main__":
    from markdown2 import markdown
    import os
    from langchain_text_splitters.markdown import MarkdownTextSplitter, MarkdownHeaderTextSplitter
    from langchain.schema import Document
    
    md_string = """
    ## Heading2 - 1

    This is heading2-1 text

    ## Heading2 - 2

    This is heading2-2 text
    """
    md = markdown(md_string)
    documents = [
        Document(page_content=md, metadata={"title": "Page1"})
    ]
    #print(documents)
    
    chunk_size = 1000
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "level_1"), ("##", "level_2"), ('###', "level_3")]
    )
    text_splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=0)

    chunker = ConfluenceMarkdownChunker(markdown_header_splitter=header_splitter, markdown_text_splitter=text_splitter)
    final = chunker.chunker(documents)
