# LangGraph Chatbot

A conversational AI chatbot built using **LangGraph, LangChain, Streamlit, and SQLite**, featuring real-time response streaming, persistent conversation memory, and multi-threaded chat management.

## Features

- **AI-Powered Conversations:** Generate responses using a Large Language Model (LLM) integrated with LangChain.
- **Real-Time Streaming:** Display AI-generated responses progressively using Streamlit.
- **Persistent Memory:** Store conversation checkpoints in SQLite using LangGraph's `SqliteSaver`.
- **Multiple Conversations:** Maintain independent chat sessions using unique thread IDs.
- **Conversation History:** Retrieve and continue previous conversations.
- **Chat Management:** Create, rename, and delete conversations.
- **Interactive Interface:** User-friendly chat interface built with Streamlit.
- **Modular Architecture:** Separate frontend, graph workflow, state management, and LLM configuration.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| LangGraph | Stateful conversation workflow |
| LangChain | LLM integration |
| Streamlit | Interactive web interface |
| SQLite | Persistent conversation storage |
| UUID | Unique conversation identifiers |

## Project Structure

```text
LangGraph-Chatbot/
├── backend/
│   ├── __init__.py
│   ├── state.py
│   ├── models.py
│   ├── components.py
│   └── graph.py
├── frontend/
│   └── app.py
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── chatbot.db
```

*Note: The exact filenames may differ depending on your project structure. The `.env` and `chatbot.db` files should not be committed to Git.*

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/LangGraph-Chatbot.git
cd LangGraph-Chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and add your API key:

```env
OPENAI_API_KEY=your_openai_api_key
```

Never commit your `.env` file or expose API keys publicly.

### 5. Run the Application

```bash
streamlit run frontend/app.py
```

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

## How It Works

The application uses LangGraph to manage the conversation workflow and SQLite to persist conversation states.

```text
User Input (Streamlit)
        |
        v
Generate / Retrieve Thread ID
        |
        v
LangGraph Workflow
        |
        v
Chat Node
        |
        v
LangChain LLM
        |
        v
AI Response
        |
        v
Stream Response to Streamlit
        |
        v
Save Conversation State (SQLite)
```

### LangGraph Workflow

The workflow consists of a chat node connected between the `START` and `END` nodes.

```python
graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

workflow = graph.compile(checkpointer=checkpointer)
```

### Conversation State

Conversation messages are maintained using LangGraph's message reducer.

```python
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

The `add_messages` reducer merges new messages into the existing conversation history.

### Persistent Memory

SQLite-based checkpointing enables conversations to be stored and retrieved using their thread IDs.

```python
conn = sqlite3.connect(
    database="chatbot.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(conn=conn)
```

Each conversation is associated with a unique `thread_id`, allowing multiple independent chat sessions.

### Response Streaming

The application uses LangGraph's message streaming mode and Streamlit's `st.write_stream()` to display generated responses progressively.

```python
ai_message = st.write_stream(
    message_chunk.content
    for message_chunk, metadata in chatbot.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
        stream_mode="messages"
    )
)
```

## Future Improvements

- User authentication and authorization
- Search across conversation history
- Export conversations
- File upload and document-based question answering
- Retrieval-Augmented Generation (RAG)
- Cloud deployment

## License

This project is distributed under the terms of the license included in the `LICENSE` file.