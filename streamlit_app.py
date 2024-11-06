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

    # Tuition by Grade Level
    pdf.drawString(50, height - 170, "Tuition by Grade Level:")
    row_y = height - 190
    pdf.setFont("Helvetica", 10)
    for i, row in df.iterrows():
        pdf.drawString(50, row_y, f"{row['Grade']}: {row['Number of Students']} students, "
                                  f"Current Tuition: {format_currency(row['Current Tuition per Student'])}, "
                                  f"Adjusted New Tuition: {format_currency(row['Adjusted New Tuition per Student'])}")
        row_y -= 15
        if row_y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            row_y = height - 50

    # Finalize PDF
    pdf.save()
    buffer.seek(0)
    return buffer

# Streamlit App Start
st.title("Tuition Calculation Tool")

# Custom Title
report_title = st.text_input("Enter a Custom Title for the Report", "2025-26 Tuition Projection")

# Grade Levels and Tuition Rates
num_grades = st.number_input("Number of Grade Levels", min_value=1, max_value=12, value=1, step=1)
if 'grades' not in st.session_state:
    st.session_state.grades = [f"Grade {i+1}" for i in range(num_grades)]
    st.session_state.num_students = [0] * num_grades
    st.session_state.current_tuition = [0.0] * num_grades
    st.session_state.adjusted_tuition = [0.0] * num_grades

for i in range(num_grades):
    st.session_state.grades[i] = st.text_input(f"Grade Level {i+1} Name", st.session_state.grades[i])
    st.session_state.num_students[i] = st.number_input(f"Number of Students in {st.session_state.grades[i]}", min_value=0, step=1, value=st.session_state.num_students[i])
    tuition_input = st.text_input(f"Current Tuition per Student in {st.session_state.grades[i]} ($)", "")
    formatted_tuition = format_currency(float(tuition_input.replace(",", "").replace("$", "")) if tuition_input else 0.0)
    st.session_state.current_tuition[i] = float(formatted_tuition.replace(",", "").replace("$", "")) if formatted_tuition else 0.0

tuition_data = {
    "Grade": st.session_state.grades,
    "Number of Students": st.session_state.num_students,
    "Current Tuition per Student": st.session_state.current_tuition,
    "Adjusted New Tuition per Student": st.session_state.adjusted_tuition
}
df = pd.DataFrame(tuition_data)

if st.button("Calculate New Tuition"):
    total_current_tuition = sum([students * tuition for students, tuition in zip(st.session_state.num_students, st.session_state.current_tuition)])
    total_new_tuition = total_current_tuition * (1 + final_tuition_increase / 100)
    new_tuition_per_student = [(tuition * (1 + final_tuition_increase / 100)) for tuition in st.session_state.current_tuition]
    st.session_state.adjusted_tuition = new_tuition_per_student
    tuition_assistance_ratio = (financial_aid / total_new_tuition) * 100 if total_new_tuition > 0 else 0.0

    # Interactive Adjustment Table
    for i, grade in enumerate(st.session_state.grades):
        adjusted_input = st.text_input(f"Adjusted Tuition for {grade}", value=format_currency(st.session_state.adjusted_tuition[i]))
        st.session_state.adjusted_tuition[i] = float(adjusted_input.replace(",", "").replace("$", ""))

    # Update DataFrame with formatted adjusted tuition values
    df["Adjusted New Tuition per Student"] = [format_currency(value) for value in st.session_state.adjusted_tuition]
    df["Total Tuition for Grade"] = [format_currency(row['Number of Students'] * row['Adjusted New Tuition per Student']) for _, row in df.iterrows()]

    # Display formatted DataFrame
    st.dataframe(df[["Grade", "Number of Students", "Current Tuition per Student", "Adjusted New Tuition per Student", "Total Tuition for Grade"]])

    # PDF download
    pdf_buffer = generate_pdf(report_title, df, total_current_tuition, adjusted_total_tuition, final_tuition_increase, tuition_assistance_ratio, strategic_items_df, "Summary of tuition adjustment calculations.")
    st.download_button("Download Report as PDF", data=pdf_buffer, file_name="tuition_report.pdf", mime="application/pdf")
