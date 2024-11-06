import streamlit as st
import pandas as pd
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap

# Configure locale for currency formatting
locale.setlocale(locale.LC_ALL, '')

# Set Streamlit to use wide layout
st.set_page_config(layout="wide")

# CSS to ensure full-width display of DataFrames
st.markdown(
    """
    <style>
    .css-1lcbmhc {
        overflow: visible !important;
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
                                  f"Current Tuition: {row['Current Tuition per Student']}, "
                                  f"New Tuition: {row['New Tuition per Student']}, "
                                  f"Increase Percentage: {row['Increase Percentage']:.2f}%")
        row_y -= 15

    # Strategic Items Section with descriptions
    if not strategic_items_df.empty:
        row_y -= 20
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, row_y, "Strategic Items, Costs, and Descriptions:")
        row_y -= 20
        pdf.setFont("Helvetica", 10)
        for i, row in strategic_items_df.iterrows():
            pdf.drawString(50, row_y, f"{row['Strategic Item']}: {row['Cost ($)']}")
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

# Step 3: Automatically Calculate Average Tuition
st.subheader("Step 3: Automatically Calculate Average Tuition")
if sum(num_students) > 0:
    total_tuition = sum([students * tuition for students, tuition in zip(num_students, current_tuition)])
    avg_tuition = total_tuition / sum(num_students)
    st.text(f"Automatically Calculated Average Tuition per Student: {format_currency(avg_tuition)}")
else:
    avg_tuition = 0.0
    st.error("Please enter valid student numbers and tuition rates to calculate average tuition.")

# Step 4: Apply Initial Tuition Increase Across All Grades
st.subheader("Step 4: Apply Initial Tuition Increase Across All Grades")
final_tuition_increase = st.number_input("Enter Overall Tuition Increase Percentage", min_value=0.0, value=9.0, step=0.1)
st.text(f"Applying {final_tuition_increase}% increase across all grades.")

# Calculate initial new tuition per student with the uniform increase
initial_new_tuition_per_student = [tuition * (1 + final_tuition_increase / 100) for tuition in current_tuition]
total_initial_new_tuition = sum([students * tuition for students, tuition in zip(num_students, initial_new_tuition_per_student)])

# Display initial results in a non-scrollable, full-width DataFrame
initial_data = {
    "Grade": grades,
    "Number of Students": num_students,
    "Current Tuition per Student": [format_currency(tuition) for tuition in current_tuition],
    "New Tuition per Student": [format_currency(nt) for nt in initial_new_tuition_per_student],
    "Increase Percentage": [final_tuition_increase] * num_grades,
}
initial_df = pd.DataFrame(initial_data)
st.subheader("Initial Tuition Increase Results")
st.write(initial_df)
st.write(f"**Total New Tuition with Initial Increase:** {format_currency(total_initial_new_tuition)}")

# Step 5: Adjust Tuition for Each Grade Level
st.subheader("Adjust Tuition for Each Grade Level")
adjustment_df = pd.DataFrame({
    "Grade": grades,
    "Number of Students": num_students,
    "Current Tuition per Student": current_tuition,
    "Initial New Tuition per Student": initial_new_tuition_per_student,
    "Adjusted New Tuition per Student": initial_new_tuition_per_student,  # Start with initial values
})

# Allow user to input adjusted tuition for each grade level
for i in range(num_grades):
    adjustment_df.at[i, "Adjusted New Tuition per Student"] = st.number_input(
        f"Adjusted Tuition for {grades[i]} ($)",
        min_value=0.0,
        value=initial_new_tuition_per_student[i],
        step=0.01,
        key=f"adjusted_tuition_{i}"
    )

# Calculate percentage increase based on user input and total tuition
adjustment_df["Adjusted Increase (%)"] = [
    ((adjusted - current) / current * 100) if current > 0 else 0
    for adjusted, current in zip(adjustment_df["Adjusted New Tuition per Student"], adjustment_df["Current Tuition per Student"])
]

adjustment_df["Total Tuition for Grade"] = adjustment_df["Number of Students"] * adjustment_df["Adjusted New Tuition per Student"]
adjusted_total_tuition = adjustment_df["Total Tuition for Grade"].sum()

# Display adjusted tuition table and the updated total in a non-scrollable, full-width DataFrame
st.subheader("Adjusted Tuition Results")
st.write(adjustment_df[["Grade", "Number of Students", "Current Tuition per Student", "Adjusted New Tuition per Student", "Adjusted Increase (%)", "Total Tuition for Grade"]])
st.write(f"**Total Adjusted Tuition:** {format_currency(adjusted_total_tuition)}")

# Step 6: Generate PDF with Results
if st.button("Download PDF Report"):
    pdf_buffer = generate_pdf(
        report_title, adjustment_df, total_current_tuition=total_tuition, total_new_tuition=adjusted_total_tuition,
        avg_increase_percentage=final_tuition_increase, tuition_assistance_ratio=0,  # Placeholder for tuition assistance ratio
        strategic_items_df=pd.DataFrame(),  # Placeholder for strategic items
        summary_text="The tuition increase was initially applied uniformly, then adjusted manually per grade level."
    )

    st.download_button(
        label="Download Report as PDF",
        data=pdf_buffer,
        file_name="tuition_report.pdf",
        mime="application/pdf"
    )
