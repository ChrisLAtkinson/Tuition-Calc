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
def generate_pdf(report_title, df, total_current_tuition, adjusted_total_tuition, 
                 tuition_increase_percentage, updated_tuition_assistance_ratio, 
                 strategic_items_df, original_calculations, financial_aid, 
                 next_year_expenses, tuition_to_expenses_ratio, compensation_to_expenses_ratio):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title of the report
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, f"Report Title: {report_title}")

    # Include Key Metrics
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 80, "Key Performance Indicators (KPIs):")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, height - 100, f"Tuition-to-Expenses Ratio: {tuition_to_expenses_ratio:.2f}%")
    pdf.drawString(50, height - 120, f"Compensation-to-Expenses Ratio: {compensation_to_expenses_ratio:.2f}%")
    pdf.drawString(50, height - 140, f"Projected Next Year's Expenses: {format_currency(next_year_expenses)}")

    # Original Calculations
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 170, "Original Calculated Results:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, height - 190, f"Total Current Tuition: {format_currency(original_calculations['total_current_tuition'])}")
    pdf.drawString(50, height - 210, f"Target New Tuition: {format_currency(original_calculations['total_new_tuition'])}")
    pdf.drawString(50, height - 230, f"Original Increase Percentage: {original_calculations['final_tuition_increase']:.2f}%")
    pdf.drawString(50, height - 250, f"Original Tuition Assistance Ratio: {original_calculations['tuition_assistance_ratio']:.2f}%")

    # Finalize PDF
    pdf.save()
    buffer.seek(0)
    return buffer

# Initialize session states
if "calculated_values" not in st.session_state:
    st.session_state.calculated_values = None

if "adjusted_tuition" not in st.session_state:
    st.session_state.adjusted_tuition = []

if "grades_data" not in st.session_state:
    st.session_state.grades_data = {"grades": [], "num_students": [], "current_tuition": []}

if "strategic_items" not in st.session_state:
    st.session_state.strategic_items = {"names": [], "costs": [], "descriptions": []}

# Streamlit App Start
st.title("Tuition Calculation Tool")

# Step 1: Enter a Custom Title for the Report
st.subheader("Step 1: Enter a Custom Title for the Report")
report_title = st.text_input("Enter a Custom Title for the Report", "2025-26 Tuition Projection")

# Step 2: Add Custom Grade Levels and Tuition Rates
st.subheader("Step 2: Add Custom Grade Levels and Tuition Rates")

grades_data = st.session_state.grades_data

num_grades = st.number_input(
    "Number of Grade Levels",
    min_value=1,
    max_value=12,
    value=max(1, len(grades_data["grades"])),
    step=1
)

# Adjust grades_data to match the selected number of grades
while len(grades_data["grades"]) < num_grades:
    grades_data["grades"].append(f"Grade {len(grades_data['grades']) + 1}")
    grades_data["num_students"].append(0)
    grades_data["current_tuition"].append(0.0)

while len(grades_data["grades"]) > num_grades:
    grades_data["grades"].pop()
    grades_data["num_students"].pop()
    grades_data["current_tuition"].pop()

# Collect user inputs for each grade level
for i in range(num_grades):
    grades_data["grades"][i] = st.text_input(f"Grade Level {i+1} Name", grades_data["grades"][i])
    grades_data["num_students"][i] = st.number_input(
        f"Number of Students in {grades_data['grades'][i]}",
        min_value=0,
        step=1,
        value=grades_data["num_students"][i]
    )
    tuition_input = st.text_input(
        f"Current Tuition per Student in {grades_data['grades'][i]} ($)", 
        value=format_currency(grades_data["current_tuition"][i])
    )
    formatted_tuition = format_input_as_currency(tuition_input)
    try:
        grades_data["current_tuition"][i] = float(formatted_tuition.replace(",", "").replace("$", ""))
    except ValueError:
        grades_data["current_tuition"][i] = 0.0

# Step 3: Automatically Calculate Average Tuition
st.subheader("Step 3: Automatically Calculate Average Tuition")
if sum(grades_data["num_students"]) > 0:
    total_tuition = sum(
        [students * tuition for students, tuition in zip(grades_data["num_students"], grades_data["current_tuition"])]
    )
    avg_tuition = total_tuition / sum(grades_data["num_students"])
    st.text(f"Automatically Calculated Average Tuition per Student: {format_currency(avg_tuition)}")
