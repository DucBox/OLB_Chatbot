import os
import xml.etree.ElementTree as ET

def parse_history_xml(xml_path: str) -> list[tuple[str, str]]:
    """
    Reads file XML and returns list of (user, bot) pairs.
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        history = []
        for conv in root.findall("conversation"):
            user_msg = conv.find("user").text or "[Empty]"
            bot_msg = conv.find("bot").text or "[Empty]"
            history.append((user_msg, bot_msg))

        return history
    except Exception as e:
        print(f"❌ Error parsing XML {xml_path}: {e}")
        return []

def load_history_from_xml(path) -> list[tuple[str, str]]:
    """
    Loads conversation history from the XML file and returns it as a list of (user, bot) tuples.
    Always returns a list (empty if file not found or failed).
    """
    if not os.path.exists(path):
        return []

    try:
        tree = ET.parse(path)
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
    
def save_history_to_xml(history: list[tuple[str, str]], path):
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
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tree.write(path, encoding="utf-8", xml_declaration=True)

