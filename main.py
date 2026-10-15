
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from backend.graph import chatbot, retrieve_all_threads
import uuid

######################## Utility Functions ########################

def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def reset_chat():
    st.session_state["thread_id"] = generate_thread_id()
    st.session_state["message_history"] = []

def load_conversation(thread_id):
    state = chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )
    return state.values.get("messages", [])

def get_chat_title(thread_id):
    if thread_id in st.session_state["chat_titles"]:
        return st.session_state["chat_titles"][thread_id]

    messages = load_conversation(thread_id)

    for msg in messages:
        if isinstance(msg, HumanMessage):
            return " ".join(msg.content.split()[:5])

    return "New Chat"

def rename_chat(thread_id, new_title):
    if new_title.strip():
        st.session_state["chat_titles"][thread_id] = new_title.strip()

def delete_chat(thread_id):
    if thread_id in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].remove(thread_id)

    st.session_state["chat_titles"].pop(thread_id, None)

    chatbot.checkpointer.delete_thread(thread_id)

    if st.session_state["thread_id"] == thread_id:
        reset_chat()

######################## Session State ########################

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

if "chat_titles" not in st.session_state:
    st.session_state["chat_titles"] = {}

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

######################## Sidebar UI ########################

st.sidebar.title("LangGraph Chat")

if st.sidebar.button("New Chat", use_container_width=True):
    reset_chat()
    st.rerun()

st.sidebar.header("My Conversations")

for thread in st.session_state["chat_threads"][::-1]:

    title = get_chat_title(thread)

    col1, col2 = st.sidebar.columns([6, 1], gap="small")

    with col1:
        if st.button(
            title,
            key=f"chat_{thread}",
            use_container_width=True
        ):
            st.session_state["thread_id"] = thread

            messages = load_conversation(thread)
            temp_messages = []

            for msg in messages:
                if isinstance(msg, HumanMessage):
                    role = "user"
                elif isinstance(msg, AIMessage):
                    role = "assistant"
                else:
                    continue

                temp_messages.append({
                    "role": role,
                    "content": msg.content
                })

            st.session_state["message_history"] = temp_messages
            st.rerun()

    with col2:
        with st.popover("⋮"):

            st.markdown("**Manage Conversation**")

            new_title = st.text_input(
                "Rename",
                value=title,
                key=f"rename_{thread}"
            )

            if st.button(
                "Save Name",
                key=f"save_{thread}",
                use_container_width=True
            ):
                rename_chat(thread, new_title)
                st.rerun()

            if st.button(
                "Delete",
                key=f"delete_{thread}",
                use_container_width=True
            ):
                st.session_state["confirm_delete"] = thread

            if st.session_state.get("confirm_delete") == thread:
                st.warning("Delete this conversation?")

                if st.button(
                    "Confirm Delete",
                    key=f"confirm_{thread}",
                    use_container_width=True
                ):
                    delete_chat(thread)
                    st.session_state["confirm_delete"] = None
                    st.rerun()

######################## Config ########################

config = {
    "configurable": {
        "thread_id": st.session_state["thread_id"]
    }
}

######################## Chat History ########################

for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

######################## Chat Input ########################

user_input = st.chat_input("Type here ...")

if user_input:

    st.session_state["message_history"].append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):

        ai_message = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages"
            )
        )

    st.session_state["message_history"].append({
        "role": "assistant",
        "content": ai_message
    })

    add_thread(st.session_state["thread_id"])

