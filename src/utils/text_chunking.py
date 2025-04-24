import tiktoken  
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils.config import CHUNK_SIZE
def count_tokens(text):
    """
    Counts the number of tokens in a given text using tiktoken.

    Args:
        text (str): The text to be tokenized.

    Returns:
        int: The token count.
    """
    encoding = tiktoken.encoding_for_model("gpt-4o")
    return len(encoding.encode(text))

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """
    Chia văn bản bằng RecursiveCharacterTextSplitter của LangChain,
    GIỮ nguyên định dạng dòng và cho phép chồng lấn giữa các chunk.

    Args:
        text (str): Văn bản gốc.
        chunk_size (int): Số lượng ký tự mỗi chunk.

    Returns:
        list[str]: Danh sách các đoạn text đã chia.
    """
    CHUNK_OVERLAP = 100
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(text)

    for i, chunk in enumerate(chunks, 1):
        print(f"\n🧩 Chunk {i}:\n{'-'*40}\n{chunk}\n{'='*40}")

    return chunks