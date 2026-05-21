# Simple in-memory conversation storage

conversation_history = []


def add_message(role, content):

    conversation_history.append({
        "role": role,
        "content": content
    })


def get_recent_messages(limit=6):

    return conversation_history[-limit:]