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

# Function to generate a downloadable PDF report
def generate_pdf(report_title, df, total_current_tuition, total_new_tuition, avg_increase_percentage, tuition_assistance_ratio, strategic_items_df, summary_text):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title of the report
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, f"Report Title: {report_title}")

    # Summary details
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 80, f"Total Current Tuition: {format_currency(total_current_tuition)}")
    pdf.drawString(50, height - 100, f"Total New Tuition: {format_currency(total_new_tuition)}")
    pdf.drawString(50, height - 120, f"Average Tuition Increase Percentage: {avg_increase_percentage:.2f}%")
    pdf.drawString(50, height - 140, f"Tuition Assistance Ratio: {tuition_assistance_ratio:.2f}%")

    # Add the table for tuition by grade level
    pdf.drawString(50, height - 170, "Tuition by Grade Level:")
    row_y = height - 190
    pdf.setFont("Helvetica", 10)
    for i, row in df.iterrows():
        pdf.drawString(50, row_y, f"{row['Grade']}: {row['Number of Students']} students, "
                                  f"Current Tuition: {format_currency(row['Current Tuition per Student'])}, "
                                  f"Adjusted New Tuition: {format_currency(row['Adjusted New Tuition per Student'])}")
        row_y -= 15

    # Strategic Items Section with descriptions
    if not strategic_items_df.empty:
        row_y -= 20
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, row_y, "Strategic Items, Costs, and Descriptions:")
        row_y -= 20
        pdf.setFont("Helvetica", 10)
        for i, row in strategic_items_df.iterrows():
            pdf.drawString(50, row_y, f"{row['Strategic Item']}: {format_currency(row['Cost ($)'])}")
            row_y -= 15
            description_lines = textwrap.wrap(row['Description'], width=90)
            for line in description_lines:
                pdf.drawString(70, row_y, line)
                row_y -= 15

    # Add the calculation summary text
    row_y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, row_y, "Summary of Calculations:")
    row_y -= 20
    pdf.setFont("Helvetica", 10)
    for line in textwrap.wrap(summary_text, width=90):
        pdf.drawString(50, row_y, line)
        row_y -= 15

    # Finalize PDF
    pdf.save()
    buffer.seek(0)
    return buffer

# Streamlit App Start
st.title("Tuition Calculation Tool")

# Step 1: Enter a Custom Title for the Report
st.subheader("Step 1: Enter a Custom Title for the Report")
report_title = st.text_input("Enter a Custom Title for the Report", "2025-26 Tuition Projection")

# Step 2: Add Custom Grade Levels and Tuition Rates
st.subheader("Step 2: Add Custom Grade Levels and Tuition Rates")
grades = []
num_students = []
current_tuition = []
num_grades = st.number_input("Number of Grade Levels", min_value=1, max_value=12, value=1, step=1)

for i in range(num_grades):
    grade = st.text_input(f"Grade Level {i+1} Name", f"Grade {i+1}")
    students = st.number_input(f"Number of Students in {grade}", min_value=0, step=1, value=0)
    tuition_input = st.text_input(f"Current Tuition per Student in {grade} ($)", "")
    formatted_tuition = format_input_as_currency(tuition_input)
    st.text(f"Formatted Tuition: {formatted_tuition}")
    tuition = float(formatted_tuition.replace(",", "").replace("$", "")) if formatted_tuition else 0.0
    grades.append(grade)
    num_students.append(students)
    current_tuition.append(tuition)

# Initialize adjusted tuition in session state
if "adjusted_tuition" not in st.session_state:
    st.session_state.adjusted_tuition = [(tuition * 1.1) for tuition in current_tuition]

# Calculate Current and New Tuition Totals
total_current_tuition = sum([students * tuition for students, tuition in zip(num_students, current_tuition)])
total_new_tuition = sum([students * adjusted for students, adjusted in zip(num_students, st.session_state.adjusted_tuition)])

# Interactive Tuition Adjustment Table
st.subheader("Adjust Tuition by Grade Level")
tuition_data = {
    "Grade": grades,
    "Number of Students": num_students,
    "Current Tuition per Student": current_tuition,
    "Adjusted New Tuition per Student": st.session_state.adjusted_tuition
}
df = pd.DataFrame(tuition_data)

# Update tuition dynamically
for i in range(len(grades)):
    st.session_state.adjusted_tuition[i] = st.number_input(
        f"Adjusted Tuition for {grades[i]}",
        value=st.session_state.adjusted_tuition[i],
        min_value=0.0,
        step=0.01,
        key=f"adjusted_tuition_{i}"
    )

# Recalculate totals after adjustment
df["Adjusted New Tuition per Student"] = st.session_state.adjusted_tuition
df["Total Tuition for Grade"] = df["Number of Students"] * df["Adjusted New Tuition per Student"]
adjusted_total_tuition = df["Total Tuition for Grade"].sum()

# Display Updated Results
st.write(df[["Grade", "Number of Students", "Current Tuition per Student",
             "Adjusted New Tuition per Student", "Total Tuition for Grade"]])
st.write(f"**Adjusted Total Tuition:** {format_currency(adjusted_total_tuition)}")
st.write(f"**Difference from Target Total Tuition:** {format_currency(total_new_tuition - adjusted_total_tuition)}")

# Generate and download updated PDF report
strategic_items_df = pd.DataFrame({
    "Strategic Item": ["Sample Item"],  # Example
    "Cost ($)": [1000],
    "Description": ["Example Description"]
})

pdf_buffer = generate_pdf(
    report_title, df, total_current_tuition, adjusted_total_tuition,
    10.0,  # Example % increase
    5.0,   # Example assistance % ratio
    strategic_items_df,
    "Updated summary of tuition adjustment calculations."
)

st.download_button(
    label="Download Updated Report as PDF",
    data=pdf_buffer,
    file_name="adjusted_tuition_report.pdf",
    mime="application/pdf"
)
