# app.py
import streamlit as st
import psycopg2
import pandas as pd
from streamlit.components.v1 import html

# Custom CSS for styling
def inject_custom_css():
    st.markdown("""
    <style>
        .card {
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin: 10px 0;
            transition: transform 0.2s;
            background-color: white;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        .stTextInput>div>div>input, .stSelectbox>div>div>select {
            border-radius: 20px;
            padding: 10px;
        }
        .stButton>button {
            width: 100%;
            border-radius: 20px;
            padding: 10px;
            background-color: #4CAF50;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=st.secrets["PGHOST"],
        database=st.secrets["PGDATABASE"],
        user=st.secrets["PGUSER"],
        password=st.secrets["PGPASSWORD"]
    )
    return conn

# Initialize database table
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS credentials (
            id SERIAL PRIMARY KEY,
            website_name VARCHAR(255) NOT NULL,
            website_link VARCHAR(255) NOT NULL,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            supervised_email VARCHAR(255),
            supervised_phone VARCHAR(20),
            auth_reference VARCHAR(255),
            status VARCHAR(50),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# Authentication
def authenticate():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("Login")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if password == st.secrets["APP_PASSWORD"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
        return False
    return True

# Page 1: Advanced Search
def show_search_page():
    st.title("🔍 Advanced Search")
    
    with st.form("search_form"):
        cols = st.columns(3)
        with cols[0]:
            website_name = st.text_input("Website Name")
        with cols[1]:
            username = st.text_input("Username")
        with cols[2]:
            status = st.selectbox("Status", ["", "Active", "Deactivated", "On hold"])
        
        search_clicked = st.form_submit_button("Search")
    
    if search_clicked:
        conn = get_db_connection()
        query = """
            SELECT * FROM credentials 
            WHERE 
                (website_name ILIKE %s OR %s = '') AND
                (username ILIKE %s OR %s = '') AND
                (status = %s OR %s = '')
        """
        params = (
            f"%{website_name}%", website_name,
            f"%{username}%", username,
            status, status
        )
        
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        
        if not df.empty:
            for _, row in df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="card">
                        <h3>{row['website_name']}</h3>
                        <p><b>URL:</b> {row['website_link']}</p>
                        <p><b>Username:</b> {row['username']}</p>
                        <p><b>Status:</b> {row['status']}</p>
                        <div style="margin-top: 10px;">
                            <button onclick="editEntry({row['id']})" style="margin-right: 10px;">Edit</button>
                            <button onclick="deleteEntry({row['id']})">Delete</button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No results found")

# Page 2: Add New Entry
def show_add_page():
    st.title("➕ Add New Entry")
    
    with st.form("add_form"):
        website_name = st.text_input("Website Name*")
        website_link = st.text_input("Website Link*")
        username = st.text_input("Username*")
        password = st.text_input("Password*", type="password")
        supervised_email = st.text_input("Supervised Email")
        supervised_phone = st.text_input("Supervised Phone Number")
        auth_reference = st.text_input("Authentication Reference")
        status = st.selectbox("Status*", ["Active", "Deactivated", "On hold"])
        description = st.text_area("Description")
        
        if st.form_submit_button("Submit"):
            if not all([website_name, website_link, username, password, status]):
                st.error("Please fill required fields (*)")
            else:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO credentials (
                        website_name, website_link, username, password,
                        supervised_email, supervised_phone, auth_reference,
                        status, description
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    website_name, website_link, username, password,
                    supervised_email, supervised_phone, auth_reference,
                    status, description
                ))
                conn.commit()
                cur.close()
                conn.close()
                st.success("Entry added successfully!")

# Page 3: View All Data
def show_view_page():
    st.title("📋 View All Data")
    
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM credentials", conn)
    conn.close()
    
    if not df.empty:
        edited_df = st.data_editor(df, hide_index=True)
        if st.button("Save Changes"):
            # Implement your update logic here
            st.success("Changes saved!")
        
        st.download_button(
            label="Download as CSV",
            data=df.to_csv().encode('utf-8'),
            file_name='credentials.csv',
            mime='text/csv'
        )
    else:
        st.info("No data available")

# Main App
def main():
    inject_custom_css()
    init_db()
    
    if not authenticate():
        return
    
    pages = {
        "Search": show_search_page,
        "Add New": show_add_page,
        "View All": show_view_page
    }
    
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(pages.keys()))
    
    pages[selection]()

if __name__ == "__main__":
    main()
