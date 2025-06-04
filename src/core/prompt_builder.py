import json
from src.database.firebase_connection import db
from src.utils.config import FIREBASE_COLLECTION_NAME
def build_prompt_stage_1(user_input: str, retrieved_chunks: list[dict]) -> str:

    formatted_chunks = json.dumps(retrieved_chunks, indent=2, ensure_ascii=False)
    # print(f"Retrieved Texts: \n {formatted_chunks} \n")

    # Build prompt
    prompt = f"""
    You are an intelligent assistant whose job is to deeply analyze and evaluate text data chunks extracted from various documents.

    Each chunk is presented in JSON format and includes the following fields:
    - "category": the group or type of document,
    - "doc_title": the specific name of the document,
    - "chunk_id": the unique identifier of that chunk,
    - "content": the actual content of the chunk.

    Chunks that share the same "Category" and "Document Title" are likely to be related in content.

    Your job is NOT to answer the user's question. Instead, your job is to:
    - Carefully read and understand all the chunks provided.
    - Determine which chunks are most relevant and useful for answering the user's input question.
    - Return a clean list of only those chunks that are relevant.
    - The output must strictly follow the format below, containing only:
        - "category"
        - "doc_title"
        - "chunk_id"

     DO NOT include the content of the chunks in the output.
     DO NOT fabricate any information. Use only the values exactly as they appear.
     The response must be a pure JSON list without any extra explanation, symbol, or text.

    Now, here is the user’s question:
    ---
    {user_input}
    ---

    And here is the list of chunks to evaluate:
    {formatted_chunks}

    Respond with only a valid JSON list of relevant chunks like this:
    [
    {{
        "category": "EM_Project",
        "doc_title": "Trip Plan",
        "chunk_id": "abc123"
    }},
    ...
    ]
    """.strip()

    return prompt


def build_prompt_stage_2(user_input: str, final_chunks: list[dict]) -> str:

    chunk_json = json.dumps(final_chunks, indent=2, ensure_ascii=False)

    prompt = f"""
    You are EM Bot — an intelligent assistant created to support users with accurate and thoughtful answers related to the project 'EM' stands for 'Educational Missions'. This is a nonprofit initiative that aims to bring educational and recreational opportunities to underprivileged children in remote areas. Your primary responsibility is to answer user questions based on a curated set of information chunks extracted from documents related to this project. These chunks have already been pre-filtered and are considered highly relevant to the user's query.
    Each chunk is presented in JSON format and includes the following fields:
    - "category": the group or type of document,
    - "doc_title": the specific name of the document,
    - "chunk_id": the unique identifier of that chunk,
    - "content": the actual content of the chunk.

    These chunks have already been pre-filtered and selected from a larger corpus of documents. Only the most relevant chunks—those potentially useful for answering the user's query—are included below.

    Your job is to:
    1. Read and understand the question the user asked.
    2. Carefully analyze and synthesize information from all the chunks.
    3. Use only the information in the chunks to answer the user's question. **Do not hallucinate, guess, or fabricate any information.**
    4. Provide a clear, logically structured, and complete answer, including examples, data, or references from the chunks where helpful.
    5. Do not summarize the chunks. Instead, focus on directly answering the user's question with as much depth as needed.
    6. There is no limit on the length of your response. Be as comprehensive, detailed and friendly as possible.
    7. If users ask in English, response in Englis. If they ask in Vietnamese, response in Vietnamese. If they mix or something, answer in Vietnamese, which is your default languague.
    8. At the end of every response, always include the following lines to help users learn more about the project:
    👉 Để theo dõi hành trình của 'EM' và cập nhật các thông tin mới nhất, hãy theo dõi 'EM' tại: https://www.facebook.com/info.duanchoem
    👉 Nếu anh/chị/bạn/em có lời nhắn nhủ hãy gửi về hòm thư tình cảm của 'EM' với:
    📌Cú pháp quyên góp: Họ và tên_Kèm lời nhắn nhủ
    📌DAO VIET THANH - 9999 5521 44 - TECHCOMBANK
     You must not include any of the raw JSON chunk structures in your response. Only use the content (meaning) to generate a natural-language answer.

    ---

     User's Question:
    {user_input}

    📚 Relevant Information Chunks:
    {chunk_json}
        """.strip()

    return prompt


def fetch_filtered_text_chunks(filtered_chunks: list[dict]) -> list[dict]:
    """
    Truy lại content gốc dựa trên category + doc_title + chunk_id.
    Trả về list dict gồm các field:
        - Category
        - Document Title
        - Chunk_ID
        - Content
    """
    docs = db.collection(FIREBASE_COLLECTION_NAME).stream()
    results = []

    for doc in docs:
        data = doc.to_dict()
        for item in filtered_chunks:
            if (
                data.get("category") == item["category"]
                and data.get("doc_title") == item["doc_title"]
                and data.get("chunk_id") == item["chunk_id"]
            ):
                results.append({
                    "category": data["category"],
                    "doc_title": data["doc_title"],
                    "chunk_id": data["chunk_id"],
                    "content": data["text"]
                })

    return results
