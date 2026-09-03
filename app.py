import streamlit as st
import time
import os
from datetime import datetime
from auth.auth_manager import AuthManager
from jarvis.memory import Memory
from jarvis.prompt_controller import PromptController
from jarvis.gemini_engine import GeminiEngine
from config.settings import Settings
from utils.voice_input import listen
from utils.export_chat import export_txt, export_pdf
import base64
from PIL import Image
import io

try:
    from streamlit_mic_recorder import speech_to_text
except ImportError:
    speech_to_text = None

if "login" not in st.session_state:
    st.session_state.login = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []


if st.session_state.current_chat_id not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat_id] = {
        "name": "New Chat",
        "messages": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }



st.set_page_config("JARVIS AI", page_icon="🤖", layout="centered")


st.markdown("""
<style>
    /* Cosmic Background with Animated Particles */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Orbitron:wght@400;500;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, 
            #0f0c29 0%, 
            #302b63 25%, 
            #24243e 50%, 
            #0f0c29 75%, 
            #302b63 100%);
        background-size: 400% 400%;
        animation: gradientFlow 15s ease infinite;
    }
    
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Animated particles in background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, rgba(255,255,255,0.3), transparent),
            radial-gradient(3px 3px at 40px 70px, rgba(255,255,255,0.2), transparent),
            radial-gradient(1px 1px at 90px 40px, rgba(255,255,255,0.4), transparent),
            radial-gradient(2px 2px at 130px 80px, rgba(255,255,255,0.2), transparent),
            radial-gradient(3px 3px at 160px 120px, rgba(255,255,255,0.3), transparent);
        background-size: 200px 200px;
        animation: float 20s linear infinite;
        z-index: -1;
    }
    
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        100% { transform: translateY(-200px) rotate(360deg); }
    }
    
    /* Futuristic Card Design */
    .card {
        background: rgba(16, 18, 27, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255, 255, 255, 0.1), 
            transparent);
        transition: 0.5s;
    }
    
    .card:hover::before {
        left: 100%;
    }
    
    /* Glassmorphism Effects */
    .glass {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    /* Neon User Message */
    .user-message {
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.2) 0%, 
            rgba(118, 75, 162, 0.2) 100%);
        color: #fff;
        padding: 18px;
        border-radius: 20px;
        margin: 12px 0;
        border-top-right-radius: 8px;
        max-width: 80%;
        margin-left: auto;
        border-left: 4px solid #667eea;
        position: relative;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    
    .user-message::before {
        content: '👤';
        position: absolute;
        left: -40px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.2em;
    }
    
    /* Holographic AI Message */
    .ai-message {
        background: linear-gradient(135deg, 
            rgba(26, 26, 46, 0.2) 0%, 
            rgba(22, 33, 62, 0.2) 100%);
        color: #fff;
        padding: 18px;
        border-radius: 20px;
        margin: 12px 0;
        border-top-left-radius: 8px;
        max-width: 80%;
        margin-right: auto;
        border-right: 4px solid #00d4ff;
        position: relative;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
        animation: hologram 2s infinite alternate;
    }
    
    @keyframes hologram {
        0% { border-right-color: #00d4ff; }
        100% { border-right-color: #667eea; }
    }
    
    .ai-message::before {
        content: '🤖';
        position: absolute;
        right: -40px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.2em;
    }
    
    /* Futuristic Buttons */
    .stButton > button {
        background: linear-gradient(135deg, 
            #667eea 0%, 
            #764ba2 50%, 
            #667eea 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 15px;
        font-weight: 600;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        background-size: 200% 200%;
        animation: gradientShift 3s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 
            0 10px 30px rgba(102, 126, 234, 0.4),
            0 0 20px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255, 255, 255, 0.2), 
            transparent);
        transition: 0.5s;
    }
    
    .stButton > button:hover::after {
        left: 100%;
    }
    
    /* Special Button Styles */
    .voice-btn {
        background: linear-gradient(135deg, 
            #FF416C 0%, 
            #FF4B2B 100%) !important;
    }
    
    .logout-btn {
        background: linear-gradient(135deg, 
            #FF416C 0%, 
            #FF4B2B 50%, 
            #FF416C 100%) !important;
        animation: dangerPulse 2s ease infinite !important;
    }
    
    @keyframes dangerPulse {
        0%, 100% { box-shadow: 0 0 0 rgba(255, 65, 108, 0.4); }
        50% { box-shadow: 0 0 20px rgba(255, 65, 108, 0.8); }
    }
    
    /* Futuristic Input Fields */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 12px 20px;
        font-size: 14px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        background: rgba(255, 255, 255, 0.08);
    }
    
    /* Cyberpunk Title */
    .title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, 
            #667eea, 
            #00d4ff, 
            #764ba2, 
            #667eea);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 2px;
        text-shadow: 
            0 0 10px rgba(102, 126, 234, 0.5),
            0 0 20px rgba(0, 212, 255, 0.3);
        animation: titleGlow 3s ease infinite;
    }
    
    @keyframes titleGlow {
        0%, 100% { text-shadow: 0 0 10px rgba(102, 126, 234, 0.5), 0 0 20px rgba(0, 212, 255, 0.3); }
        50% { text-shadow: 0 0 20px rgba(102, 126, 234, 0.8), 0 0 40px rgba(0, 212, 255, 0.5); }
    }
    
    /* Welcome Card with Holographic Effect */
    .welcome-card {
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.1) 0%, 
            rgba(118, 75, 162, 0.1) 100%);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 40px;
        text-align: center;
        margin: 30px auto;
        border: 1px solid rgba(255, 255, 255, 0.1);
        max-width: 600px;
        position: relative;
        overflow: hidden;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .welcome-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, 
            transparent, 
            rgba(255, 255, 255, 0.03), 
            transparent);
        transform: rotate(45deg);
        animation: shine 3s infinite linear;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }
    
    /* Futuristic Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(16, 18, 27, 0.5);
        padding: 8px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Status Indicator */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #00ff88;
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 10px #00ff88;
        animation: statusPulse 2s infinite;
    }
    
    @keyframes statusPulse {
        0%, 100% { box-shadow: 0 0 10px #00ff88; }
        50% { box-shadow: 0 0 20px #00ff88; }
    }
    
    /* Floating Animation */
    @keyframes floatUp {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .floating {
        animation: floatUp 3s ease-in-out infinite;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #764ba2, #667eea);
    }
    
    /* Typing Indicator */
    .typing-indicator {
        display: inline-block;
        width: 60px;
        height: 30px;
        position: relative;
    }
    
    .typing-indicator span {
        position: absolute;
        width: 8px;
        height: 8px;
        background: #667eea;
        border-radius: 50%;
        animation: typing 1.4s infinite;
    }
    
    .typing-indicator span:nth-child(1) { left: 0; animation-delay: 0s; }
    .typing-indicator span:nth-child(2) { left: 15px; animation-delay: 0.2s; }
    .typing-indicator span:nth-child(3) { left: 30px; animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-10px); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .title {
            font-size: 2.5rem;
        }
        
        .user-message, .ai-message {
            max-width: 90%;
            margin: 8px 0;
        }
        
        .card {
            padding: 20px;
            margin: 10px 0;
        }
    }
</style>
""", unsafe_allow_html=True)

