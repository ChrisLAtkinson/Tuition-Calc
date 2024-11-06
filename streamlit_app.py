import streamlit as st
import pandas as pd
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap

# Set page layout to wide for better visibility
st.set_page_config(layout="wide")

# Configure locale for currency formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

# Helper function to format numbers as currency
def format_currency(value):
    try:
        return locale.currency(value, grouping=True)
    except:
        return f"${value:,.2f}"

# Function to format input strings as currency
def format_input_as_currency(input_value):
    try:
        if not input_value:
            return ""
        input_value = input_value.replace(",", "").replace("$", "")
        value = float(input_value)
        return f"${value:,.2f}"
    except ValueError:
        return ""

# Streamlit App Start
st.title("Tuition Calculation Tool")

# Step 1: Enter a Custom Title for the Report
st.subheader("Step 1: Enter a Custom Title for the Report")
report_title = st.text_input("Enter a Custom Title for the Report", "2025-26 Tuition Projection")

# Step 2: Add Custom Grade Levels and Tuition Rates
st.subheader("Step 2: Add Custom Grade Levels and Tuition Rates")
num_grades = st.number_input("Number of Grade Levels", min_value=1, max_value=12, value=1, step=1)

# Initialize session state for storing inputs if not already set
if 'grades' not in st.session_state:
    st.session_state.grades = [f"Grade {i+1}" for i in range(num_grades)]
    st.session_state.num_students = [0] * num_grades
    st.session_state.current_tuition = [0.0] * num_grades
    st.session_state.adjusted_tuition = [0.0] * num_grades

# Adjust session state lists if num_grades has changed
if len(st.session_state.grades) != num_grades:
    st.session_state.grades = [f"Grade {i+1}" for i in range(num_grades)]
    st.session_state.num_students = [0] * num_grades
    st.session_state.current_tuition = [0.0] * num_grades
    st.session_state.adjusted_tuition = [0.0] * num_grades

# Collect input data for each grade
for i in range(num_grades):
    st.session_state.grades[i] = st.text_input(f"Grade Level {i+1} Name", st.session_state.grades[i])
    st.session_state.num_students[i] = st.number_input(
        f"Number of Students in {st.session_state.grades[i]}",
        min_value=0, step=1, value=st.session_state.num_students[i]
    )
    tuition_input = st.text_input(f"Current Tuition per Student in {st.session_state.grades[i]} ($)", "")
    formatted_tuition = format_input_as_currency(tuition_input)
    st.text(f"Formatted Tuition: {formatted_tuition}")
    st.session_state.current_tuition[i] = (
        float(formatted_tuition.replace(",", "").replace("$", "")) if formatted_tuition else 0.0
    )

# Build the DataFrame using session state variables for displaying data
tuition_data = {
    "Grade": st.session_state.grades,
    "Number of Students": st.session_state.num_students,
    "Current Tuition per Student": st.session_state.current_tuition,
    "Adjusted New Tuition per Student": st.session_state.adjusted_tuition
}
df = pd.DataFrame(tuition_data)

# Display the table with current values
st.subheader("Adjust Tuition by Grade Level")
for i, grade in enumerate(st.session_state.grades):
    st.session_state.adjusted_tuition[i] = st.number_input(
        f"Adjusted Tuition for {grade}",
        value=st.session_state.adjusted_tuition[i],
        min_value=0.0,
        step=0.01
    )

# Update the DataFrame based on session state adjustments
df["Adjusted New Tuition per Student"] = st.session_state.adjusted_tuition
df["Total Tuition for Grade"] = df["Number of Students"] * df["Adjusted New Tuition per Student"]

# Display the updated table
st.dataframe(df[["Grade", "Number of Students", "Current Tuition per Student", "Adjusted New Tuition per Student", "Total Tuition for Grade"]], use_container_width=True)

# Calculate totals and display the summary
total_current_tuition = sum([students * tuition for students, tuition in zip(st.session_state.num_students, st.session_state.current_tuition)])
total_new_tuition = sum(df["Total Tuition for Grade"])
st.write(f"**Total Current Tuition:** {format_currency(total_current_tuition)}")
st.write(f"**Total New Tuition:** {format_currency(total_new_tuition)}")

