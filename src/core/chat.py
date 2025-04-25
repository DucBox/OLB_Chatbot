import openai
import os
import re
import json
from src.utils.config import TOKEN_LIMIT, OPENAI_API_KEY
from src.utils.text_chunking import count_tokens
from src.utils.xml_utils import save_history_to_xml, load_history_from_xml
from src.core.retrieval import retrieve_relevant_chunks
from src.services.chat_history_handler import process_history_chat
from src.services.embedding_handler import generate_embedding
from src.utils.utils import call_gpt
from src.core.prompt_builder import build_prompt_stage_1, build_prompt_stage_2, fetch_filtered_text_chunks
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
    print("Retrieving ....")
    # Step 1: Retrieve relevant memory info
    retrieved_texts = retrieve_relevant_chunks(query_embedding = user_embedding, top_k= 10, user_id = user_id)
    
    # Step 2: Build prompt stage 1
    print("Stage 1 ....")
    stage_1_prompt = build_prompt_stage_1(user_input = user_input, retrieved_chunks = retrieved_texts)
    system_prompt_1 = "You are an intelligent assistant whose job is to deeply analyze and evaluate text data chunks extracted from various documents."
    
    # Step 3: Call OpenAI
    bot_response_stage_1 = call_gpt(system_prompt = system_prompt_1, user_prompt = stage_1_prompt, model = 'gpt-4o-mini')
    filtered_chunks = json.loads(bot_response_stage_1)
    print("---------------------------")
    print(f"1st stage response: \n {filtered_chunks}")
    
    final_chunks_for_stage_2 = fetch_filtered_text_chunks(filtered_chunks)
    
    #Step 4: Build prompt stage 2
    stage_2_prompt = build_prompt_stage_2(user_input = user_input, final_chunks = final_chunks_for_stage_2)
    system_prompt_2 = "You are EM Bot — an intelligent assistant created to support users with accurate and thoughtful answers related to the project 'EM' stands for 'Educational Missions'. This is a nonprofit initiative that aims to bring educational and recreational opportunities to underprivileged children in remote areas. Your primary responsibility is to answer user questions based on a curated set of information chunks extracted from documents related to this project. These chunks have already been pre-filtered and are considered highly relevant to the user's query."
    
    #Step 5: Call OpenAI
    bot_response_stage_2 = call_gpt(system_prompt = system_prompt_2, user_prompt = stage_2_prompt, model = 'gpt-4o-mini')

    # Step 5: Update history
    updated_history = (history + [(user_input, bot_response_stage_2)])[-3:]

    # if total_tokens > TOKEN_LIMIT:
    #     print("⚠️ Token limit exceeded! Chunking and summarizing chat history...")
    #     updated_history = process_history_chat(history = updated_history, source_type=f"{user_id}_conversation", user_id = user_id)

    return bot_response_stage_2, updated_history