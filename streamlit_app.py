import streamlit as st
import pandas as pd
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

# PDF Generation Function
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

# Define ROI and RPI defaults
roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01, value=3.32)
rpi_percentage = st.number_input("Rate of Productivity Increase (RPI) %", min_value=0.0, step=0.01, value=2.08)

# Streamlit App Start
st.title("Tuition Calculation Tool")

# Step 1: Enter a Custom Title for the Report
st.subheader("Step 1: Enter a Custom Title for the Report")
report_title = st.text_input("Enter a Custom Title for the Report", "2025-26 Tuition Projection")

# Step 2: Add Custom Grade Levels and Tuition Rates
st.subheader("Step 2: Add Custom Grade Levels and Tuition Rates")
# Collect grades, students, and tuition rates (same as original)

# Step 3: Automatically Calculate Average Tuition
st.subheader("Step 3: Automatically Calculate Average Tuition")
# Calculate average tuition based on user inputs (same as original)

# Step 4: Add Strategic Items and Descriptions
st.subheader("Step 4: Add Strategic Items and Descriptions")
# Allow user to input strategic items (same as original)

# Step 5: Previous Year's Total Expenses
st.subheader("Step 5: Enter Previous Year's Total Expenses")
previous_expenses_input = st.text_input("Previous Year's Total Expenses ($)", "")
formatted_previous_expenses = format_input_as_currency(previous_expenses_input)

try:
    previous_expenses = float(formatted_previous_expenses.replace(",", "").replace("$", ""))
except ValueError:
    previous_expenses = 0.0

# KPI Calculations (same as original)
if previous_expenses > 0:
    # Compute and display KPIs
    pass

# Step 6: Operations Tuition Increase (OTI)
st.subheader("Step 6: Operations Tuition Increase (OTI) and Final Increase Calculation")
# Perform OTI and SI calculations (same as original)

# Step 7: Financial Aid Calculation
st.subheader("Step 7: Financial Aid (Tuition Assistance)")
# Handle financial aid and results (same as original)

# PDF Generation and Download
# Include all updated calculations and metrics in the PDF (same as original)

