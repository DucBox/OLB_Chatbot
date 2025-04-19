import os
import xml.etree.ElementTree as ET
from src.utils.config import LOG_FILE_XML

def load_history_from_xml() -> list[tuple[str, str]]:
    """
    Loads conversation history from the XML file and returns it as a list of (user, bot) tuples.
    Always returns a list (empty if file not found or failed).
    """
    if not os.path.exists(LOG_FILE_XML):
        return []

    try:
        tree = ET.parse(LOG_FILE_XML)
        root = tree.getroot()
        history = []
        for conv in root.findall("conversation"):
            user_msg = conv.find("user").text or ""
            bot_msg = conv.find("bot").text or ""
            history.append((user_msg, bot_msg))
        return history
    except Exception as e:
        print(f"⚠️ Error loading chat history: {str(e)}")
        return []
    
def save_history_to_xml(history: list[tuple[str, str]]):
    """
    Saves the given conversation history to an XML file.
    Expects a list of (user, bot) tuples.
    """
    if not history:
        print("⚠️ Warning: empty history, nothing to save.")
        return

    root = ET.Element("chat_history")
    for user_msg, bot_msg in history:
        conversation = ET.SubElement(root, "conversation")
        user_elem = ET.SubElement(conversation, "user")
        user_elem.text = user_msg
        bot_elem = ET.SubElement(conversation, "bot")
        bot_elem.text = bot_msg

    tree = ET.ElementTree(root)
    os.makedirs(os.path.dirname(LOG_FILE_XML), exist_ok=True)
    tree.write(LOG_FILE_XML, encoding="utf-8", xml_declaration=True)

