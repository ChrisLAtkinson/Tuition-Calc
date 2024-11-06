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
if "tuition_data" not in st.session_state:
    st.session_state.tuition_data = pd.DataFrame(columns=[
        "Grade", "Number of Students", "Current Tuition per Student", "Adjusted New Tuition per Student"
    ])

num_grades = st.number_input("Number of Grade Levels", min_value=1, max_value=12, value=1, step=1)

new_rows = []
for i in range(num_grades):
    grade = st.text_input(f"Grade Level {i+1} Name", f"Grade {i+1}", key=f"grade_{i}")
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
    new_rows.append({
        "Grade": grade,
        "Number of Students": students,
        "Current Tuition per Student": tuition,
        "Adjusted New Tuition per Student": adjusted_tuition,
    })

st.session_state.tuition_data = pd.concat([st.session_state.tuition_data, pd.DataFrame(new_rows)], ignore_index=True)

# Step 3: Display Tuition Data
df = st.session_state.tuition_data.copy()
df["Total Tuition for Grade"] = df["Number of Students"] * df["Adjusted New Tuition per Student"]

st.subheader("Tuition Adjustment Table")
st.write(df)

# Step 4: Summary and Calculations
total_current_tuition = df["Number of Students"] * df["Current Tuition per Student"]
total_adjusted_tuition = df["Total Tuition for Grade"].sum()

st.write(f"**Adjusted Total Tuition:** {format_currency(total_adjusted_tuition)}")
st.write(f"**Difference from Current Tuition Total:** {format_currency(total_current_tuition.sum() - total_adjusted_tuition)}")

# Step 5: Generate PDF Report
if st.button("Generate PDF Report"):
    pdf_buffer = generate_pdf(
        report_title,
        df,
        total_current_tuition.sum(),
        total_adjusted_tuition,
        0,  # Replace with actual percentage if applicable
        0,  # Replace with tuition assistance ratio if applicable
        pd.DataFrame(),  # Replace with strategic items DataFrame if applicable
        "Summary of tuition adjustment calculations."
    )
    st.download_button(
        label="Download PDF Report",
        data=pdf_buffer,
        file_name="tuition_report.pdf",
        mime="application/pdf"
    )
