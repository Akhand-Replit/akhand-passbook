# app.py
import streamlit as st
import psycopg2
from psycopg2 import sql

# Initialize connection
def init_connection():
    return psycopg2.connect(
        host=st.secrets["PGHOST"],
        database=st.secrets["PGDATABASE"],
        user=st.secrets["PGUSER"],
        password=st.secrets["PGPASSWORD"]
    )

conn = init_connection()

# Create table if not exists
def create_table():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                id SERIAL PRIMARY KEY,
                website_name VARCHAR(255) NOT NULL,
                website_link VARCHAR(255) NOT NULL,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                supervised_email VARCHAR(255),
                supervised_phone VARCHAR(255),
                auth_reference VARCHAR(255),
                status VARCHAR(50),
                description TEXT
            )
        """)
        conn.commit()

create_table()

# Authentication
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        st.title("Login")
        password = st.text_input("Enter Password", type="password")
        if st.button("Login"):
            if password == st.secrets["APP_PASSWORD"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
        st.stop()

# CRUD Operations
def search_records(search_term):
    with conn.cursor() as cur:
        query = sql.SQL("""
            SELECT * FROM credentials
            WHERE 
                website_name ILIKE %s OR
                website_link ILIKE %s OR
                username ILIKE %s OR
                password ILIKE %s OR
                supervised_email ILIKE %s OR
                supervised_phone ILIKE %s OR
                auth_reference ILIKE %s OR
                status ILIKE %s
        """)
        cur.execute(query, [f"%{search_term}%"]*8)
        return cur.fetchall()

def update_record(record_id, data):
    with conn.cursor() as cur:
        query = sql.SQL("""
            UPDATE credentials SET
                website_name = %s,
                website_link = %s,
                username = %s,
                password = %s,
                supervised_email = %s,
                supervised_phone = %s,
                auth_reference = %s,
                status = %s,
                description = %s
            WHERE id = %s
        """)
        cur.execute(query, (*data, record_id))
        conn.commit()

def delete_record(record_id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM credentials WHERE id = %s", (record_id,))
        conn.commit()

# Pages
def show_search_page():
    st.title("🔍 Advanced Search")
    
    search_term = st.text_input("Search across all fields (except description)")
    results = search_records(search_term) if search_term else []
    
    if results:
        cols = st.columns(3)
        for idx, row in enumerate(results):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"**{row[1]}**")
                    st.write(f"🔗 {row[2]}")
                    st.write(f"👤 {row[3]}")
                    st.write(f"🔑 {row[4][:10]}...")
                    st.write(f"📧 {row[5] or 'N/A'}")
                    st.write(f"📱 {row[6] or 'N/A'}")
                    st.write(f"🆔 {row[7] or 'N/A'}")
                    st.write(f"📌 {row[8] or 'N/A'}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✏️ Edit", key=f"edit_{row[0]}"):
                            st.session_state.edit_record = row
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_{row[0]}"):
                            delete_record(row[0])
                            st.rerun()
    
    if "edit_record" in st.session_state:
        with st.form("edit_form"):
            record = st.session_state.edit_record
            st.subheader("Edit Record")
            
            website_name = st.text_input("Website Name*", value=record[1])
            website_link = st.text_input("Website Link*", value=record[2])
            username = st.text_input("Username*", value=record[3])
            password = st.text_input("Password*", value=record[4])
            supervised_email = st.text_input("Supervised Email", value=record[5])
            supervised_phone = st.text_input("Supervised Phone", value=record[6])
            auth_reference = st.text_input("Auth Reference", value=record[7])
            status = st.selectbox("Status", ["Active", "Deactivated", "On hold"], 
                                index=["Active", "Deactivated", "On hold"].index(record[8]))
            description = st.text_area("Description", value=record[9])
            
            if st.form_submit_button("Update"):
                update_data = (
                    website_name, website_link, username, password,
                    supervised_email, supervised_phone, auth_reference,
                    status, description
                )
                update_record(record[0], update_data)
                del st.session_state.edit_record
                st.rerun()

def show_add_page():
    st.title("📝 Add New Credentials")
    
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        with col1:
            website_name = st.text_input("Website Name*")
            website_link = st.text_input("Website Link*")
            username = st.text_input("Username*")
            password = st.text_input("Password*")
        with col2:
            supervised_email = st.text_input("Supervised Email")
            supervised_phone = st.text_input("Supervised Phone")
            auth_reference = st.text_input("Authentication Reference")
            status = st.selectbox("Status", ["Active", "Deactivated", "On hold"])
        
        description = st.text_area("Description")
        
        if st.form_submit_button("Submit"):
            if not all([website_name, website_link, username, password]):
                st.error("Please fill required fields (*)")
            else:
                with conn.cursor() as cur:
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
                    st.success("Record added successfully!")
                    st.rerun()

# Main App
def main():
    check_password()
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Search", "Add New"])
    
    if page == "Search":
        show_search_page()
    else:
        show_add_page()

if __name__ == "__main__":
    main()
