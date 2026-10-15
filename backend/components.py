from backend.state import ChatState
from backend.models import llm

def chat_node(state: ChatState) -> ChatState:
    messages = state['messages']
    response = llm.invoke(messages)
    
    return {'messages': [response]}
    