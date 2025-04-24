import os
import openai
import datetime
from src.utils.text_chunking import chunk_text
from src.utils.history_format import format_chat_history
from dotenv import load_dotenv
from src.utils.config import OPENAI_API_KEY

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def summarize_chunks(chunks: list[str], doc_id: str = "summary") -> list[tuple[str, str]]:
    """
    Summarizes each chunk and returns (chunk_id, summary).

    Args:
        chunks (list): List of text chunks.
        doc_id (str): Base identifier for naming summary chunks.

    Returns:
        list of (chunk_id, summary)
    """
    result = []

    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_summary_chunk_{i}"
        summary = summarize_single_chunk(chunk)
        result.append((chunk_id, summary))

    return result

def summarize_single_chunk(chunk):
    """
    Summarizes a single chat history chunk using OpenAI with a structured prompt.

    Args:
        chunk (str): The text chunk to summarize.

    Returns:
        str: A structured summary of the chunk.
    """
    prompt = f"""
    ### **Role & Goal:**  
    You are an **AI assistant** specializing in **summarizing structured conversations** between a **user and a chatbot assistant**.  
    Your task is to **summarize each conversation chunk** while preserving **all key details, maintaining logical coherence, and ensuring readability**.  

    ### **Requirements:**  
    1. **Preserve Key Information:**  
    - Always retain names, dates, times, locations, numbers, and technical terms.  
    - Keep the sequence of events intact, ensuring logical flow.  
    - Avoid omitting critical decisions, conclusions, or action points.  

    2. **Ensure Contextual Consistency Across Chunks:**  
    - Assume the conversation is part of a **larger, token-limited history**.  
    - Summarize **without excessive repetition**, ensuring smooth integration with other chunks.  
    - Do **not** assume missing context—only summarize based on the provided chunk.  

    3. **Formatting & Style:**  
    - Present the summary in a **cohesive paragraph**, grouping related ideas naturally.  
    - Use **clear and structured sentences** to maintain readability.  
    - If a decision or conclusion is reached, emphasize it at the end.  
    - In the start of summarization, signal that this is a summary of part of the conversation by using the phrase "This is a summarization of a part of history chat"
    - At the end of summarization, use phrase "This is the end of summarization"
    - Example: 
    "This is a summarization of a part of history chat.
    The user inquired about the details of the upcoming volunteer trip to Bắc Kạn. The chatbot confirmed that the trip is scheduled for March 14-16, 2025, with departure at 6 PM from Minh Thu’s house in Mai Dịch, Hà Nội. A total of 12 members will participate, and the donation fund currently stands at 15 million VNĐ. The budget is allocated as follows: 9 million VNĐ for gifts and school supplies, and 6 million VNĐ for renting a 16-seater car with a driver. The trip is organized by founder Dao Viet Thanh, co-founders Ta Thanh Thao and Nguyen Minh Thu, with Dao Quy Duong as the head of communications. The itinerary includes a departure at 6 PM on March 14, arriving in Bắc Kạn at 11 PM, followed by various activities such as distributing gifts, supporting local schools, and engaging in cultural interactions.
    This is the end of summarization."
    ---
    
    📝 **Final Summary:**  
    [Generate a well-structured paragraph that captures all key points accurately.]  

    ```
    **Conversation Chunk to Summarize:**
    {chunk}

    **Provide a structured summary based on the above format.**
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are an expert AI summarizer."},
                      {"role": "user", "content": prompt}]
        )

        summary = response.choices[0].message.content.strip()

        return summary

    except Exception as e:
        return f"⚠️ Error generating summary: {str(e)}"


