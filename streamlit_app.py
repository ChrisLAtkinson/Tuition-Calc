import streamlit as st
import pandas as pd
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

# Streamlit App Start
st.title("Tuition and Expense Planning Tool")

# Step 1: Previous Year's Total Expenses
st.subheader("Step 1: Previous Year's Total Expenses")
previous_expenses_input = st.text_input("Enter the Previous Year's Total Expenses ($)", "")
formatted_previous_expenses = format_input_as_currency(previous_expenses_input)
try:
    previous_expenses = float(formatted_previous_expenses.replace(",", "").replace("$", ""))
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
    formatted_cost = format_input_as_currency(item_cost_input)
    try:
        item_cost = float(formatted_cost.replace(",", "").replace("$", ""))
    except ValueError:
        item_cost = 0.0
    strategic_items.append({"Item": item_name, "Cost": item_cost})

total_si_cost = sum(item["Cost"] for item in strategic_items)
si_percentage = (total_si_cost / previous_expenses) * 100 if previous_expenses > 0 else 0.0
st.info(f"Total Strategic Items Cost: {format_currency(total_si_cost)}")
st.info(f"Strategic Items (SI) Percentage: {si_percentage:.2f}%")

# Step 4: Total Expense Growth and Budget Projection
st.subheader("Step 4: Total Expense Growth and Budget Projection")
total_increase_percentage = oti_percentage + si_percentage
new_expense_budget = previous_expenses * (1 + total_increase_percentage / 100)

st.write(f"Total Increase in Expenses: {total_increase_percentage:.2f}%")
st.write(f"Projected New Expense Budget: {format_currency(new_expense_budget)}")

# Step 5: Tuition Adjustment
st.subheader("Step 5: Tuition Adjustment")
number_of_students = st.number_input("Total Number of Students", min_value=1, step=1, value=1)
current_avg_tuition = st.number_input("Current Average Tuition per Student ($)", min_value=0.0, step=0.01, value=0.0)

current_total_tuition = number_of_students * current_avg_tuition
new_avg_tuition = current_avg_tuition * (1 + total_increase_percentage / 100)
new_total_tuition = number_of_students * new_avg_tuition

st.write(f"Current Total Tuition: {format_currency(current_total_tuition)}")
st.write(f"Projected New Average Tuition per Student: {format_currency(new_avg_tuition)}")
st.write(f"Projected New Total Tuition: {format_currency(new_total_tuition)}")

# Step 6: Financial Metrics and KPIs
st.subheader("Step 6: Financial Metrics and Key Performance Indicators")
income_to_expense_ratio = (new_total_tuition / new_expense_budget) * 100 if new_expense_budget > 0 else 0.0

st.write(f"Income to Expense (I/E) Ratio: {income_to_expense_ratio:.2f}%")
st.write(f"Target KPI (I/E Ratio): {100:.2f}%")
if income_to_expense_ratio < 100:
    st.warning("Projected income does not fully cover projected expenses.")

# Downloadable Report
if st.button("Generate PDF Report"):
    st.write("PDF generation functionality to be added here.")
