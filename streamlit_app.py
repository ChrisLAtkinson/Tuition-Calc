import streamlit as st
import pandas as pd
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import base64

# Configure locale for currency formatting
locale.setlocale(locale.LC_ALL, '')

def format_currency(value):
    """Format numbers as currency."""
    try:
        return locale.currency(value, grouping=True)
    except:
        return f"${value:,.2f}"

def format_input_as_currency(input_value):
    """Format input strings as currency."""
    try:
        if not input_value:
            return ""
        input_value = input_value.replace(",", "").replace("$", "")
        value = float(input_value)
        return f"${value:,.2f}"
    except ValueError:
        return ""

# Function to generate a PDF
def create_pdf():
    """Generate a PDF report and return it as a BytesIO object."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Tuition and Expense Planning Report")
    c.drawString(100, 730, f"Previous Year's Total Expenses: {format_currency(previous_expenses)}")
    c.drawString(100, 710, f"Operational Tuition Increase (OTI): {oti_percentage:.2f}%")
    c.drawString(100, 690, f"Total Strategic Items Cost: {format_currency(total_si_cost)}")
    c.drawString(100, 670, f"Total Increase in Expenses: {total_increase_percentage:.2f}%")
    c.drawString(100, 650, f"Projected New Expense Budget: {format_currency(new_expense_budget)}")
    c.drawString(100, 630, f"Total Financial Aid: {format_currency(financial_aid)}")
    c.drawString(100, 610, f"Current Total Tuition: {format_currency(current_total_tuition)}")
    c.drawString(100, 590, f"Projected Total Tuition (Initial Increase): {format_currency(projected_total_tuition)}")
    c.drawString(100, 570, f"Adjusted Total Tuition: {format_currency(adjusted_total_tuition)}")
    c.drawString(100, 550, f"Adjusted Income to Expense Ratio: {income_to_expense_ratio_adjusted:.2f}%")
    c.drawString(100, 530, f"Adjusted Tuition Assistance Ratio: {tuition_assistance_ratio_adjusted:.2f}%")
    c.save()
    buffer.seek(0)
    return buffer

def download_pdf_link(pdf_buffer, filename="report.pdf"):
    """Generate a link to download the PDF."""
    b64_pdf = base64.b64encode(pdf_buffer.read()).decode("utf-8")
    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}">Download Report as PDF</a>'
    return href

# Streamlit App Start
st.title("Tuition and Expense Planning Tool")

# Step 1: Previous Year's Total Expenses
st.subheader("Step 1: Previous Year's Total Expenses")
previous_expenses_input = st.text_input("Enter the Previous Year's Total Expenses ($)", "")
previous_expenses_input = format_input_as_currency(previous_expenses_input)
previous_expenses_input = st.text_input("Formatted:", previous_expenses_input)
try:
    previous_expenses = float(previous_expenses_input.replace(",", "").replace("$", ""))
except ValueError:
    previous_expenses = 0.0

if previous_expenses > 0:
    st.success(f"Previous Year's Total Expenses: {format_currency(previous_expenses)}")
else:
    st.warning("Please enter valid total expenses.")

# Step 2: Operational Tuition Increase (OTI) Calculation
st.subheader("Step 2: Operational Tuition Increase (OTI)")
roi = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01, value=3.32)
rpi = st.number_input("Rate of Productivity Increase (RPI) %", min_value=0.0, step=0.01, value=2.08)
oti_percentage = roi + rpi
st.info(f"Operational Tuition Increase (OTI): {oti_percentage:.2f}%")

# Step 3: Strategic Items (SI) Input
st.subheader("Step 3: Strategic Items (SI)")
strategic_items = []
num_items = st.number_input("Number of Strategic Items", min_value=0, max_value=10, step=1, value=0)
for i in range(num_items):
    item_name = st.text_input(f"Strategic Item {i+1} Name", f"Item {i+1}")
    item_cost_input = st.text_input(f"Cost of {item_name} ($)", "")
    item_cost_input = format_input_as_currency(item_cost_input)
    item_cost_input = st.text_input("Formatted:", item_cost_input)
    try:
        item_cost = float(item_cost_input.replace(",", "").replace("$", ""))
    except ValueError:
        item_cost = 0.0
    item_description = st.text_area(f"Description of {item_name}", f"Details for {item_name}")
    strategic_items.append({"Item": item_name, "Cost": item_cost, "Description": item_description})

total_si_cost = sum(item["Cost"] for item in strategic_items)
si_percentage = (total_si_cost / previous_expenses) * 100 if previous_expenses > 0 else 0.0
st.info(f"Total Strategic Items Cost: {format_currency(total_si_cost)}")
st.info(f"Strategic Items (SI) Percentage: {si_percentage:.2f}%")

# Display Strategic Items Table
if strategic_items:
    st.subheader("Strategic Items Overview")
    strategic_items_df = pd.DataFrame(strategic_items)
    st.table(strategic_items_df)

# Step 4: Total Expense Growth and Budget Projection
st.subheader("Step 4: Total Expense Growth and Budget Projection")
total_increase_percentage = oti_percentage + si_percentage
new_expense_budget = previous_expenses * (1 + total_increase_percentage / 100)

st.write(f"Total Increase in Expenses: {total_increase_percentage:.2f}%")
st.write(f"Projected New Expense Budget: {format_currency(new_expense_budget)}")

# Step 5: Tuition Assistance
st.subheader("Step 5: Tuition Assistance")
financial_aid_input = st.text_input("Total Financial Aid Provided ($)", "")
financial_aid_input = format_input_as_currency(financial_aid_input)
financial_aid_input = st.text_input("Formatted:", financial_aid_input)
try:
    financial_aid = float(financial_aid_input.replace(",", "").replace("$", ""))
except ValueError:
    financial_aid = 0.0

if financial_aid > 0:
    st.success(f"Total Financial Aid: {format_currency(financial_aid)}")
else:
    st.warning("Please enter valid financial aid amount.")

# Step 6: Tuition Adjustment by Grade Level
st.subheader("Step 6: Tuition Adjustment by Grade Level")
num_grades = st.number_input("Number of Grade Levels", min_value=1, max_value=12, step=1, value=1)
grades = []
for i in range(num_grades):
    grade_name = st.text_input(f"Grade Level {i+1} Name", f"Grade {i+1}")
    num_students = st.number_input(f"Number of Students in {grade_name}", min_value=0, step=1, value=0)
    current_tuition = st.number_input(f"Current Tuition per Student in {grade_name} ($)", min_value=0.0, step=0.01, value=0.0)
    grades.append({"Grade": grade_name, "Number of Students": num_students, "Current Tuition": current_tuition})

grades_df = pd.DataFrame(grades)
grades_df["Projected Tuition per Student"] = grades_df["Current Tuition"] * (1 + total_increase_percentage / 100)
grades_df["Total Current Tuition"] = grades_df["Number of Students"] * grades_df["Current Tuition"]
grades_df["Total Projected Tuition"] = grades_df["Number of Students"] * grades_df["Projected Tuition per Student"]

current_total_tuition = grades_df["Total Current Tuition"].sum()

if st.button("View Results"):
    st.subheader("Initial Projected Tuition Increase")
    st.table(grades_df)

    projected_total_tuition = grades_df["Total Projected Tuition"].sum()
    tuition_assistance_ratio_projected = (financial_aid / projected_total_tuition) * 100 if projected_total_tuition > 0 else 0.0
    income_to_expense_ratio_projected = (projected_total_tuition / new_expense_budget) * 100 if new_expense_budget > 0 else 0.0
    tuition_rate_increase_projected = ((projected_total_tuition - current_total_tuition) / current_total_tuition) * 100 if current_total_tuition > 0 else 0.0

    st.write(f"**Current Total Tuition:** {format_currency(current_total_tuition)}")
    st.write(f"**Projected Total Tuition (Initial Increase):** {format_currency(projected_total_tuition)}")
    st.write(f"**Projected Tuition Assistance Ratio:** {tuition_assistance_ratio_projected:.2f}%")
    st.write(f"**Projected Income to Expense (I/E) Ratio:** {income_to_expense_ratio_projected:.2f}%")
    st.write(f"**Tuition Rate Increase (Projected):** {tuition_rate_increase_projected:.2f}%")

st.subheader("Generate and Download Report")
if st.button("Print PDF"):
    pdf_buffer = create_pdf()
    st.markdown(download_pdf_link(pdf_buffer), unsafe_allow_html=True)
