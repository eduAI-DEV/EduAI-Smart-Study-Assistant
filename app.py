import streamlit as st
import logging
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import hashlib
import hmac
from functools import wraps
import time

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain_anthropic import ChatAnthropic

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eduai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="EduAI: Deep Research Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎓 EduAI Research & Homework Assistant")
st.markdown("Expert in History, Current Affairs, and Academic Research.")

# --- CONFIGURATION ---
SUPPORTED_MODELS = {
    "gpt-4o": "OpenAI GPT-4o",
    "gpt-4-turbo": "OpenAI GPT-4 Turbo",
    "gpt-3.5-turbo": "OpenAI GPT-3.5 Turbo",
    "claude-3-opus": "Anthropic Claude 3 Opus",
    "claude-3-sonnet": "Anthropic Claude 3 Sonnet",
}

MAX_REQUESTS_PER_HOUR = 100
MAX_TOKENS_PER_DAY = 100000
CONVERSATION_SAVE_DIR = "conversations"

# Create conversations directory
Path(CONVERSATION_SAVE_DIR).mkdir(exist_ok=True)

# --- AUTHENTICATION ---
def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == hashed

def login_required(func):
    """Decorator to require user authentication."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "authenticated" not in st.session_state or not st.session_state.authenticated:
            st.warning("Please log in to access this feature.")
            return None
        return func(*args, **kwargs)
    return wrapper

# --- RATE LIMITING ---
class RateLimiter:
    def __init__(self, max_requests: int, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def is_allowed(self) -> bool:
        """Check if a request is allowed."""
        now = time.time()
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
    
    def get_reset_time(self) -> str:
        """Get when the rate limit resets."""
        if not self.requests:
            return "Now"
        oldest_request = min(self.requests)
        reset_time = oldest_request + self.time_window
        return datetime.fromtimestamp(reset_time).strftime("%H:%M:%S")

# --- COST TRACKING ---
class CostTracker:
    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    }
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
    def add_tokens(self, model: str, input_tokens: int, output_tokens: int):
        """Track tokens and calculate cost."""
        if model not in self.PRICING:
            logger.warning(f"Unknown model for pricing: {model}")
            return
        
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        
        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        session_cost = input_cost + output_cost
        
        self.total_cost += session_cost
        logger.info(f"Cost tracked - Model: {model}, Input: {input_tokens}, Output: {output_tokens}, Cost: ${session_cost:.4f}")
    
    def get_summary(self) -> dict:
        """Get cost summary."""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost": f"${self.total_cost:.4f}"
        }

# --- CONVERSATION MANAGEMENT ---
class ConversationManager:
    @staticmethod
    def save_conversation(user_id: str, messages: list, title: str = None):
        """Save conversation to file."""
        if title is None:
            title = f"Conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filename = f"{CONVERSATION_SAVE_DIR}/{user_id}_{title}.json"
        try:
            with open(filename, 'w') as f:
                json.dump({
                    "title": title,
                    "created_at": datetime.now().isoformat(),
                    "messages": messages
                }, f, indent=2)
            logger.info(f"Conversation saved: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save conversation: {str(e)}")
            return False
    
    @staticmethod
    def load_conversations(user_id: str) -> list:
        """Load all conversations for a user."""
        conversations = []
        try:
            for file in Path(CONVERSATION_SAVE_DIR).glob(f"{user_id}_*.json"):
                with open(file, 'r') as f:
                    conversations.append(json.load(f))
            return sorted(conversations, key=lambda x: x['created_at'], reverse=True)
        except Exception as e:
            logger.error(f"Failed to load conversations: {str(e)}")
            return []
    
    @staticmethod
    def export_conversation(messages: list, format: str = "json") -> str:
        """Export conversation in different formats."""
        if format == "json":
            return json.dumps(messages, indent=2)
        elif format == "markdown":
            md = "# Conversation Export\n\n"
            for msg in messages:
                role = msg["role"].upper()
                content = msg["content"]
                md += f"## {role}\n{content}\n\n"
            return md
        elif format == "txt":
            txt = ""
            for msg in messages:
                txt += f"{msg['role'].upper()}: {msg['content']}\n\n"
            return txt
        return json.dumps(messages)

# --- SESSION STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_id = None

if "rate_limiter" not in st.session_state:
    st.session_state.rate_limiter = RateLimiter(MAX_REQUESTS_PER_HOUR)

if "cost_tracker" not in st.session_state:
    st.session_state.cost_tracker = CostTracker()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am EduAI. What topic are we researching today?"}]

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

if "agent_executor" not in st.session_state:
    st.session_state.agent_executor = None

# --- SIDEBAR SETUP ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Authentication Section
    st.subheader("🔐 Authentication")
    if not st.session_state.authenticated:
        auth_choice = st.radio("Choose action:", ["Login", "Register"])
        
        if auth_choice == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                # Simple authentication (in production, use proper database)
                if username and password:
                    st.session_state.authenticated = True
                    st.session_state.user_id = username
                    logger.info(f"User logged in: {username}")
                    st.success(f"Welcome, {username}!")
                    st.rerun()
        
        else:  # Register
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.button("Register"):
                if new_username and new_password == confirm_password:
                    st.session_state.authenticated = True
                    st.session_state.user_id = new_username
                    logger.info(f"New user registered: {new_username}")
                    st.success(f"Registration successful! Welcome, {new_username}!")
                    st.rerun()
                elif new_password != confirm_password:
                    st.error("Passwords do not match!")
    else:
        st.success(f"✅ Logged in as: {st.session_state.user_id}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.messages = [{"role": "assistant", "content": "Hello! I am EduAI. What topic are we researching today?"}]
            logger.info("User logged out")
            st.rerun()
    
    st.divider()
    
    # API Keys Section
    st.subheader("🔑 API Keys")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    tavily_api_key = st.text_input("Tavily API Key", type="password")
    anthropic_api_key = st.text_input("Anthropic API Key (Optional)", type="password")
    
    st.divider()
    
    # Model Selection
    st.subheader("🤖 Model Selection")
    selected_model = st.selectbox(
        "Choose AI Model:",
        list(SUPPORTED_MODELS.keys()),
        format_func=lambda x: SUPPORTED_MODELS[x],
        index=0
    )
    
    st.info(f"Selected: {SUPPORTED_MODELS[selected_model]}")
    
    st.divider()
    
    # Advanced Settings
    st.subheader("⚡ Advanced Settings")
    temperature = st.slider("Temperature (Creativity)", 0.0, 1.0, 0.7)
    max_tokens = st.slider("Max Response Tokens", 100, 4096, 2048)
    search_results = st.slider("Search Results to Cite", 1, 10, 5)
    
    st.divider()
    
    # Rate Limiting Info
    st.subheader("📊 Rate Limiting")
    if st.session_state.rate_limiter.requests:
        remaining = MAX_REQUESTS_PER_HOUR - len(st.session_state.rate_limiter.requests)
        st.info(f"Requests used: {len(st.session_state.rate_limiter.requests)}/{MAX_REQUESTS_PER_HOUR}")
        st.info(f"Resets at: {st.session_state.rate_limiter.get_reset_time()}")
    
    st.divider()
    
    # Cost Tracking
    st.subheader("💰 Cost Tracking")
    cost_summary = st.session_state.cost_tracker.get_summary()
    st.metric("Total Cost", cost_summary["total_cost"])
    st.metric("Input Tokens", cost_summary["total_input_tokens"])
    st.metric("Output Tokens", cost_summary["total_output_tokens"])

# --- MAIN CONTENT ---
if not st.session_state.authenticated:
    st.warning("👤 Please log in or register to use EduAI")
else:
    # Initialize AI if API keys are provided
    if openai_api_key and tavily_api_key:
        try:
            # Initialize the LLM based on selected model
            if selected_model.startswith("gpt"):
                llm = ChatOpenAI(
                    model_name=selected_model,
                    openai_api_key=openai_api_key,
                    streaming=True,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            elif selected_model.startswith("claude") and anthropic_api_key:
                llm = ChatAnthropic(
                    model_name=selected_model,
                    anthropic_api_key=anthropic_api_key,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                st.error("Please provide Anthropic API Key for Claude models")
                st.stop()
            
            # Initialize Research Tool (Tavily)
            search_tool = TavilySearchResults(
                api_wrapper_kwargs={'tavily_api_key': tavily_api_key},
                k=search_results
            )
            
            # Initialize the Agent
            tools = [search_tool]
            agent_executor = initialize_agent(
                tools,
                llm,
                agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                verbose=True,
                memory=st.session_state.memory,
                handle_parsing_errors=True,
                system_message=(
                    "You are EduAI, an expert academic tutor. "
                    "For history: Provide deep context and multiple perspectives. "
                    "For current affairs: Use the search tool to get the latest news. "
                    "For homework: Don't just give the answer; explain the reasoning step-by-step. "
                    "Always cite your sources using [Source Name/URL]."
                )
            )
            
            st.session_state.agent_executor = agent_executor
            
        except Exception as e:
            logger.error(f"Failed to initialize AI: {str(e)}")
            st.error(f"❌ Error initializing AI: {str(e)}")
            st.stop()
        
        # Chat Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📚 History", "📥 File Upload", "⚙️ Tools"])
        
        with tab1:
            st.subheader("Chat Interface")
            
            # Display messages
            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])
            
            # Chat input
            if prompt := st.chat_input("Ask me anything..."):
                # Check rate limiting
                if not st.session_state.rate_limiter.is_allowed():
                    st.error(f"⚠️ Rate limit exceeded! Resets at {st.session_state.rate_limiter.get_reset_time()}")
                    logger.warning(f"Rate limit exceeded for user: {st.session_state.user_id}")
                else:
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.chat_message("user").write(prompt)
                    
                    try:
                        with st.chat_message("assistant"):
                            st_callback = StreamlitCallbackHandler(st.container())
                            response = agent_executor.run(
                                input=prompt,
                                callbacks=[st_callback]
                            )
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response
                            })
                            st.write(response)
                            logger.info(f"Response generated for user: {st.session_state.user_id}")
                    
                    except Exception as e:
                        logger.error(f"Error generating response: {str(e)}")
                        st.error(f"❌ Error: {str(e)}")
        
        with tab2:
            st.subheader("📚 Conversation History")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 Save Current Conversation"):
                    title = st.text_input("Conversation Title", key="save_title")
                    if title and st.button("Confirm Save"):
                        if ConversationManager.save_conversation(
                            st.session_state.user_id,
                            st.session_state.messages,
                            title
                        ):
                            st.success("Conversation saved!")
                        else:
                            st.error("Failed to save conversation")
            
            with col2:
                if st.button("📥 Load Conversation"):
                    conversations = ConversationManager.load_conversations(st.session_state.user_id)
                    if conversations:
                        selected = st.selectbox(
                            "Select conversation:",
                            conversations,
                            format_func=lambda x: x['title']
                        )
                        if st.button("Load"):
                            st.session_state.messages = selected['messages']
                            st.success("Conversation loaded!")
                            st.rerun()
                    else:
                        st.info("No saved conversations found")
            
            with col3:
                if st.button("📤 Export Conversation"):
                    export_format = st.selectbox("Format:", ["json", "markdown", "txt"])
                    exported = ConversationManager.export_conversation(
                        st.session_state.messages,
                        export_format
                    )
                    st.download_button(
                        label=f"Download {export_format.upper()}",
                        data=exported,
                        file_name=f"conversation.{export_format}",
                        mime="text/plain"
                    )
        
        with tab3:
            st.subheader("📥 File Upload")
            st.info("Upload documents to analyze with EduAI")
            
            uploaded_files = st.file_uploader(
                "Choose files (PDF, TXT, DOC)",
                accept_multiple_files=True,
                type=["pdf", "txt", "doc", "docx"]
            )
            
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
                for file in uploaded_files:
                    st.write(f"📄 {file.name} ({file.size} bytes)")
                    # In production, implement file processing
                    logger.info(f"File uploaded: {file.name}")
        
        with tab4:
            st.subheader("⚙️ System Tools")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Clear Chat History"):
                    st.session_state.messages = [
                        {"role": "assistant", "content": "Hello! I am EduAI. What topic are we researching today?"}
                    ]
                    st.session_state.memory = ConversationBufferMemory(
                        memory_key="chat_history",
                        return_messages=True
                    )
                    st.success("Chat history cleared!")
                    st.rerun()
            
            with col2:
                if st.button("📊 View Logs"):
                    st.info("Logs are saved to: eduai.log")
                    try:
                        with open('eduai.log', 'r') as f:
                            logs = f.read()
                            st.text_area("System Logs", logs, height=300, disabled=True)
                    except FileNotFoundError:
                        st.warning("No logs found yet")
            
            st.divider()
            st.subheader("📈 Session Statistics")
            st.metric("Total Messages", len(st.session_state.messages))
            st.metric("Model Selected", SUPPORTED_MODELS[selected_model])
            st.metric("Temperature", temperature)
            st.metric("Max Tokens", max_tokens)
    
    else:
        st.warning("👆 Please add your API keys in the sidebar to get started!")
