import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import hashlib
import base64
import io

# --- Initialize session state variables ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ""

# --- User Authentication ---
users = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "analyst": hashlib.sha256("analyst123".encode()).hexdigest(),
    "viewer": hashlib.sha256("viewer123".encode()).hexdigest()
}

@st.cache_data

def verify_user(username, password):
    if username in users:
        return users[username] == hashlib.sha256(password.encode()).hexdigest()
    return False

# --- Login Form ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
            else:
                st.error("Invalid username or password")
    st.stop()

# --- Main Dashboard ---
st.title("📊 Interactive Data Visualization Dashboard")
st.sidebar.title(f"Welcome, {st.session_state.username}")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Data Preview")
    st.dataframe(df.head())

    # --- EDA ---
    st.subheader("Exploratory Data Analysis")
    st.write("Summary Statistics")
    st.dataframe(df.describe())

    st.write("Missing Values")
    st.dataframe(df.isnull().sum())

    st.write("Data Types")
    st.dataframe(df.dtypes)

    # --- Filtering & Sorting ---
    st.sidebar.subheader("🔍 Filter & Sort")
    for col in df.select_dtypes(include='object').columns:
        options = st.sidebar.multiselect(f"Filter {col}", df[col].unique())
        if options:
            df = df[df[col].isin(options)]

    for col in df.select_dtypes(include=['int', 'float']).columns:
        min_val, max_val = float(df[col].min()), float(df[col].max())
        selected_range = st.sidebar.slider(f"Filter {col}", min_val, max_val, (min_val, max_val))
        df = df[(df[col] >= selected_range[0]) & (df[col] <= selected_range[1])]

    st.sidebar.write("Sort by column")
    sort_col = st.sidebar.selectbox("Sort by", df.columns)
    sort_order = st.sidebar.radio("Order", ["Ascending", "Descending"])
    df = df.sort_values(by=sort_col, ascending=(sort_order == "Ascending"))

    st.subheader("Filtered Data")
    st.dataframe(df)

    # --- Visualizations ---
    st.subheader("📈 Visualizations")
    chart_type = st.selectbox("Select chart type", ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram"])
    numeric_cols = df.select_dtypes(include=['float', 'int']).columns.tolist()
    categorical_cols = df.select_dtypes(include='object').columns.tolist()

    if chart_type == "Bar Chart":
        x = st.selectbox("X-axis", categorical_cols)
        y = st.selectbox("Y-axis", numeric_cols)
        fig = px.bar(df, x=x, y=y)
        st.plotly_chart(fig)

    elif chart_type == "Line Chart":
        x = st.selectbox("X-axis", numeric_cols)
        y = st.selectbox("Y-axis", numeric_cols)
        fig = px.line(df, x=x, y=y)
        st.plotly_chart(fig)

    elif chart_type == "Scatter Plot":
        x = st.selectbox("X-axis", numeric_cols)
        y = st.selectbox("Y-axis", numeric_cols)
        fig = px.scatter(df, x=x, y=y, color=df[categorical_cols[0]] if categorical_cols else None)
        st.plotly_chart(fig)

    elif chart_type == "Histogram":
        x = st.selectbox("Column", numeric_cols)
        fig = px.histogram(df, x=x)
        st.plotly_chart(fig)

    # --- Download filtered data ---
    st.subheader("📥 Download Filtered Data")
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # B64 encode
    href = f'<a href="data:file/csv;base64,{b64}" download="filtered_data.csv">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)
else:
    st.info("Please upload a CSV file to begin analysis.")
