from src.core.summarizer import summarize_chunks
from src.services.embedding import embed_text
from src.utils.config import KEEP_LAST_N_PAIRS, CHUNK_SIZE
from src.utils.utils import format_chat_history, chunk_text
from datetime import datetime

def process_history_chat(
    history: list[tuple[str, str]],
    doc_id: str = "conversation",
    uploaded_by: str = "system",
    position: str = "automated"
) -> list[tuple[str, str]]:
    """
    Processes chat history by:
    1. Formatting full conversation
    2. Chunking it
    3. Summarizing each chunk
    4. Embedding summaries with metadata
    5. Truncating history if needed

    Args:
        history (list): List of (user, bot) message pairs.
        doc_id (str): Identifier for this chat history batch.
        uploaded_by (str): Who initiated the chat session.
        position (str): Role of the user or system.

    Returns:
        list: Truncated history for continued tracking.
    """
    formatted_text = format_chat_history(history)
    chunks = chunk_text(formatted_text, chunk_size=CHUNK_SIZE)
    summarized_chunks = summarize_chunks(chunks, doc_id=doc_id)

    timestamp = datetime.now().isoformat()
    for i, (chunk_id, summary) in enumerate(summarized_chunks):
        metadata = {
            "doc_id": doc_id,
            "chunk_index": i,
            "source_type": "history_chat",
            "uploaded_by": uploaded_by,
            "position": position,
            "timestamp": timestamp
        }
        embed_text(summary, chunk_id, metadata)

    truncated = history[-KEEP_LAST_N_PAIRS:] if KEEP_LAST_N_PAIRS > 0 else []
    print(truncated)
    return truncated