else:
    avg_tuition = 0.0
    st.error("Please enter valid student numbers and tuition rates to calculate average tuition.")

# Step 4: Add Strategic Items and Descriptions
st.subheader("Step 4: Add Strategic Items and Descriptions")
strategic_items = st.session_state.strategic_items
num_items = st.number_input("Number of Strategic Items", min_value=0, max_value=10, value=len(strategic_items["names"]), step=1)

# Adjust strategic items lists to match the number of items
while len(strategic_items["names"]) < num_items:
    strategic_items["names"].append(f"Item {len(strategic_items['names']) + 1}")
    strategic_items["costs"].append(0.0)
    strategic_items["descriptions"].append("")

while len(strategic_items["names"]) > num_items:
    strategic_items["names"].pop()
    strategic_items["costs"].pop()
    strategic_items["descriptions"].pop()

strategic_items_list = []
for i in range(num_items):
    strategic_items["names"][i] = st.text_input(f"Strategic Item {i+1} Name", strategic_items["names"][i])
    cost_input = st.text_input(f"Cost of {strategic_items['names'][i]} ($)", value=format_currency(strategic_items["costs"][i]))
    formatted_cost = format_input_as_currency(cost_input)
    try:
        strategic_items["costs"][i] = float(formatted_cost.replace(",", "").replace("$", ""))
    except ValueError:
        strategic_items["costs"][i] = 0.0
    strategic_items["descriptions"][i] = st.text_area(
        f"Description for {strategic_items['names'][i]}", value=strategic_items["descriptions"][i]
    )
    strategic_items_list.append({
        "Strategic Item": strategic_items["names"][i],
        "Cost": strategic_items["costs"][i],
        "Description": strategic_items["descriptions"][i]
    })

strategic_items_df = pd.DataFrame(strategic_items_list)

# Step 5: Previous Year's Total Expenses and Key Performance Indicators (KPIs)
st.subheader("Step 5: Enter Previous Year's Total Expenses")
previous_expenses_input = st.text_input("Previous Year's Total Expenses ($)", "")
formatted_previous_expenses = format_input_as_currency(previous_expenses_input)

try:
    previous_expenses = float(formatted_previous_expenses.replace(",", "").replace("$", ""))
except ValueError:
    previous_expenses = 0.0

if previous_expenses > 0:
    # Calculate KPIs
    total_tuition = sum(grades_data["num_students"]) * avg_tuition
    tuition_to_expenses_ratio = (total_tuition / previous_expenses) * 100
    total_compensation = sum(strategic_items["costs"])
    compensation_to_expenses_ratio = (total_compensation / previous_expenses) * 100

    # Display KPIs
    st.write("**Key Performance Indicators (KPIs):**")
    st.write(f"- Tuition-to-Expenses Ratio: {tuition_to_expenses_ratio:.2f}% (Target: 100%-102%)")
    st.write(f"- Compensation-to-Expenses Ratio: {compensation_to_expenses_ratio:.2f}% (Target: 70%-80%)")

    # Estimate Next Year's Expenses
    total_strategic_items_cost = sum(strategic_items["costs"])
    expense_increase_oti = previous_expenses * (roi_percentage / 100 + rpi_percentage / 100)
    next_year_expenses = previous_expenses

    next_year_expenses = previous_expenses + expense_increase_oti + total_strategic_items_cost

    st.write(f"**Projected Next Year's Expenses:** {format_currency(next_year_expenses)}")
    st.write(
        f"This projection includes:\n"
        f"- Inflation (ROI): {roi_percentage:.2f}%\n"
        f"- Productivity Increase (RPI): {rpi_percentage:.2f}%\n"
        f"- Strategic Items Cost: {format_currency(total_strategic_items_cost)}"
    )
else:
    st.error("Please enter a valid value for the previous year's total expenses.")

# Step 6: Operations Tuition Increase (OTI) and Final Increase Calculation
st.subheader("Step 6: Operations Tuition Increase (OTI) and Final Increase Calculation")

