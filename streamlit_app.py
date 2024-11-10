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

# Initialize session states
if "calculated_values" not in st.session_state:
    st.session_state.calculated_values = None

if "adjusted_tuition" not in st.session_state:
    st.session_state.adjusted_tuition = None

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

# Ensure the value respects the minimum constraint
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

# Step 5: Previous Year's Total Expenses
st.subheader("Step 5: Enter Previous Year's Total Expenses")
previous_expenses_input = st.text_input("Previous Year's Total Expenses ($)", "")
formatted_previous_expenses = format_input_as_currency(previous_expenses_input)
try:
    previous_expenses = float(formatted_previous_expenses.replace(",", "").replace("$", ""))
except ValueError:
    previous_expenses = 0.0

# Step 6: Operations Tuition Increase (OTI) and Final Increase Calculation
st.subheader("Step 6: Operations Tuition Increase (OTI) and Final Increase Calculation")
roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01, value=3.32)
rpi_percentage = st.number_input("Rate of Productivity Increase (RPI) %", min_value=0.0, step=0.01, value=2.08)
oti = roi_percentage + rpi_percentage
total_strategic_items_cost = sum(strategic_items["costs"])
si_percentage = (
    (total_strategic_items_cost / (sum(grades_data["num_students"]) * avg_tuition)) * 100 if avg_tuition > 0 else 0.0
)
final_tuition_increase = oti + si_percentage

# Step 7: Financial Aid (Tuition Assistance) Calculation
st.subheader("Step 7: Financial Aid (Tuition Assistance)")
financial_aid_input = st.text_input("Total Financial Aid ($)", "")
formatted_financial_aid = format_input_as_currency(financial_aid_input)
try:
    financial_aid = float(formatted_financial_aid.replace(",", "").replace("$", ""))
except ValueError:
    financial_aid = 0.0

# Add "Calculate New Tuition" button
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
        "tuition_assistance_ratio": tuition_assistance_ratio
    }

    # Initialize adjusted tuition if not already set
    if st.session_state.adjusted_tuition is None:
        st.session_state.adjusted_tuition = [
            tuition * (1 + final_tuition_increase / 100) for tuition in grades_data["current_tuition"]
        ]

# Display results if calculations have been performed
if st.session_state.calculated_values is not None:
    st.subheader("Results")
    st.write(f"**Report Title:** {report_title}")
    st.write(f"**Total Current Tuition:** {format_currency(st.session_state.calculated_values['total_current_tuition'])}")
    st.write(f"**Total New Tuition:** {format_currency(st.session_state.calculated_values['total_new_tuition'])}")
    st.write(f"**Final Tuition Increase Percentage:** {st.session_state.calculated_values['final_tuition_increase']:.2f}%")
    st.write(f"**Tuition Assistance Ratio:** {st.session_state.calculated_values['tuition_assistance_ratio']:.2f}%")

    # Interactive Table: Adjust Tuition by Grade Level
    st.subheader("Adjust Tuition by Grade Level")
    
    # Create initial DataFrame
    tuition_data = {
        "Grade": grades_data["grades"],
        "Number of Students": grades_data["num_students"],
        "Current Tuition per Student": grades_data["current_tuition"],
    }
    
    # Render the interactive number inputs dynamically
    adjusted_tuition_values = []
    for i in range(len(grades_data["grades"])):
        adjusted_value = st.number_input(
            f"Adjusted Tuition for {grades_data['grades'][i]}",
            value=float(st.session_state.adjusted_tuition[i]),
            min_value=0.0,
            step=0.01,
            key=f"adjusted_tuition_{i}"
        )
        adjusted_tuition_values.append(adjusted_value)
    
    # Update session state with new values
    st.session_state.adjusted_tuition = adjusted_tuition_values
    
    # Create complete DataFrame with all values
    df = pd.DataFrame(tuition_data)
    df["Adjusted New Tuition per Student"] = adjusted_tuition_values
    df["Total Tuition for Grade"] = df["Number of Students"] * df["Adjusted New Tuition per Student"]
    
    # Calculate updated totals
    adjusted_total_tuition = df["Total Tuition for Grade"].sum()
    updated_tuition_assistance_ratio = (financial_aid / adjusted_total_tuition) * 100 if adjusted_total_tuition > 0 else 0.0

    # Display the updated table and calculations
    st.write(df[["Grade", "Number of Students", "Current Tuition per Student", "Adjusted New Tuition per Student", "Total Tuition for Grade"]].style.format({
        "Current Tuition per Student": lambda x: format_currency(x),
        "Adjusted New Tuition per Student": lambda x: format_currency(x),
        "Total Tuition for Grade": lambda x: format_currency(x)
    }))
    
    st.write(f"**Adjusted Total Tuition:** {format_currency(adjusted_total_tuition)}")
    st.write(f"**Difference from Target Total Tuition:** {format_currency(st.session_state.calculated_values['total_new_tuition'] - adjusted_total_tuition)}")
    st.write(f"**Updated Tuition Assistance Ratio:** {updated_tuition_assistance_ratio