auth = AuthManager()


if not st.session_state.login:
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 class="title floating">🤖 JARVIS AI</h1>
            <p style="color: rgba(255,255,255,0.7); margin-top: -20px;">Your Personal Artificial Intelligence Companion</p>
            <div style="margin: 20px 0;">
                <span class="status-indicator"></span>
                <span style="color: #00ff88; font-size: 0.9em;">System Online</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        
        st.markdown("""
        <div class="welcome-card floating">
            <h2 style="color: white; margin-bottom: 15px;">🚀 Welcome to JARVIS</h2>
            <p style="color: rgba(255,255,255,0.8); margin-bottom: 10px;">
                Experience the future of AI assistance with advanced features and intuitive interface.
            </p>
            <div style="display: flex; justify-content: center; gap: 20px; margin-top: 25px;">
                <div style="text-align: center;">
                    <div style="font-size: 1.5em;">🎯</div>
                    <div style="font-size: 0.9em; color: rgba(255,255,255,0.7);">Smart AI</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5em;">🎤</div>
                    <div style="font-size: 0.9em; color: rgba(255,255,255,0.7);">Voice Input</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5em;">💾</div>
                    <div style="font-size: 0.9em; color: rgba(255,255,255,0.7);">Memory</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
       
        tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 New Registration"])
        
        with tab1:
            
            st.markdown("<h3 style='color: white; margin-bottom: 20px;'>Access Your Dashboard</h3>", unsafe_allow_html=True)
            
            username = st.text_input("email", key="login_user", 
                                    placeholder="Enter your email")
            password = st.text_input("Password", type="password", key="login_pass",
                                    placeholder="Enter your password")
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("🚀 Login", use_container_width=True, key="login_btn"):
                    if auth.login(username, password):
                        st.session_state.login = True
                        st.session_state.current_user = username
                        st.success("Access Granted! Initializing JARVIS...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Authentication Failed! Check credentials.")
            with col_b:
                if st.button("🔄 Reset", use_container_width=True, type="secondary"):
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            
            st.markdown("<h3 style='color: white; margin-bottom: 20px;'>Create New Account</h3>", unsafe_allow_html=True)
            
            new_user = st.text_input("Choose Username", key="reg_user",
                                    placeholder="Select unique username")
            new_pass = st.text_input("Choose Password", type="password", key="reg_pass",
                                    placeholder="Create strong password")
            confirm_pass = st.text_input("Confirm Password", type="password", key="confirm_pass",
                                        placeholder="Re-enter password")
            
            if st.button("✨ Register Now", use_container_width=True, key="reg_btn"):
                if new_pass != confirm_pass:
                    st.error("Passwords do not match!")
                elif auth.register(new_user, new_pass):
                    st.success("Registration Successful! You can now login.")
                else:
                    st.error("Username already exists. Try another.")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Footer with futuristic design
        st.markdown("""
        <div style="text-align: center; margin-top: 40px; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.9em;">
                🔐 Powered by Advanced Security Protocols | ⚡ Built with Streamlit & Gemini AI
            </p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.8em; margin-top: 10px;">
                © 2025 JARVIS AI Systems | Version 2.1.0
            </p>
        </div>
        """, unsafe_allow_html=True)


else:
    
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>⚙️ Control Panel</h2>", unsafe_allow_html=True)
        
        
        st.markdown(f"""
        <div class='card'>
            <div style='text-align: center;'>
                <h3>👤 {st.session_state.current_user}</h3>
                <p style='color: rgba(255,255,255,0.7);'>Active Session</p>
                <div style='margin: 10px 0;'>
                    <span class='status-indicator'></span>
                    <span style='color: #00ff88; font-size: 0.9em;'>Online</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        

        st.markdown("<h3>💬 Chats</h3>", unsafe_allow_html=True)
        
        if st.button("🆕 create Chat", use_container_width=True):
            st.session_state.current_chat_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.all_chats[st.session_state.current_chat_id] = {
                "name": f"Chat {len(st.session_state.all_chats)+1}",
                "messages": [],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.chat_history = []
            st.rerun()

        
        for chat_id, chat_data in st.session_state.all_chats.items():
            if st.button(chat_data["name"], key=f"chat_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.session_state.chat_history = chat_data["messages"]
                st.rerun()
        
        
        role = st.selectbox(
            "🎭 Select Assistant Role",
            ["Assistant", "Tutor", "Coding Assistant", "Career Mentor"],
            index=0
        )
        
       
        role_descriptions = {
            "Assistant": "General purpose assistant",
            "Tutor": "Educational and learning support",
            "Coding Assistant": "Programming and development help",
            "Career Mentor": "Career guidance and advice"
        }
        st.caption(f"📝 {role_descriptions[role]}")
        
        
        st.markdown("### 💾 Export Chat")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 PDF", use_container_width=True, key="pdf_btn", 
                        help="Export chat as PDF document"):
                try:
                    memory = Memory()
                    export_pdf(memory.get_history())
                    st.success("✅ PDF exported successfully!")
                except Exception as e:
                    st.error(f"Export failed: {str(e)}")
        with col2:
            if st.button("📝 TXT", use_container_width=True, key="txt_btn",
                        help="Export chat as text file"):
                try:
                    memory = Memory()
                    export_txt(memory.get_history())
                    st.success("✅ TXT exported successfully!")
                except Exception as e:
                    st.error(f"Export failed: {str(e)}")
        
        
        if st.button("🗑️ Clear Chat History", use_container_width=True,
                    help="Delete all chat history"):
            try:
                memory = Memory()
                memory.clear()
                st.session_state.chat_history = []
                # Also clear current chat in all_chats
                if st.session_state.current_chat_id in st.session_state.all_chats:
                    st.session_state.all_chats[st.session_state.current_chat_id]["messages"] = []
                st.success("✅ Chat history cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Clear failed: {str(e)}")
        
       
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn", 
                    type="primary", help="End current session"):
            st.session_state.login = False
            st.session_state.current_user = ""
            st.session_state.chat_history = []
            st.success("Logged out successfully!")
            time.sleep(1)
            st.rerun()
    
    
    st.markdown(f"<h1 class='title'>🤖 JARVIS - {role}</h1>", unsafe_allow_html=True)
    
    
    try:
        settings = Settings()
        engine = GeminiEngine(settings.load_api_key())
        memory = Memory()
        prompt_controller = PromptController(role)
    except Exception as e:
        st.error(f"Failed to initialize JARVIS: {str(e)}")
        if st.button("🔄 Retry Initialization"):
            st.rerun()
        st.stop()
    
   
    chat_container = st.container()
    with chat_container:
        history = st.session_state.chat_history
        if not history:
            st.markdown("""
            <div class="welcome-card" style="max-width: 800px; margin: 40px auto;">
                <h3 style="color: white; text-align: center;">✨ Start a Conversation</h3>
                <p style="color: rgba(255,255,255,0.8); text-align: center;">
                    Ask me anything! I'm here to help as your {role}.<br>
                    Try using voice input or type your message below.
                </p>
                <div style="display: flex; justify-content: center; gap: 20px; margin-top: 25px;">
                    <div style="text-align: center;">
                        <div style="font-size: 2em;">💬</div>
                        <div style="font-size: 0.9em; color: rgba(255,255,255,0.7);">Chat</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2em;">🎤</div>
                        <div style="font-size: 0.9em; color: rgba(255,255,255,0.7);">Voice</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2em;">⚡</div>
                        <div style="font-size: 0.9em; color: rgba(255,255,255,0.7);">Fast</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in history:
                if msg['role'] == 'user':
                    st.markdown(f"<div class='user-message'>{msg['message']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='ai-message'>{msg['message']}</div>", unsafe_allow_html=True)
    
    
    st.markdown("<br><br>", unsafe_allow_html=True)  
    
    uploaded_file = st.file_uploader("📎 Upload a text file (optional)")
    file_content = ""
    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8")
        st.markdown(f"**File content detected ({uploaded_file.name}):**")
        st.text(file_content)
    

    input_container = st.container()
    with input_container:
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.chat_input(
                f"Ask JARVIS as your {role}...",
                key="chat_input"
            )
        
        with col2:
            if speech_to_text is not None:
                voice_text = speech_to_text(
                    language="en",
                    start_prompt="🎤",
                    stop_prompt="⏹️",
                    just_once=True,
                    use_container_width=True,
                    key="browser_voice_input"
                )
                if voice_text:
                    st.session_state.voice_input = voice_text
                    st.rerun()
            elif st.button("🎤", key="voice_btn", use_container_width=True,
                           help="Use voice input"):
                with st.spinner("🎤 Listening..."):
                    try:
                        voice_text = listen()
                        if voice_text:
                            st.session_state.voice_input = voice_text
                            st.rerun()
                    except Exception as e:
                        st.error(f"Voice input failed: {str(e)}")
    
    
    if "voice_input" in st.session_state and st.session_state.voice_input:
        user_input = st.session_state.voice_input
        del st.session_state.voice_input
    
    if user_input and not st.session_state.is_processing:
        st.session_state.is_processing = True
        
        try:
            
            if file_content:
                user_input = f"{user_input}\n\n[File content]\n{file_content}"
            
           
            memory.add("user", user_input)
            st.session_state.chat_history.append({"role": "user", "message": user_input})
            
            
            st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)
       
            prompt = prompt_controller.build_prompt(user_input, memory)
            
     
            response_placeholder = st.empty()
            full_response = ""
            
            
            response_placeholder.markdown("""
            <div class='ai-message'>
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            
            for chunk in engine.stream(prompt):
                full_response += chunk
                response_placeholder.markdown(f"<div class='ai-message'>{full_response}</div>", unsafe_allow_html=True)
            
            
            memory.add("assistant", full_response)
            st.session_state.chat_history.append({"role": "assistant", "message": full_response})
            
            
            if st.session_state.current_chat_id in st.session_state.all_chats:
                st.session_state.all_chats[st.session_state.current_chat_id]["messages"] = st.session_state.chat_history
            
        except Exception as e:
            st.error(f"Error processing request: {str(e)}")
        finally:
            st.session_state.is_processing = False
            st.rerun()
