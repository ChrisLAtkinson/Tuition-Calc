import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
                                  f"Current Tuition: {row['Current Tuition per Student']}, "
                                  f"New Tuition: {row['New Tuition per Student']}, "
                                  f"Increase Applied: {row['Increase Percentage']:.2f}%")
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

# Step 4: Add Strategic Items and Descriptions
st.subheader("Step 4: Add Strategic Items and Descriptions")
strategic_items_costs = []
strategic_item_names = []
strategic_item_descriptions = []
num_items = st.number_input("Number of Strategic Items", min_value=0, max_value=10, value=0, step=1)

for i in range(int(num_items)):
    item_name = st.text_input(f"Strategic Item {i+1} Name", f"Item {i+1}")
    item_cost_input = st.text_input(f"Cost of {item_name} ($)", "")
    formatted_item_cost = format_input_as_currency(item_cost_input)
    st.text(f"Formatted Cost: {formatted_item_cost}")
    item_cost = float(formatted_item_cost.replace(",", "").replace("$", "")) if formatted_item_cost else 0.0
    item_description = st.text_area(f"Description for {item_name}", f"Enter a description for {item_name}")

    strategic_item_names.append(item_name)
    strategic_items_costs.append(item_cost)
    strategic_item_descriptions.append(item_description)

# Step 5: Previous Year’s Expenses
st.subheader("Step 5: Previous Year's Total Expenses")
previous_expenses_input = st.text_input("Previous Year's Total Expenses ($)", "")
formatted_previous_expenses = format_input_as_currency(previous_expenses_input)
st.text(f"Formatted Previous Expenses: {formatted_previous_expenses}")
previous_expenses = float(formatted_previous_expenses.replace(",", "").replace("$", "")) if formatted_previous_expenses else 0.0

# Step 6: Operations Tuition Increase (OTI) Calculation
st.subheader("Step 6: Operations Tuition Increase (OTI) Calculation")
roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01, value=3.32)
rpi_percentage = st.number_input("Rate of Productivity Increase (RPI) %", min_value=0.0, step=0.01, value=2.08)
oti = roi_percentage + rpi_percentage
st.text(f"Operations Tuition Increase (OTI): {oti:.2f}%")

# Step 7: Automatically Calculate Strategic Items (SI) Percentage
st.subheader("Step 7: Automatically Calculate Strategic Items (SI) Percentage")
total_strategic_items_cost = sum(strategic_items_costs)
num_total_students = sum(num_students)

if avg_tuition > 0 and num_total_students > 0:
    cost_per_student = total_strategic_items_cost / num_total_students
    si_percentage = (cost_per_student / avg_tuition) * 100
else:
    si_percentage = 0.0

st.text(f"Strategic Items (SI) Percentage: {si_percentage:.2f}%")

# Step 8: Calculate Final Tuition Increase
st.subheader("Step 8: Calculate Final Tuition Increase")
final_tuition_increase = oti + si_percentage
st.text(f"Final Tuition Increase: {final_tuition_increase:.2f}%")

# Step 9: Financial Aid (Tuition Assistance) Calculation
st.subheader("Step 9: Financial Aid (Tuition Assistance)")
financial_aid_input = st.text_input("Total Financial Aid ($)", "")
formatted_financial_aid = format_input_as_currency(financial_aid_input)
st.text(f"Formatted Financial Aid: {formatted_financial_aid}")
financial_aid = float(formatted_financial_aid.replace(",", "").replace("$", "")) if formatted_financial_aid else 0.0

# Step 10: Initial Calculation and Display of Results with Adjustments
if st.button("Calculate New Tuition"):
    try:
        if sum(num_students) == 0 or len(current_tuition) == 0:
            st.error("Please provide valid inputs for all grade levels.")
        else:
            # Calculate total current tuition for all students
            total_current_tuition = sum([students * tuition for students, tuition in zip(num_students, current_tuition)])
            
            # Evenly distribute initial increase across all grades
            initial_increase_percentage = final_tuition_increase / num_grades
            adjusted_increases = [initial_increase_percentage] * num_grades
            new_tuition_per_student = [
                tuition * (1 + increase / 100) for tuition, increase in zip(current_tuition, adjusted_increases)
            ]

            # Display initial results
            st.subheader("Results - Initial Evenly Distributed Increase")
            tuition_data = {
                "Grade": grades,
                "Number of Students": num_students,
                "Current Tuition per Student": [format_currency(tuition) for tuition in current_tuition],
                "New Tuition per Student": [format_currency(nt) for nt in new_tuition_per_student],
                "Increase Percentage": adjusted_increases,
            }
            df = pd.DataFrame(tuition_data)
            st.write(df)

            # User Adjustment of Increase Percentages
            st.subheader("Adjust Increase Percentage by Grade Level")
            for i, grade in enumerate(grades):
                adjusted_increases[i] = st.slider(
                    f"Adjust Increase for {grade}",
                    min_value=0.0,
                    max_value=2 * final_tuition_increase,
                    value=initial_increase_percentage,
                    step=0.1,
                    key=f"slider_{i}"
                )

            # Apply new tuition after adjustments
            new_tuition_per_student = [
                tuition * (1 + increase / 100) for tuition, increase in zip(current_tuition, adjusted_increases)
            ]
            total_new_tuition = sum([students * tuition for students, tuition in zip(num_students, new_tuition_per_student)])
            tuition_assistance_ratio = (financial_aid / total_new_tuition) * 100 if total_new_tuition > 0 else 0.0

            # Display adjusted results
            st.subheader("Adjusted Tuition Results")
            tuition_data["New Tuition per Student"] = [format_currency(nt) for nt in new_tuition_per_student]
            tuition_data["Increase Percentage"] = adjusted_increases
            df = pd.DataFrame(tuition_data)
            st.write(df)

            # Generate PDF report
            pdf_buffer = generate_pdf(
                report_title, df, total_current_tuition, total_new_tuition,
                final_tuition_increase, tuition_assistance_ratio, pd.DataFrame({
                    "Strategic Item": strategic_item_names,
                    "Cost ($)": [format_currency(cost) for cost in strategic_items_costs],
                    "Description": strategic_item_descriptions
                }), summary_text="The tuition increase was calculated with an evenly distributed increase across grades, with adjustments based on user input."
            )

            st.download_button(
                label="Download Report as PDF",
                data=pdf_buffer,
                file_name="tuition_report.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"An error occurred during calculation: {str(e)}")
