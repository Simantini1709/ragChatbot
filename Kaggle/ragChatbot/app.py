"""
Streamlit Web UI for RAG Chatbot
Professional interface for enterprise documentation Q&A
"""

import streamlit as st
import sys
import os
from typing import List, Dict
import tempfile
from io import BytesIO

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from src.chatbot import RAGChatbot
from src.embedding_manager import EmbeddingManager
from src.vector_store import VectorStore
from src.retriever import Retriever
from src.llm_chain import LLMChain
from src.mongodb_manager import MongoDBManager

# Audio recording component
try:
    from audiorecorder import audiorecorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False

# OpenAI for Whisper API
from openai import OpenAI

# Page configuration
st.set_page_config(
    page_title="Enterprise RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
    }
    .bot-message {
        background-color: #f5f5f5;
        border-left: 5px solid #4caf50;
    }
    .source-tag {
        background-color: #fff3cd;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        margin: 0.25rem;
        display: inline-block;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_chatbot():
    """Initialize chatbot components (cached for performance)"""
    try:
        # Initialize components
        embedding_manager = EmbeddingManager()
        vector_store = VectorStore()

        # Connect to existing Pinecone index
        vector_store.create_index()

        retriever = Retriever(embedding_manager, vector_store)
        llm_chain = LLMChain()

        # Create chatbot (only needs retriever and llm_chain)
        chatbot = RAGChatbot(
            retriever=retriever,
            llm_chain=llm_chain
        )

        return chatbot, vector_store
    except Exception as e:
        st.error(f"Error initializing chatbot: {e}")
        return None, None


@st.cache_resource
def initialize_mongodb():
    """Initialize MongoDB connection (cached for performance)"""
    try:
        # Get MongoDB URI from environment or Streamlit secrets
        mongodb_uri = os.getenv("MONGODB_URI") or st.secrets.get("MONGODB_URI")

        if not mongodb_uri:
            st.warning("⚠️ MongoDB not configured. Chat history will not be saved.")
            return None

        mongodb_manager = MongoDBManager(connection_string=mongodb_uri)
        return mongodb_manager

    except Exception as e:
        st.warning(f"⚠️ MongoDB connection failed: {e}. Chat history will not be saved.")
        return None


def transcribe_audio(audio_bytes, filename="audio.wav") -> str:
    """Transcribe audio using OpenAI Whisper API"""
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Determine file extension from filename
        ext = os.path.splitext(filename)[1] if filename else ".wav"
        if not ext:
            ext = ".wav"

        # Save audio bytes to a temporary file with correct extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        # Transcribe using Whisper API
        with open(temp_audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"  # You can make this configurable
            )

        # Clean up temp file
        os.unlink(temp_audio_path)

        return transcript.text

    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return None


def display_message(role: str, content: str, sources: List[str] = None):
    """Display a chat message with styling"""
    css_class = "user-message" if role == "user" else "bot-message"
    icon = "🧑" if role == "user" else "🤖"

    st.markdown(f"""
        <div class="chat-message {css_class}">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                <strong>{"You" if role == "user" else "AI Assistant"}</strong>
            </div>
            <div style="margin-left: 2.5rem;">
                {content}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Display sources if available
    if sources and len(sources) > 0:
        st.markdown("**📚 Sources:**")
        cols = st.columns(min(len(sources), 3))
        for idx, source in enumerate(sources):
            with cols[idx % 3]:
                st.markdown(f'<span class="source-tag">{source}</span>', unsafe_allow_html=True)


def main():
    """Main application"""

    # Header
    st.title("🤖 Enterprise RAG Chatbot")
    st.markdown("*Intelligent documentation assistant powered by AI*")
    st.divider()

    # Initialize MongoDB
    if 'mongodb' not in st.session_state:
        st.session_state.mongodb = initialize_mongodb()

    # User Authentication
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
        st.session_state.user_logged_in = False

    # Login UI
    if not st.session_state.user_logged_in:
        st.info("👤 Please login to access chat history")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.subheader("🔐 User Login")
                user_id = st.text_input(
                    "User ID / Email",
                    placeholder="Enter your unique ID or email",
                    help="This will be used to save and retrieve your chat history"
                )
                name = st.text_input(
                    "Display Name (optional)",
                    placeholder="How should we address you?"
                )
                submitted = st.form_submit_button("Login", use_container_width=True)

                if submitted and user_id:
                    st.session_state.user_id = user_id.strip()
                    st.session_state.user_logged_in = True

                    # Create or update user in MongoDB
                    if st.session_state.mongodb:
                        st.session_state.mongodb.create_user(
                            user_id=st.session_state.user_id,
                            name=name if name else user_id
                        )

                    st.success(f"✅ Welcome, {name if name else user_id}!")
                    st.rerun()

        st.stop()  # Stop here if not logged in

    # Display logged in user info
    st.success(f"👤 Logged in as: **{st.session_state.user_id}**")

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []

        # Load chat history from MongoDB if available
        if st.session_state.mongodb and st.session_state.user_id:
            try:
                history = st.session_state.mongodb.get_chat_history(
                    user_id=st.session_state.user_id,
                    limit=50
                )

                # Convert MongoDB history to session state format
                for msg in history:
                    st.session_state.messages.append({
                        "role": msg["role"],
                        "content": msg["content"],
                        "sources": msg.get("sources", [])
                    })

                if len(history) > 0:
                    st.info(f"📜 Loaded {len(history)} previous messages")

            except Exception as e:
                st.warning(f"Could not load chat history: {e}")

    if 'chatbot' not in st.session_state:
        with st.spinner("Initializing AI chatbot..."):
            chatbot, vector_store = initialize_chatbot()
            if chatbot:
                st.session_state.chatbot = chatbot
                st.session_state.vector_store = vector_store
                st.success("✅ Chatbot initialized successfully!")
            else:
                st.error("❌ Failed to initialize chatbot. Please check your configuration.")
                st.stop()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Configuration
        st.subheader("Retrieval Settings")
        top_k = st.slider(
            "Number of context chunks",
            min_value=1,
            max_value=20,
            value=5,
            help="How many similar document chunks to retrieve"
        )

        temperature = st.slider(
            "Response creativity",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="0 = Factual, 1 = Creative"
        )

        # Search filters
        st.subheader("🔍 Search Filters")
        search_mode = st.selectbox(
            "Search mode",
            ["All Documents", "By Document Type", "By Category"],
            help="Filter search scope"
        )

        filter_value = None
        if search_mode == "By Document Type":
            filter_value = st.selectbox(
                "Document type",
                ["markdown", "pdf", "json"]
            )
        elif search_mode == "By Category":
            filter_value = st.selectbox(
                "Category",
                ["blog", "help", "other"]
            )

        # Advanced options
        with st.expander("🔧 Advanced Options"):
            show_sources = st.checkbox("Show source citations", value=True)
            show_relevance = st.checkbox("Show relevance scores", value=False)
            enable_history = st.checkbox("Enable conversation memory", value=True)

        st.divider()

        # Statistics
        st.subheader("📊 Database Stats")
        if st.session_state.vector_store:
            try:
                stats = st.session_state.vector_store.get_stats()
                if stats:
                    st.metric("Total Vectors", f"{stats.get('total_vector_count', 0):,}")
                    st.metric("Dimensions", stats.get('dimension', 'N/A'))
                else:
                    st.info("Stats unavailable")
            except:
                st.warning("Could not fetch stats")

        st.divider()

        # Actions
        st.subheader("🎬 Actions")

        if st.button("🗑️ Clear Chat History", use_container_width=True):
            # Clear from session state
            st.session_state.messages = []

            # Clear from MongoDB
            if st.session_state.mongodb and st.session_state.user_id:
                try:
                    deleted_count = st.session_state.mongodb.clear_user_history(st.session_state.user_id)
                    st.success(f"✅ Cleared {deleted_count} messages from database")
                except Exception as e:
                    st.error(f"Error clearing database: {e}")

            # Reset chatbot conversation
            if hasattr(st.session_state.chatbot, 'reset_conversation'):
                st.session_state.chatbot.reset_conversation()

            st.rerun()

        if st.button("🚪 Logout", use_container_width=True):
            # Clear session state
            st.session_state.user_logged_in = False
            st.session_state.user_id = None
            st.session_state.messages = []
            st.rerun()

        if st.button("🔄 Reset Settings", use_container_width=True):
            st.rerun()

    # Main chat interface
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("💬 Chat")

        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                display_message(
                    role=message["role"],
                    content=message["content"],
                    sources=message.get("sources", [])
                )

    with col2:
        st.subheader("💡 Quick Tips")

        st.info("""
        **How to use:**
        1. Type your question below
        2. Adjust settings in sidebar
        3. Get AI-powered answers
        4. Review source citations
        """)

        st.success("""
        **Example questions:**
        - What are the system requirements?
        - How do I get started?
        - What's the pricing model?
        - How does authentication work?
        """)

        st.warning("""
        **Pro tips:**
        - Be specific in your questions
        - Use filters for targeted search
        - Check sources for accuracy
        - Enable memory for follow-ups
        """)

        # Metrics
        st.divider()
        st.subheader("📈 Session Metrics")
        st.metric("Messages", len(st.session_state.messages))
        st.metric("User Queries", len([m for m in st.session_state.messages if m["role"] == "user"]))

    # Audio upload section (compact, at bottom)
    st.divider()

    # Audio file uploader (single row, minimal)
    audio_file = st.file_uploader(
        "Audio",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
        help="🎤 Upload audio file to transcribe your question",
        key="audio_uploader",
        label_visibility="collapsed"
    )

    # Handle audio upload
    if audio_file is not None:
        st.divider()
        audio_col1, audio_col2 = st.columns([2, 1])

        with audio_col1:
            st.audio(audio_file)
            st.caption(f"📎 {audio_file.name}")

        with audio_col2:
            st.write("")  # Spacing
            if st.button("📝 Transcribe & Ask", use_container_width=True, type="primary"):
                with st.spinner("🎧 Transcribing audio..."):
                    # Get audio bytes
                    audio_bytes = audio_file.read()

                    # Transcribe
                    transcribed_text = transcribe_audio(audio_bytes, audio_file.name)

                    if transcribed_text:
                        st.success(f"✅ Transcribed: *{transcribed_text}*")
                        # Store transcription to be processed
                        st.session_state.pending_question = transcribed_text
                        st.rerun()

    # Check for pending transcribed question
    if 'pending_question' in st.session_state:
        user_input = st.session_state.pending_question
        del st.session_state.pending_question
    else:
        # Chat input (must be at root level, not in columns)
        user_input = st.chat_input("Ask me anything about the documentation...")

    if user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "sources": []
        })

        # Save user message to MongoDB
        if st.session_state.mongodb and st.session_state.user_id:
            try:
                st.session_state.mongodb.save_message(
                    user_id=st.session_state.user_id,
                    role="user",
                    content=user_input,
                    sources=[]
                )
            except Exception as e:
                st.warning(f"Could not save message to database: {e}")

        # Generate response
        with st.spinner("🤔 Thinking..."):
            try:
                # Determine search method based on filters
                if search_mode == "By Document Type" and filter_value:
                    answer = st.session_state.chatbot.search_doc_type(
                        question=user_input,
                        doc_type=filter_value,
                        top_k=top_k
                    )
                    sources = []
                elif search_mode == "By Category" and filter_value:
                    answer = st.session_state.chatbot.search_category(
                        question=user_input,
                        category=filter_value,
                        top_k=top_k
                    )
                    sources = []
                else:
                    # Standard search with sources
                    if show_sources:
                        answer, sources = st.session_state.chatbot.ask_with_sources(
                            question=user_input,
                            top_k=top_k
                        )
                        # Extract just filenames from paths
                        sources = [s.split('/')[-1] for s in sources]
                    else:
                        answer = st.session_state.chatbot.ask(
                            question=user_input,
                            top_k=top_k,
                            temperature=temperature
                        )
                        sources = []

                # Add bot response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources if show_sources else []
                })

                # Save bot response to MongoDB
                if st.session_state.mongodb and st.session_state.user_id:
                    try:
                        st.session_state.mongodb.save_message(
                            user_id=st.session_state.user_id,
                            role="assistant",
                            content=answer,
                            sources=sources if show_sources else []
                        )
                    except Exception as e:
                        st.warning(f"Could not save response to database: {e}")

                # Rerun to display new messages
                st.rerun()

            except Exception as e:
                error_msg = f"Error generating response: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "sources": []
                })
                st.rerun()

    # Footer
    st.divider()
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            Built with ❤️ using OpenAI, Anthropic Claude, Pinecone & Streamlit<br>
            <a href="https://github.com/Simantini1709/ragChatbot" target="_blank">View on GitHub</a>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
