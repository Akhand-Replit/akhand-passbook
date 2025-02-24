import streamlit as st

# Custom CSS for modern UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    :root {
        --primary: #6366f1;
        --secondary: #4f46e5;
        --background: #f8fafc;
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: var(--background);
    }
    
    .card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
        border: 1px solid #e2e8f0;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .card-description {
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    
    .gradient-header {
        background: linear-gradient(45deg, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .logout-btn {
        background: #ef4444 !important;
        color: white !important;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: opacity 0.2s ease;
    }
    
    .logout-btn:hover {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Authentication function
def check_password():
    """Returns `True` if the user entered the correct password."""
    def password_entered():
        if "PASSWORD" in st.secrets and "password" in st.session_state:
            if st.session_state["password"] == st.secrets.PASSWORD:
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store the password
            else:
                st.session_state["password_correct"] = False

    # Add title and description
    st.title("Akhand Passbook")
    st.markdown("**Access all of the accounts & Password**")
    # First run: show password input and login button
    if "password_correct" not in st.session_state:
        with st.form(key="login_form"):
            st.text_input(
                "Password", 
                type="password", 
                key="password", 
                placeholder="Enter your access code"
            )
            if st.form_submit_button("Login"):
                password_entered()
        return False

    # Incorrect password: show input again with error and login button
    elif not st.session_state["password_correct"]:
        with st.form(key="retry_form"):
            st.text_input(
                "Password", 
                type="password", 
                key="password", 
                placeholder="Try again"
            )
            if st.form_submit_button("Login"):
                password_entered()
        st.error("Incorrect password. Please try again.")
        return False

    # Correct password: return True to proceed
    else:
        return True

# Main app logic - SINGLE CHECK
if check_password():
    # Sidebar components
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Log Out", key="logout_btn"):
            st.session_state["password_correct"] = False
            st.rerun()

    # Main content
    st.title("Akhand Unified Portal")
    st.markdown('<h2 class="gradient-header">Application Gateway</h2>', unsafe_allow_html=True)
    
    # First row of cards
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">Akhand Data</div>
            <div class="card-description">Access Voter Data</div>
            <a href="https://akhand.streamlit.app/" target="_blank" style="text-decoration:none;">
                <button style="
                    background: linear-gradient(45deg, #6366f1, #8b5cf6);
                    color: white;
                    border: none;
                    padding: 0.75rem 1.5rem;
                    border-radius: 8px;
                    cursor: pointer;
                    width: 100%;
                    font-weight: 600;
                    transition: opacity 0.2s ease;
                ">
                    Launch App
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">Akhand People/div>
            <div class="card-description">Selected People Database</div>
            <a href="https://akhand-selected-people.streamlit.app/" target="_blank" style="text-decoration:none;">
                <button style="
                    background: linear-gradient(45deg, #10b981, #059669);
                    color: white;
                    border: none;
                    padding: 0.75rem 1.5rem;
                    border-radius: 8px;
                    cursor: pointer;
                    width: 100%;
                    font-weight: 600;
                    transition: opacity 0.2s ease;
                ">
                    Launch App
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row of cards
    col3, col4 = st.columns(2, gap="large")
    
    with col3:
        st.markdown("""
        <div class="card">
            <div class="card-title">Passbook Application</div>
            <div class="card-description">Access your passbook and accounts history</div>
            <a href="https://akhand-passbook.streamlit.app/" target="_blank" style="text-decoration:none;">
                <button style="
                    background: linear-gradient(45deg, #f59e0b, #d97706);
                    color: white;
                    border: none;
                    padding: 0.75rem 1.5rem;
                    border-radius: 8px;
                    cursor: pointer;
                    width: 100%;
                    font-weight: 600;
                    transition: opacity 0.2s ease;
                ">
                    Launch App
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="card">
            <div class="card-title">Coming Soon</div>
            <div class="card-description">Various Feature coming soon</div>
            <a href="#" target="_blank" style="text-decoration:none;">
                <button style="
                    background: linear-gradient(45deg, #8b5cf6, #7c3aed);
                    color: white;
                    border: none;
                    padding: 0.75rem 1.5rem;
                    border-radius: 8px;
                    cursor: pointer;
                    width: 100%;
                    font-weight: 600;
                    transition: opacity 0.2s ease;
                ">
                    Launch App
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("ℹ️ Applications will open in new browser tabs • v1.1.0")
    st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
