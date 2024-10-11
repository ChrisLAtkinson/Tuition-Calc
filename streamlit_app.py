import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import tempfile
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

# Function to wrap text for PDF
def wrap_text(text, max_width=90):
    return "\n".join(textwrap.wrap(text, max_width))

# Function to generate a downloadable PDF report
def generate_pdf(report_title, df, total_current_tuition, total_new_tuition,
                 avg_increase_percentage, tuition_assistance_ratio, strategic_items_df,
                 graph_image, summary_text, csm_quote, link, expense_summary,
                 comparison_table_image):
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
                                  f"New Tuition: {row['New Tuition per Student']}")
        row_y -= 15

    # Strategic Items Section
    if not strategic_items_df.empty:
        row_y -= 20
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, row_y, "Strategic Items and Costs:")
        row_y -= 20
        pdf.setFont("Helvetica", 10)
        for i, row in strategic_items_df.iterrows():
            pdf.drawString(50, row_y, f"{row['Strategic Item']}: {row['Cost ($)']}")
            row_y -= 15

    # Add the calculation summary text
    row_y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, row_y, "Summary of Calculations:")
    row_y -= 20
    pdf.setFont("Helvetica", 10)
    for line in wrap_text(summary_text).split('\n'):
        pdf.drawString(50, row_y, line)
        row_y -= 15

    # Include the external link
    row_y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, row_y, "External Link to the Article:")
    row_y -= 20
    pdf.setFont("Helvetica", 10)
    for line in wrap_text(link, max_width=70).split('\n'):
        pdf.drawString(50, row_y, line)
        row_y -= 15

    # Include the Christian School Management quote
    row_y -= 30
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, row_y, "Quote from Christian School Management:")
    row_y -= 20
    pdf.setFont("Helvetica", 10)
    for line in wrap_text(csm_quote).split('\n'):
        pdf.drawString(50, row_y, line)
        row_y -= 15

    # Add the Expense Summary
    row_y -= 30
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, row_y, "Expense Summary:")
    row_y -= 20
    pdf.setFont("Helvetica", 10)
    for line in wrap_text(expense_summary).split('\n'):
        pdf.drawString(50, row_y, line)
        row_y -= 15

    # Embed images if available
    try:
        if graph_image:
            pdf.drawImage(ImageReader(graph_image), 50, row_y - 250, width=500, height=200)
            row_y -= 270
        if comparison_table_image:
            pdf.drawImage(ImageReader(comparison_table_image), 50, row_y - 250, width=500, height=200)
            row_y -= 270
    except Exception as e:
        pdf.drawString(50, row_y, f"Could not include images due to: {str(e)}")

    # Finalize PDF
    pdf.save()
    buffer.seek(0)
    return buffer

# Start of Streamlit app
st.title("Tuition Calculation Tool")

# Step 1: Enter a Custom Title for the Report
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

# Step 3: Add Strategic Items
st.subheader("Step 3: Add Strategic Items")
strategic_items_costs = []
strategic_item_names = []
num_items = st.number_input("Number of Strategic Items", min_value=0, max_value=10, value=0, step=1)

for i in range(int(num_items)):
    item_name = st.text_input(f"Strategic Item {i+1} Name", f"Item {i+1}")
    item_cost_input = st.text_input(f"Cost of {item_name} ($)", "")
    formatted_item_cost = format_input_as_currency(item_cost_input)
    st.text(f"Formatted Cost: {formatted_item_cost}")
    item_cost = float(formatted_item_cost.replace(",", "").replace("$", "")) if formatted_item_cost else 0.0
    strategic_item_names.append(item_name)
    strategic_items_costs.append(item_cost)

# Ensure strategic items lists are not empty
if not strategic_item_names:
    strategic_item_names = ["No Strategic Items"]
if not strategic_items_costs:
    strategic_items_costs = [0.0]

# Step 4: Previous Year's Expense Budget
st.subheader("Step 4: Enter the Previous Year's Total Expenses")
total_expenses_input = st.text_input("Total Expenses ($)", "")
formatted_expenses = format_input_as_currency(total_expenses_input)
st.text(f"Formatted Expenses: {formatted_expenses}")
previous_expenses = float(formatted_expenses.replace(",", "").replace("$", "")) if formatted_expenses else 0.0

# Step 5: Operations Tuition Increase (OTI) Calculation
st.subheader("Step 5: Operations Tuition Increase (OTI) Calculation")
roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01, value=0.0)
efficiency_rate = 2.08  # Fixed rate of efficiency
oti = roi_percentage + efficiency_rate

