import streamlit as st
from utils.supabase_client import get_supabase
import bcrypt

class CustomUser:
    def __init__(self, db_row):
        self.id = db_row.get('id')
        self.user_metadata = {"full_name": db_row.get('full_name')}

def login_user(email, password):
    try:
        supabase = get_supabase()
        # Direct DB query to pusers table
        response = supabase.table("pusers").select("*").eq("email", email).execute()
        if response.data and len(response.data) > 0:
            stored_user = response.data[0]
            stored_password = stored_user.get('password', '')
            
            # Check if the stored password looks like a valid bcrypt hash
            try:
                if stored_password.startswith('$2b$') or stored_password.startswith('$2a$'):
                    if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                        return CustomUser(stored_user)
                else:
                    # Fallback for legacy plain-text accounts during transition
                    if password == stored_password:
                        return CustomUser(stored_user)
            except:
                # If bcrypt check fails for any reason, try plain text
                if password == stored_password:
                    return CustomUser(stored_user)
                
        st.error("Invalid email or password")
        return None
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return None

def register_user(email, password, name):
    try:
        supabase = get_supabase()
        
        # Check if email is already taken
        existing = supabase.table("pusers").select("id").eq("email", email).execute()
        if existing.data and len(existing.data) > 0:
            st.error("Email already registered. Please switch to the Login tab.")
            return None
            
        # Hash the password for safety
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
        # Insert the new user directly into the pusers table
        response = supabase.table("pusers").insert({
            "email": email,
            "password": hashed_password,
            "full_name": name
        }).execute()
        
        if response.data and len(response.data) > 0:
            return CustomUser(response.data[0])
        return None
    except Exception as e:
        st.error(f"Registration failed: {str(e)}")
        return None

class DummyUser:
    def __init__(self):
        self.id = '00000000-0000-0000-0000-000000000000'
        self.user_metadata = {'full_name': 'Developer'}

def render_auth():
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>AI Interview Prep Coach 🎯</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<p style='text-align: center; color: gray;'>Welcome! Please login or register to start practicing.</p>", unsafe_allow_html=True)
        
        if st.button("🚀 Dev Mode: Bypass Login", use_container_width=True, type="secondary"):
            # Ensure Dummy user exists in DB so foreign keys don't break for interview history
            dummy = DummyUser()
            try:
                supabase = get_supabase()
                # Use upsert to create or update the dummy user
                supabase.table("pusers").upsert({
                    "id": dummy.id,
                    "email": "dev@example.com",
                    "password": "bypass_active",
                    "full_name": "Developer"
                }).execute()
            except:
                pass # Fail silently if DB is not ready, worst case history won't save
            
            st.session_state.authenticated = True
            st.session_state.user_data = dummy
            st.session_state.current_page = 'dashboard'
            st.rerun()
            
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["🔒 Login", "📝 Register"])
        
        with tab1:
            st.markdown("### Welcome Back")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Login", use_container_width=True):
                if email and password:
                    with st.spinner("Logging in..."):
                        clean_email = email.strip().replace('"', '').replace("'", "")
                        user = login_user(clean_email, password)
                        if user:
                            # If successful, set state and rerun
                            st.session_state.authenticated = True
                            st.session_state.user_data = user
                            st.session_state.current_page = 'dashboard'
                            st.rerun()
                else:
                    st.warning("Please enter email and password")
                    
        with tab2:
            st.markdown("### Create an Account")
            name = st.text_input("Full Name", key="reg_name")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_pass")
            
            if st.button("Register", use_container_width=True):
                if new_email and new_password and name:
                    with st.spinner("Registering..."):
                        clean_email = new_email.strip().replace('"', '').replace("'", "")
                        user = register_user(clean_email, new_password, name)
                        if user:
                            st.success("Registration successful! Please proceed to Login.")
                else:
                    st.warning("Please fill all fields")
