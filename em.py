import streamlit as st
import mysql.connector
from hashlib import sha256
import re  # Regular expressions for validation

# Database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='sql12.freesqldatabase.com',
            user='sql12723269',
            password='TxAprekznd',  # Use empty password if default
            database='sql12723269'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Password validation function
def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r'\d', password):
        return "Password must contain at least one digit."
    return None

# Email validation function
def validate_email(email):
    email = email.lower()  # Convert to lowercase
    pattern = r'^[a-z0-9._-]+@gmail\.com$'
    if not re.match(pattern, email):
        return "Email must contain letters, numbers, periods, underscores, or dashes, and end with '@gmail.com'."
    return None

# Signup function with improved error handling
def signup(name, lastname, email, password):
    conn = get_db_connection()
    if conn:
        password_error = validate_password(password)
        if password_error:
            return password_error

        email_error = validate_email(email)
        if email_error:
            return email_error

        hashed_password = sha256(password.encode()).hexdigest()
        cursor = conn.cursor()

        try:
            query = "INSERT INTO employee_info (name, lastname, email, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, lastname, email, hashed_password))
            conn.commit()
            cursor.close()
            conn.close()
            st.session_state['authenticated'] = True
            st.session_state['user'] = email
            return "Signup Successful!"
        except mysql.connector.Error as err:
            conn.rollback()  # Rollback in case of error
            error_message = f"Error inserting into database: {err}"
            print(error_message)  # Log the error for debugging
            return error_message
    else:
        return "Failed to connect to the database."

# Login function
def login(email, password):
    conn = get_db_connection()
    if conn:
        hashed_password = sha256(password.encode()).hexdigest()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employee_info WHERE email=%s AND password=%s", (email, hashed_password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            st.session_state['authenticated'] = True
            st.session_state['user'] = email
            return "Login Successful!"
        else:
            return "Invalid Credentials!"
    else:
        return "Failed to connect to the database."

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None

# Streamlit UI
st.title("Employee Management System")

if st.session_state['authenticated']:
    st.markdown("""
    <style>
    </style>
    <p>This culture is more than just a set of values or a series of practices 
    it's the very essence of how employees interact, collaborate, and contribute to the company's success. A vibrant employee culture nurtures an environment where individuals feel valued, empowered, and motivated.

    In such a culture, transparency and open communication are paramount, fostering trust and ensuring that everyone is aligned with the organization’s goals and vision. It encourages diversity of thought and innovation, creating a space where every idea is considered and every contribution is recognized.

    A positive employee culture also emphasizes work-life balance, recognizing that personal well-being is integral to professional success. By supporting employees in achieving this balance, organizations not only enhance job satisfaction but also boost productivity and retention.

    Ultimately, a strong employee culture is a driving force behind a company's success. It attracts top talent, retains valuable employees, and cultivates a sense of belonging and purpose. By investing in and nurturing this culture, organizations lay the foundation for sustained growth and achievement.</p>
    <p>Feel free to explore the features and functionalities we offer.</p>
    """, unsafe_allow_html=True)

    if st.button("Logout"):
        st.session_state['authenticated'] = False
        st.experimental_rerun()

else:
    menu = ["Login", "Signup"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Signup":
        st.subheader("Signup Form")
        name = st.text_input("Name")
        lastname = st.text_input("Lastname")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Signup"):
            if password == confirm_password:
                message = signup(name, lastname, email, password)
                if "Successful" in message:
                    st.success(message)
                    st.experimental_rerun()
                else:
                    st.error(message)
            else:
                st.error("Passwords do not match!")

    elif choice == "Login":
        st.subheader("Login Form")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            message = login(email, password)
            if "Successful" in message:
                st.success(message)
                st.experimental_rerun()
            else:
                st.error(message)