# Rate of Inflation (ROI) and Rate of Productivity Increase (RPI)
roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01, value=3.32)
rpi_percentage = st.number_input("Rate of Productivity Increase (RPI) %", min_value=0.0, step=0.01, value=2.08)

# Calculate OTI
oti = roi_percentage + rpi_percentage

# Calculate Strategic Items Contribution
if avg_tuition > 0:
    si_percentage = (total_strategic_items_cost / (sum(grades_data["num_students"]) * avg_tuition)) * 100
else:
    si_percentage = 0.0

# Final Tuition Increase
final_tuition_increase = oti + si_percentage

# Display Tuition Increase Narrative
tuition_increase_summary = (
    f"The tuition increase calculation includes:\n"
    f"- Operations Tuition Increase (OTI): {oti:.2f}%\n"
    f"- Strategic Items Contribution: {si_percentage:.2f}%\n"
    f"Resulting in a total tuition increase of: {final_tuition_increase:.2f}%."
)
st.subheader("Tuition Increase Narrative")
st.write(tuition_increase_summary)

# Step 7: Financial Aid (Tuition Assistance) Calculation
st.subheader("Step 7: Financial Aid (Tuition Assistance)")
financial_aid_input = st.text_input("Total Financial Aid ($)", "")
formatted_financial_aid = format_input_as_currency(financial_aid_input)
try:
    financial_aid = float(formatted_financial_aid.replace(",", "").replace("$", ""))
except ValueError:
    financial_aid = 0.0

# Final Results
if st.button("Calculate New Tuition"):
    total_current_tuition = sum(
        [students * tuition for students, tuition in zip(grades_data["num_students"], grades_data["current_tuition"])]
    )
    total_new_tuition = total_current_tuition * (1 + final_tuition_increase / 100)
    tuition_assistance_ratio = (financial_aid / total_new_tuition) * 100 if total_new_tuition > 0 else 0.0

    # Store calculated values in session state
    st.session_state.calculated_values = {
        "total_current_tuition": total_current_tuition,
        "total_new_tuition": total_new_tuition,
        "final_tuition_increase": final_tuition_increase,
        "tuition_assistance_ratio": tuition_assistance_ratio,
        "tuition_to_expenses_ratio": tuition_to_expenses_ratio,
        "compensation_to_expenses_ratio": compensation_to_expenses_ratio,
        "next_year_expenses": next_year_expenses
    }

    # Display Results
    st.subheader("Results")
    st.write(f"**Projected Next Year's Expenses:** {format_currency(next_year_expenses)}")
    st.write(f"**Tuition-to-Expenses Ratio:** {tuition_to_expenses_ratio:.2f}%")
    st.write(f"**Compensation-to-Expenses Ratio:** {compensation_to_expenses_ratio:.2f}%")
    st.write(f"**Final Tuition Increase:** {final_tuition_increase:.2f}%")
    st.write(f"**Total Financial Aid:** {format_currency(financial_aid)}")

    # Generate and Display Adjusted Tuition Table
    st.subheader("Adjusted Tuition by Grade Level")
    tuition_data = {
        "Grade": grades_data["grades"],
        "Number of Students": grades_data["num_students"],
        "Current Tuition per Student": [format_currency(val) for val in grades_data["current_tuition"]],
    }
    adjusted_tuition_values = [
        tuition * (1 + final_tuition_increase / 100) for tuition in grades_data["current_tuition"]
    ]
    tuition_data["Adjusted Tuition per Student"] = [format_currency(val) for val in adjusted_tuition_values]
    tuition_data["Total Tuition per Grade"] = [
        format_currency(students * adj_tuition)
        for students, adj_tuition in zip(grades_data["num_students"], adjusted_tuition_values)
    ]
    df = pd.DataFrame(tuition_data)
    st.table(df)

    # PDF Generation
    if st.button("Download PDF Report"):
        pdf_buffer = generate_pdf(
            report_title,
            df,
            total_current_tuition,
            total_new_tuition,
            final_tuition_increase,
            tuition_assistance_ratio,
            strategic_items_df,
            st.session_state.calculated_values,
            financial_aid,
            next_year_expenses,
            tuition_to_expenses_ratio,
            compensation_to_expenses_ratio
        )
        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="tuition_report.pdf",
            mime="application/pdf"
        )
