import streamlit as st
from sqlalchemy import create_engine, Column, String, Text, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd

# Database configuration
Base = declarative_base()

class Credential(Base):
    __tablename__ = 'credentials'
    
    website_name = Column(String(100), primary_key=True)
    website_link = Column(String(200))
    username = Column(String(50))
    password = Column(String(50))
    supervised_email = Column(String(100))
    supervised_phone = Column(String(20))
    auth_reference = Column(String(50))
    status = Column(String(20))
    description = Column(Text)

# Database connection
@st.cache_resource
def init_db():
    engine = create_engine(
        f"postgresql://{st.secrets['postgres']['PGUSER']}:{st.secrets['postgres']['PGPASSWORD']}"
        f"@{st.secrets['postgres']['PGHOST']}/{st.secrets['postgres']['PGDATABASE']}"
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

# Authentication
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        password = st.text_input("Enter Password:", type="password")
        if st.button("Login"):
            if password == st.secrets["APP_PASSWORD"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
        return False
    return True

# Custom CSS
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    margin: 10px 0;
    transition: 0.3s;
}
.card:hover {
    box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# Pages
def search_page():
    st.header("Advanced Search")
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            website_name = st.text_input("Website Name")
            supervised_email = st.text_input("Supervised Email")
        with col2:
            username = st.text_input("Username")
            supervised_phone = st.text_input("Supervised Phone Number")
        
        if st.form_submit_button("Search"):
            session = init_db()
            query = session.query(Credential)
            
            if website_name:
                query = query.filter(Credential.website_name.ilike(f"%{website_name}%"))
            if username:
                query = query.filter(Credential.username.ilike(f"%{username}%"))
            if supervised_email:
                query = query.filter(Credential.supervised_email.ilike(f"%{supervised_email}%"))
            if supervised_phone:
                query = query.filter(Credential.supervised_phone.ilike(f"%{supervised_phone}%"))
            
            results = query.all()
            session.close()
            
            if results:
                for cred in results:
                    st.markdown(f"""
                    <div class="card">
                        <h3>{cred.website_name}</h3>
                        <p>URL: <a href="{cred.website_link}">{cred.website_link}</a></p>
                        <p>Username: {cred.username}</p>
                        <p>Password: {cred.password}</p>
                        <p>Email: {cred.supervised_email}</p>
                        <p>Phone: {cred.supervised_phone}</p>
                        <p>Auth Reference: {cred.auth_reference}</p>
                        <p>Status: {cred.status}</p>
                        <p>Description: {cred.description}</p>
                        <div>
                            <button>Edit</button>
                            <button>Delete</button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No results found")

def data_entry_page():
    st.header("New Data Entry")
    with st.form("entry_form"):
        website_name = st.text_input("Website Name*", placeholder="Example Site")
        website_link = st.text_input("Website Link*", placeholder="https://example.com")
        username = st.text_input("Username*", placeholder="user123")
        password = st.text_input("Password*", type="password")
        supervised_email = st.text_input("Supervised Email", placeholder="user@example.com")
        supervised_phone = st.text_input("Supervised Phone Number", placeholder="+1234567890")
        auth_reference = st.text_input("Authentication Reference")
        status = st.selectbox("Status", ["Active", "Deactivated", "On Hold"])
        description = st.text_area("Description")
        
        if st.form_submit_button("Submit"):
            if not all([website_name, website_link, username, password]):
                st.error("Please fill all required fields (*)")
            else:
                session = init_db()
                new_cred = Credential(
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
                session.add(new_cred)
                session.commit()
                session.close()
                st.success("Entry added successfully!")

def data_table_page():
    st.header("All Records")
    session = init_db()
    credentials = session.query(Credential).all()
    session.close()
    
    if credentials:
        df = pd.DataFrame([{
            "Website Name": c.website_name,
            "Website Link": c.website_link,
            "Username": c.username,
            "Password": c.password,
            "Email": c.supervised_email,
            "Phone": c.supervised_phone,
            "Auth Reference": c.auth_reference,
            "Status": c.status,
            "Description": c.description
        } for c in credentials])
        
        edited_df = st.data_editor(df, num_rows="dynamic")
        
        if st.button("Save Changes"):
            session = init_db()
            for index, row in edited_df.iterrows():
                session.query(Credential).filter_by(website_name=row["Website Name"]).update({
                    "website_link": row["Website Link"],
                    "username": row["Username"],
                    "password": row["Password"],
                    "supervised_email": row["Email"],
                    "supervised_phone": row["Phone"],
                    "auth_reference": row["Auth Reference"],
                    "status": row["Status"],
                    "description": row["Description"]
                })
            session.commit()
            session.close()
            st.success("Changes saved!")
        
        st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="credentials.csv",
            mime="text/csv"
        )
    else:
        st.info("No records found")

# Main app
if check_password():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Search", "Data Entry", "Data Table"])
    
    if page == "Search":
        search_page()
    elif page == "Data Entry":
        data_entry_page()
    elif page == "Data Table":
        data_table_page()
