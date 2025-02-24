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
/* Previous CSS styles remain the same */
</style>
""", unsafe_allow_html=True)

def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# Edit/Delete functions (from previous implementation)
# [Keep the edit_form and delete_record functions here]

# Search Page (from previous implementation)
# [Keep the search_page function here]

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
