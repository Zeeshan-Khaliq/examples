
import pytest

from markdown2 import markdown
from langchain_text_splitters.markdown import MarkdownTextSplitter, MarkdownHeaderTextSplitter
from langchain.schema import Document

from splitters_confluence import ConfluenceMarkdownChunker

@pytest.fixture
def md_string():
    _string = """
    My name is zeeshan and this is just the starting string.

    ## Heading2-1

    This is heading2-1 text. This test should be a bit longer.
    but let us see if this will be correctly chunked.
    The rest of the stuff is not fully stripped.

    ## Heading2-2

    This is heading2-2 text

    ### Heading3

    This is heading3 text. 



    Unfortunately, due to page size, sometimes the Confluence API doesn't match the limit value and this is a very long. 
    If limit is 100 confluence seems to cap the response to 100. 
    Short sentence.
    Also, due to the Atlassian Python package, we don't get the “next” values from 
    the “_links” key because they only return the value from the result key. 
    So here, the pagination starts from 0 and goes until the max_pages, getting the 
    limit number of pages with each request. 
    
    #### Heading4
    This is heading4 text
    """
    return _string

@pytest.fixture
def header_splitter():
    return MarkdownHeaderTextSplitter(
        headers_to_split_on=[('###', "level_3"), ("##", "level_2")]
    )

@pytest.fixture
def text_splitter():
    return MarkdownTextSplitter(chunk_size=100, chunk_overlap=10)


def test_confluence_loader(md_string, header_splitter, text_splitter):
    
    md = markdown(md_string).strip("<pre><code>").split("</code></pre>")[0]
    documents = [
        Document(page_content=md, metadata={"title": "Page1"})
    ]
    
    chunker = ConfluenceMarkdownChunker(markdown_header_splitter=header_splitter, markdown_text_splitter=text_splitter)
    f = chunker.chunker(documents)
    for d in f:
        print(":"*10)
        print(len(d.page_content), d)


        


