# app.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text, Column, String, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from streamlit.components.v1 import html
import hashlib

# Database configuration
Base = declarative_base()

class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    website_name = Column(String)
    website_link = Column(String)
    username = Column(String)
    password = Column(String)
    supervised_email = Column(String)
    supervised_phone = Column(String)
    auth_reference = Column(String)
    status = Column(String)
    description = Column(Text)

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)

def get_engine():
    return create_engine(
        f"postgresql://{st.secrets['postgres']['PGUSER']}:{st.secrets['postgres']['PGPASSWORD']}"
        f"@{st.secrets['postgres']['PGHOST']}/{st.secrets['postgres']['PGDATABASE']}"
    )

# Security
def check_password():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        with st.form("login"):
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit:
                if hashlib.sha256(password.encode()).hexdigest() == hashlib.sha256(st.secrets.APP_PASSWORD.encode()).hexdigest():
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password")
        st.stop()

# Common database operations
def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def search_entries(search_term):
    with get_session() as session:
        query = session.query(Entry).filter(
            Entry.website_name.ilike(f"%{search_term}%") |
            Entry.username.ilike(f"%{search_term}%") |
            Entry.supervised_email.ilike(f"%{search_term}%") |
            Entry.supervised_phone.ilike(f"%{search_term}%")
        )
        return query.all()

def delete_entry(entry_id):
    with get_session() as session:
        entry = session.query(Entry).get(entry_id)
        session.delete(entry)
        session.commit()

# Pages
def search_page():
    st.header("🔍 Advanced Search")
    search_term = st.text_input("Search")
    
    if search_term:
        results = search_entries(search_term)
        
        if results:
            for entry in results:
                card_html = f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; margin: 10px 0; 
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s;"
                    onmouseover="this.style.transform='scale(1.02)'" 
                    onmouseout="this.style.transform='scale(1)'">
                    <h3>{entry.website_name}</h3>
                    <p>🔗 <a href="{entry.website_link}">{entry.website_link}</a></p>
                    <p>👤 {entry.username}</p>
                    <p>🔑 {entry.password}</p>
                    <p>📧 {entry.supervised_email}</p>
                    <p>📞 {entry.supervised_phone}</p>
                    <p>🔍 {entry.auth_reference}</p>
                    <p>📊 {entry.status}</p>
                    <div style="display: flex; gap: 10px;">
                        <button onclick="parent.postMessage({{'action': 'edit', 'id': {entry.id}}}, '*')"
                            style="background: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px;">
                            Edit
                        </button>
                        <button onclick="parent.postMessage({{'action': 'delete', 'id': {entry.id}}}, '*')"
                            style="background: #f44336; color: white; border: none; padding: 8px 16px; border-radius: 4px;">
                            Delete
                        </button>
                    </div>
                </div>
                """
                html(card_html, height=300)
                
                # Handle actions
                if st.session_state.get('action') == 'delete' and st.session_state.get('entry_id') == entry.id:
                    delete_entry(entry.id)
                    st.success("Entry deleted successfully!")
                    del st.session_state.action
                    st.rerun()
        else:
            st.info("No results found")

def data_entry_page():
    st.header("✍️ Data Entry Form")
    with st.form("entry_form"):
        cols = st.columns(2)
        website_name = cols[0].text_input("Website Name*", key='website_name')
        website_link = cols[1].text_input("Website Link*", key='website_link')
        username = cols[0].text_input("Username*", key='username')
        password = cols[1].text_input("Password*", type="password", key='password')
        supervised_email = cols[0].text_input("Supervised Email", key='supervised_email')
        supervised_phone = cols[1].text_input("Supervised Phone Number", key='supervised_phone')
        auth_reference = cols[0].text_input("Authentication Reference", key='auth_reference')
        status = cols[1].selectbox("Status", ["Active", "Deactivated", "On Hold"], key='status')
        description = st.text_area("Description", key='description')
        
        if st.form_submit_button("Submit"):
            if not all([website_name, website_link, username, password]):
                st.error("Please fill all required fields (*)")
            else:
                with get_session() as session:
                    entry = Entry(
                        website_name=website_name,
                        website_link=website_link,
                        username=username,
                        password=password,
                        supervised_email=supervised_email,
                        supervised_phone=supervised_phone,
                        auth_reference=auth_reference,
                        status=status,
                        description=description
                    )
                    session.add(entry)
                    session.commit()
                    st.success("Entry added successfully!")

def data_table_page():
    st.header("📊 Data Table View")
    with get_session() as session:
        df = pd.read_sql(session.query(Entry).statement, session.bind)
    
    if not df.empty:
        edited_df = st.data_editor(df, num_rows="dynamic")
        
        # Handle edits
        if not df.equals(edited_df):
            changes = edited_df.compare(df)
            with get_session() as session:
                for idx in changes.index:
                    entry_id = idx[0]
                    field = idx[1].split('_')[1]
                    new_value = changes.loc[idx].iloc[0]
                    
                    entry = session.query(Entry).get(entry_id)
                    setattr(entry, field, new_value)
                session.commit()
                st.success("Changes saved!")
        
        st.download_button(
            "Download CSV",
            df.to_csv(index=False),
            "data.csv",
            "text/csv"
        )
    else:
        st.info("No data available")

# Main app
def main():
    check_password()
    st.title("🔒 Password Manager Pro")
    
    pages = {
        "🔍 Search": search_page,
        "✍️ Data Entry": data_entry_page,
        "📊 Data Table": data_table_page
    }
    
    page = st.sidebar.radio("Navigation", list(pages.keys()))
    pages[page]()

if __name__ == "__main__":
    init_db()
    main()
