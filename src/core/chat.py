import openai
import os
import re

from src.utils.config import TOKEN_LIMIT, OPENAI_API_KEY
from src.utils.utils import count_tokens
from src.storage.history import save_history_to_xml, load_history_from_xml
from src.core.retrieval import retrieve_relevant_chunks
from src.services.chat_history_handler import process_history_chat
from src.services.embedding import generate_embedding
from dotenv import load_dotenv

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def chat_with_gpt(user_input: str, history: list[tuple[str, str]], user_id: str) -> tuple[str, list[tuple[str, str]]]:
    """
    Handles chatbot conversation, tracks tokens, retrieves document information, and manages history overflow.

    Args:
        user_input (str): Latest user message.
        history (List[Tuple[str, str]]): Existing conversation history.

    Returns:
        Tuple[str, List[Tuple[str, str]]]: (Bot response, updated history)
    """
    # Step 0: Embed user input
    user_embedding = generate_embedding(user_input)
        
    # Step 1: Retrieve relevant memory info
    retrieved_texts = retrieve_relevant_chunks(query_embedding = user_embedding, top_k= 5, user_id = user_id)

    # retrieved_output_path = "/Users/ngoquangduc/Desktop/AI_Project/chatbot_rag/data_test/retrieved_chunks.txt"

    # with open(retrieved_output_path, "w", encoding="utf-8") as f:
    #     for i, chunk in enumerate(retrieved_texts):
    #         f.write(f"--- Chunk {i+1} ---\n")
    #         f.write(chunk + "\n\n")

    # print(f"📄 Retrieved texts đã được lưu vào: {retrieved_output_path}")
    
    # Step 2: Build prompt
    prompt = build_prompt(user_input, history, retrieved_texts)

    # Step 3: Send to OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )
    bot_response = response.choices[0].message.content.strip()

    # Step 4: Token tracking
    total_tokens = count_tokens(prompt) + count_tokens(bot_response)
    print(f"📊 Token Count - Total Prompt: {total_tokens}")

    # Step 5: Update history
    updated_history = history + [(user_input, bot_response)]

    if total_tokens > TOKEN_LIMIT:
        print("⚠️ Token limit exceeded! Chunking and summarizing chat history...")
        updated_history = process_history_chat(history = updated_history, source_type=f"{user_id}_conversation", user_id = user_id)

    return bot_response, updated_history

def build_prompt(user_input: str, history: list[tuple[str, str]], retrieved_texts: list[str]) -> str:
    """
    Builds the full prompt with history, memory and system instructions.
    """
    # History chat
    history_chat = "\n".join([f"User: {user}\nAssistant: {bot}" for user, bot in history])
    history_chat = f"<History Chat>\n{history_chat}\n</History Chat>" if history_chat else "<History Chat>\n(No prior chat history)\n</History Chat>"

    # Memory section
    memory_section = "<Memory>\n"
    user_uploaded_data = []
    summarized_chat_history = []

    for text in retrieved_texts:
        if "This is a summarization of a part of history chat" in text:
            summarized_chat_history.append(text)
        else:
            user_uploaded_data.append(text)

    if user_uploaded_data:
        memory_section += "[User-Uploaded Documents]\n" + "\n".join([f"- {doc}" for doc in user_uploaded_data]) + "\n"

    if summarized_chat_history:
        memory_section += "[Past Summarized History]\n" + "\n".join([f"- {summary}" for summary in summarized_chat_history]) + "\n"

    memory_section += "</Memory>"

    # Background instructions
    background_section = (
        "Background: You are an assistant with 20 years of experience. Your name is OLB Bot, you were created by Ngô Quang Đức who is a member of OLB. Your responsibility is to support and answer all OLB member questions. "
        "The History Chat section contains the most recent user interactions and bot responses. "
        "The Memory section consists of two types of documents: "
        "1 User-uploaded files (facts, reports, or guidelines). "
        "2 Summarized past chat history (long-term memory). "
        "\n\nImportant Rules: "
        "- If recent history conflicts with summarized history, prioritize recent. "
        "- If answering from uploaded documents, state '[Source: User-Uploaded Document]'. "
        "- If answering from summarized history, state '[Source: Past History Chat]'. "
        "- Keep all names in original format. Do not translate them. "
        "- If no relevant info, say I DON'T KNOW and give helpful suggestions without hallucinating."
    )

    # Final composition
    user_prompt = f"Current User Input: {user_input}"

    final_prompt = f"""
{history_chat}

{memory_section}

{background_section}

{user_prompt}
    """.strip()

    return final_prompt

