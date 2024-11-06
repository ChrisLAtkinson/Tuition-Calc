import streamlit as st
import pandas as pd
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap

# Configure locale for currency formatting
locale.setlocale(locale.LC_ALL, '')

# Helper function to format numbers as currency
def format_currency(value):
    try:
        return locale.currency(value, grouping=True)
    except:
        return f"${value:,.2f}"

# PDF generation function
def generate_pdf(report_title, df, adjusted_total_tuition, target_total_tuition):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Report Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, report_title)

    # Adjusted Tuition Table
    pdf.setFont("Helvetica", 12)
    row_y = height - 100
    pdf.drawString(50, row_y, "Adjusted Tuition by Grade Level:")
    row_y -= 20
    pdf.setFont("Helvetica", 10)

    for _, row in df.iterrows():
        pdf.drawString(
            50,
            row_y,
            f"{row['Grade']}: {row['Number of Students']} students, "
            f"Current Tuition: {format_currency(row['Current Tuition per Student'])}, "
            f"Adjusted Tuition: {format_currency(row['Adjusted New Tuition per Student'])}"
        )
        row_y -= 15

    # Summary
    row_y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, row_y, "Summary:")
    row_y -= 20
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, row_y, f"Adjusted Total Tuition: {format_currency(adjusted_total_tuition)}")
    row_y -= 15
    pdf.drawString(50, row_y, f"Difference from Target Total Tuition: {format_currency(target_total_tuition - adjusted_total_tuition)}")

    pdf.save()
    buffer.seek(0)
    return buffer

# App title
st.title("Tuition Adjustment Tool")

# Input: Report title
report_title = st.text_input("Report Title", "2025-26 Tuition Projection")

# Input: Grade data
st.subheader("Grade Levels and Tuition Rates")
grades = []
num_students = []
current_tuition = []
if "tuition_data" not in st.session_state:
    st.session_state.tuition_data = pd.DataFrame(columns=[
        "Grade", "Number of Students", "Current Tuition per Student", "Adjusted New Tuition per Student"
    ])

num_grades = st.number_input("Number of Grades", min_value=1, max_value=12, value=1, step=1)

# Collect grade-specific data
for i in range(num_grades):
    grade = st.text_input(f"Grade {i + 1}", value=f"Grade {i + 1}")
    students = st.number_input(f"Number of Students in {grade}", min_value=0, value=0, step=1, key=f"students_{i}")
    tuition = st.number_input(
        f"Current Tuition per Student in {grade}",
        min_value=0.0,
        value=0.0,
        step=0.01,
        key=f"tuition_{i}"
    )
    adjusted_tuition = st.number_input(
        f"Adjusted Tuition for {grade}",
        value=tuition,
        min_value=0.0,
        step=0.01,
        key=f"adjusted_tuition_{i}"
    )

    # Append to data lists
    grades.append(grade)
    num_students.append(students)
    current_tuition.append(tuition)
    st.session_state.tuition_data = st.session_state.tuition_data.append(
        {
            "Grade": grade,
            "Number of Students": students,
            "Current Tuition per Student": tuition,
            "Adjusted New Tuition per Student": adjusted_tuition,
        },
        ignore_index=True,
    )

# Show the DataFrame
df = pd.DataFrame({
    "Grade": grades,
    "Number of Students": num_students,
    "Current Tuition per Student": current_tuition,
    "Adjusted New Tuition per Student": [st.session_state[f"adjusted_tuition_{i}"] for i in range(len(grades))]
})

df["Total Tuition for Grade"] = df["Number of Students"] * df["Adjusted New Tuition per Student"]

# Display table
st.subheader("Adjusted Tuition Table")
st.write(df)

# Calculate totals
adjusted_total_tuition = df["Total Tuition for Grade"].sum()
target_total_tuition = sum([students * tuition for students, tuition in zip(num_students, current_tuition)])

st.write(f"**Adjusted Total Tuition:** {format_currency(adjusted_total_tuition)}")
st.write(f"**Difference from Target Total Tuition:** {format_currency(target_total_tuition - adjusted_total_tuition)}")

# Generate PDF
if st.button("Generate PDF Report"):
    pdf_buffer = generate_pdf(report_title, df, adjusted_total_tuition, target_total_tuition)
    st.download_button(
        label="Download PDF Report",
        data=pdf_buffer,
        file_name="tuition_report.pdf",
        mime="application/pdf"
    )
