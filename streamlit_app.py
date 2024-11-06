import streamlit as st
import pandas as pd
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap
import json

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

# Custom JSON encoder for handling non-serializable types
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, (pd.Series, pd.DataFrame)):
            return obj.to_json(orient='records')
        else:
            try:
                return super().default(obj)
            except TypeError:
                return str(obj)

# Function to generate a downloadable PDF report
def generate_pdf(report_title, df, total_current_tuition, total_new_tuition, avg_increase_percentage, tuition_assistance_ratio, strategic_items_df, summary_text):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title of the report
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, f"Report Title: {report_title}")

    # ... (rest of the PDF generation code remains the same)

    return buffer

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
    tuition = float(formatted_tuition.replace(",", "").replace("$", "")) if formatted_tuition else 0.0
    grades.append(grade)
    num_students.append(students)
    current_tuition.append(tuition)

# Step 3: Automatically Calculate Average Tuition
st.subheader("Step 3: Automatically Calculate Average Tuition")
if sum(num_students) > 0:
    total_tuition = sum([students * tuition for students, tuition in zip(num_students, current_tuition)])
    avg_tuition = total_tuition / sum(num_students)
    st.write(f"Automatically Calculated Average Tuition per Student: {format_currency(avg_tuition)}")
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
    item_cost = float(formatted_item_cost.replace(",", "").replace("$", "")) if formatted_item_cost else 0.0
    item_description = st.text_area(f"Description for {item_name}", f"Enter a description for {item_name}")

    strategic_item_names.append(item_name)
    strategic_items_costs.append(item_cost)
    strategic_item_descriptions.append(item_description)

# Step 5: Previous Year’s Total Expenses
st.subheader("Step 5: Enter Previous Year's Total Expenses")
previous_expenses_input = st.text_input("Previous Year's Total Expenses ($)", "")
formatted_previous_expenses = format_input_as_currency(previous_expenses_input)
previous_expenses = float(formatted_previous_expenses.replace(",", "").replace("$", "")) if formatted_previous_expenses else 0.0

# Step 6: Operations Tuition Increase (OTI) and Final Increase Calculation
st.subheader("Step 6: Operations Tuition Increase (OTI) and Final Increase Calculation")
roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01, value=3.32)
rpi_percentage = st.number_input("Rate of Productivity Increase (RPI) %", min_value=0.0, step=0.01, value=2.08)
oti = roi_percentage + rpi_percentage
total_strategic_items_cost = sum(strategic_items_costs)
si_percentage = (total_strategic_items_cost / (sum(num_students) * avg_tuition)) * 100 if avg_tuition > 0 else 0.0
final_tuition_increase = oti + si_percentage

# Step 7: Financial Aid (Tuition Assistance) Calculation
st.subheader("Step 7: Financial Aid (Tuition Assistance)")
financial_aid_input = st.text_input("Total Financial Aid ($)", "")
formatted_financial_aid = format_input_as_currency(financial_aid_input)
financial_aid = float(formatted_financial_aid.replace(",", "").replace("$", "")) if formatted_financial_aid else 0.0

# Step 8: Calculate New Tuition and Display Results
if st.button("Calculate New Tuition"):
    total_current_tuition = sum([students * tuition for students, tuition in zip(num_students, current_tuition)])
    total_new_tuition = total_current_tuition * (1 + final_tuition_increase / 100)
    new_tuition_per_student = [(tuition * (1 + final_tuition_increase / 100)) for tuition in current_tuition]
    tuition_assistance_ratio = (financial_aid / total_new_tuition) * 100 if total_new_tuition > 0 else 0.0

    # Display Summary Prior to Interactive Adjustment
    st.subheader("Summary Prior to Interactive Adjustment")
    st.write(f"**Report Title:** {report_title}")
    st.write(f"**Total Current Tuition:** {format_currency(total_current_tuition)}")
    st.write(f"**Total New Tuition:** {format_currency(total_new_tuition)}")
    st.write(f"**Final Tuition Increase Percentage:** {final_tuition_increase:.2f}%")
    st.write(f"**Tuition Assistance Ratio:** {tuition_assistance_ratio:.2f}%")

    # Prepare data for editing
    tuition_data = {
        "Grade": grades,
        "Number of Students": num_students,
        "Current Tuition per Student": current_tuition,
        "Adjusted New Tuition per Student": new_tuition_per_student
    }
    df = pd.DataFrame(tuition_data)

    # Handle possible non-serializable types
    df = df.fillna('')  # Replace NaN with empty string
    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = df[col].astype(str)
        elif df[col].dtype == 'int64':
            df[col] = df[col].astype(str)

    # Use session_state for persistence
    if 'adjusted_tuition_df' not in st.session_state:
        st.session_state['adjusted_tuition_df'] = df.to_json(orient='records')

    # Convert back from JSON for editing
    data = st.session_state['adjusted_tuition_df']
    if isinstance(data, str):
        edited_df = pd.read_json(data, orient='records')
    else:
        edited_df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data

    # Interactive Adjustment Table using st.data_editor
    st.subheader("Adjust Tuition by Grade Level")
    
    edited_df = st.data_editor(
        data=edited_df,
        use_container_width=True,
        column_config={
            "Number of Students": st.column_config.NumberColumn(
                "Number of Students", min_value=0, step=1, format="%.0f"
            ),
            "Current Tuition per Student": st.column_config.NumberColumn(
                "Current Tuition per Student", format=format_currency
            ),
            "Adjusted New Tuition per Student": st.column_config.NumberColumn(
                "Adjusted New Tuition per Student", format=format_currency
            ),
        },
        encoder=CustomEncoder
    )

    # Convert edited dataframe back to JSON for session state storage
    st.session_state['adjusted_tuition_df'] = edited_df.to_json(orient='records')

    # Display the adjusted data
    st.write("**Adjusted Tuition Data:**")
    st.write(edited_df)

    # Calculate adjusted totals and differences
    edited_df["Total Tuition for Grade"] = edited_df["Number of Students"].astype(float) * edited_df["Adjusted New Tuition per Student"].astype(float)
    adjusted_total_tuition = edited_df["Total Tuition for Grade"].sum()

    # Display Adjusted Total
    st.write(f"**Adjusted Total Tuition:** {format_currency(adjusted_total_tuition)}")
    st.write(f"**Difference from Target Total Tuition:** {format_currency(total_new_tuition - adjusted_total_tuition)}")

    # Generate the PDF report
    strategic_items_df = pd.DataFrame({
        "Strategic Item": strategic_item_names,
        "Cost ($)": strategic_items_costs,
        "Description": strategic_item_descriptions
    })

    pdf_buffer = generate_pdf(
        report_title, edited_df, total_current_tuition, adjusted_total_tuition,
        final_tuition_increase, tuition_assistance_ratio, strategic_items_df,
        "Summary of tuition adjustment calculations."
    )

    st.download_button(
        label="Download Report as PDF",
        data=pdf_buffer,
        file_name="tuition_report.pdf",
        mime="application/pdf"
    )
