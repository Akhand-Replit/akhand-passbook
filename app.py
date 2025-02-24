import streamlit as st
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
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
    try:
        engine = create_engine(
            f"postgresql://{st.secrets['postgres']['PGUSER']}:{st.secrets['postgres']['PGPASSWORD']}"
            f"@{st.secrets['postgres']['PGHOST']}/{st.secrets['postgres']['PGDATABASE']}"
        )
        Base.metadata.create_all(engine)
        return sessionmaker(bind=engine)
    except KeyError as e:
        st.error(f"Missing database configuration: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Database connection error: {e}")
        st.stop()

# Authentication
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        # Add title here
        st.title("Akhand Passbook")
        st.write("**Access all of the accounts & passwords**")
    if not st.session_state.authenticated:
        password = st.text_input("Enter Password:", type="password")
        if st.button("Login"):
            try:
                if password == st.secrets["APP_PASSWORD"]:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password")
            except KeyError:
                st.error("Password not configured in secrets")
        return False
    return True

# Custom CSS
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 15px 0;
    transition: 0.3s;
    background: white;
    border: 1px solid #e0e0e0;
}
.card:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    transform: translateY(-2px);
}
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}
.card-title {
    margin: 0;
    color: #2c3e50;
    font-size: 1.2rem;
}
.card-content p {
    margin: 8px 0;
    color: #34495e;
}
.button-group {
    margin-top: 15px;
    display: flex;
    gap: 10px;
}
.status-active { color: #27ae60; }
.status-deactivated { color: #e74c3c; }
.status-onhold { color: #f1c40f; }
</style>
""", unsafe_allow_html=True)

def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# Edit Record Form
def edit_form(cred):
    with st.form(key=f"edit_{cred.website_name}"):
        st.write("### Edit Record")
        new_data = {
            "website_name": st.text_input("Website Name", value=cred.website_name),
            "website_link": st.text_input("Website Link", value=cred.website_link),
            "username": st.text_input("Username", value=cred.username),
            "password": st.text_input("Password", value=cred.password, type="password"),
            "supervised_email": st.text_input("Email", value=cred.supervised_email),
            "supervised_phone": st.text_input("Phone", value=cred.supervised_phone),
            "auth_reference": st.text_input("Auth Reference", value=cred.auth_reference),
            "status": st.selectbox("Status", ["Active", "Deactivated", "On Hold"], 
                                index=["Active", "Deactivated", "On Hold"].index(cred.status)),
            "description": st.text_area("Description", value=cred.description)
        }
        
        if st.form_submit_button("Save Changes"):
            Session = init_db()
            session = Session()
            try:
                session.query(Credential).filter_by(website_name=cred.website_name).update(new_data)
                session.commit()
                st.success("Record updated successfully!")
                session.close()
                st.rerun()
            except Exception as e:
                session.rollback()
                st.error(f"Error updating record: {e}")
            finally:
                session.close()

# Delete Record
def delete_record(website_name):
    Session = init_db()
    session = Session()
    try:
        session.query(Credential).filter_by(website_name=website_name).delete()
        session.commit()
        st.success("Record deleted successfully!")
        st.rerun()
    except Exception as e:
        session.rollback()
        st.error(f"Error deleting record: {e}")
    finally:
        session.close()

# Search Page
def search_page():
    st.header("Advanced Search")
    with st.form(key="search_form"):
        col1, col2 = st.columns(2)
        with col1:
            website_name = st.text_input("Website Name")
            supervised_email = st.text_input("Supervised Email")
        with col2:
            username = st.text_input("Username")
            supervised_phone = st.text_input("Supervised Phone Number")
        
        if st.form_submit_button("Search"):
            Session = init_db()
            session = Session()
            try:
                query = session.query(Credential)
                
                filters = {
                    "website_name": website_name,
                    "username": username,
                    "supervised_email": supervised_email,
                    "supervised_phone": supervised_phone
                }
                
                for field, value in filters.items():
                    if value:
                        query = query.filter(getattr(Credential, field).ilike(f"%{value}%"))
                
                st.session_state.search_results = query.all()
            finally:
                session.close()
    
    if 'search_results' in st.session_state and st.session_state.search_results:
        for cred in st.session_state.search_results:
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">{cred.website_name}</h3>
                        <span class="status-{cred.status.lower()}">● {cred.status}</span>
                    </div>
                    <div class="card-content">
                        <p>URL: <a href="{cred.website_link}" target="_blank">{cred.website_link}</a></p>
                        <p>Username: {cred.username}</p>
                        <p>Password: {cred.password}</p>
                        <p>Email: {cred.supervised_email or 'N/A'}</p>
                        <p>Phone: {cred.supervised_phone or 'N/A'}</p>
                        <p>Auth Reference: {cred.auth_reference or 'N/A'}</p>
                        <p>Description: {cred.description or 'N/A'}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 6])
                with col1:
                    if st.button(f"Edit {cred.website_name}", key=f"edit_{cred.website_name}"):
                        st.session_state.editing = cred.website_name
                with col2:
                    if st.button(f"Delete {cred.website_name}", key=f"delete_{cred.website_name}"):
                        delete_record(cred.website_name)
                
                if 'editing' in st.session_state and st.session_state.editing == cred.website_name:
                    edit_form(cred)
                    if st.button("Cancel Edit"):
                        del st.session_state.editing
                        st.rerun()

# Data Entry Page
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
                Session = init_db()
                session = Session()
                try:
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
                    st.success("Entry added successfully!")
                except Exception as e:
                    session.rollback()
                    st.error(f"Error saving entry: {e}")
                finally:
                    session.close()

# Data Table Page
def data_table_page():
    st.header("All Records")
    Session = init_db()
    session = Session()
    try:
        credentials = session.query(Credential).all()
        
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
                try:
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
                    st.success("Changes saved!")
                except Exception as e:
                    session.rollback()
                    st.error(f"Error saving changes: {e}")
            
            st.download_button(
                label="Download CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="credentials.csv",
                mime="text/csv"
            )
        else:
            st.info("No records found")
    finally:
        session.close()

# Main app
if check_password():
    logout_button()
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Search", "Data Entry", "Data Table"])
    
    if page == "Search":
        search_page()
    elif page == "Data Entry":
        data_entry_page()
    elif page == "Data Table":
        data_table_page()