# Step 6: Compensation Percentage
st.subheader("Step 6: Enter Compensation as a Percentage of Expenses")
compensation_percentage = st.number_input("Compensation Percentage (%)", min_value=0.0, max_value=100.0, value=None, step=0.01)

# Step 7: Financial Aid (Tuition Assistance) Calculation
st.subheader("Step 7: Financial Aid (Tuition Assistance)")
financial_aid_input = st.text_input("Total Financial Aid ($)", "")
formatted_financial_aid = format_input_as_currency(financial_aid_input)
st.text(f"Formatted Financial Aid: {formatted_financial_aid}")
financial_aid = float(formatted_financial_aid.replace(",", "").replace("$", "")) if formatted_financial_aid else 0.0

# External link and quote
link = "https://drive.google.com/file/d/1M05nzvRf646Cb5aRkFZuQ4y9F6tlcR1Z/view?usp=drive_link"
csm_quote = """
[Include the quote here]
"""

# Expense Summary
expense_summary = f"""
Total Expenses: {format_currency(previous_expenses)}
ROI plus RPI (OTI): {oti:.2f}%
New Expense Budget: {format_currency(previous_expenses * (1 + oti / 100))}
"""

# Calculate new tuition with OTI
if st.button("Calculate New Tuition"):
    try:
        if sum(num_students) == 0 or len(current_tuition) == 0:
            st.error("Please provide valid inputs for all grade levels.")
        else:
            # Ensure strategic costs per grade level
            if len(strategic_items_costs) < len(current_tuition):
                strategic_items_costs = [sum(strategic_items_costs) / len(current_tuition)] * len(current_tuition)
            else:
                strategic_items_costs = strategic_items_costs[:len(current_tuition)]

            total_current_tuition = sum([students * tuition for students, tuition in zip(num_students, current_tuition)])
            new_tuition_per_student = [(tuition * (1 + oti / 100) + cost) for tuition, cost in zip(current_tuition, strategic_items_costs)]
            total_new_tuition = sum([nt * students for nt, students in zip(new_tuition_per_student, num_students)])
            avg_increase_percentage = ((total_new_tuition - total_current_tuition) / total_current_tuition) * 100 if total_current_tuition > 0 else 0.0
            tuition_assistance_ratio = (financial_aid / total_new_tuition) * 100 if total_new_tuition > 0 else 0.0

            # Display Results
            st.subheader("Results")
            st.write(f"**Report Title:** {report_title}")
            st.write(f"**Total Current Tuition:** {format_currency(total_current_tuition)}")
            st.write(f"**Total New Tuition:** {format_currency(total_new_tuition)}")
            st.write(f"**Average Tuition Increase Percentage:** {avg_increase_percentage:.2f}%")
            st.write(f"**Tuition Assistance Ratio:** {tuition_assistance_ratio:.2f}%")

            # Summary Text
            summary_text = f"""
            ### Summary of Calculation:
            - Applied an OTI of {oti:.2f}% (ROI + 2.08%) to the current tuition.
            - Added strategic costs per student.
            - Calculated new tuition per student and total new tuition.
            - Calculated average tuition increase percentage and tuition assistance ratio.
            """

            st.write(summary_text)
            st.markdown(f"**[External Link to the Article]({link})**")
            st.subheader("Quote from Christian School Management")
            st.write(csm_quote)

            # Create DataFrame for tuition by grade level
            tuition_data = {
                "Grade": grades,
                "Number of Students": num_students,
                "Current Tuition per Student": [format_currency(tuition) for tuition in current_tuition],
                "New Tuition per Student": [format_currency(nt) for nt in new_tuition_per_student],
                "Increase per Student": [format_currency(nt - tuition) for nt, tuition in zip(new_tuition_per_student, current_tuition)]
            }
            df = pd.DataFrame(tuition_data)

            st.subheader("Tuition by Grade Level")
            st.write(df)

            # Create strategic items DataFrame
            strategic_items_df = pd.DataFrame({
                "Strategic Item": strategic_item_names,
                "Cost ($)": [format_currency(cost) for cost in strategic_items_costs]
            })

            st.subheader("Strategic Items")
            st.write(strategic_items_df)

            # Generate graphs and images
            # [Graphs code here, ensuring that images are correctly saved and embedded]

            # Generate the PDF report
            pdf_buffer = generate_pdf(
                report_title, df, total_current_tuition, total_new_tuition,
                avg_increase_percentage, tuition_assistance_ratio, strategic_items_df,
                None, summary_text, csm_quote, link, expense_summary, None
            )

            # Download button for the PDF report
            st.download_button(
                label="Download Report as PDF",
                data=pdf_buffer,
                file_name="tuition_report.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"An error occurred during calculation: {str(e)}")
