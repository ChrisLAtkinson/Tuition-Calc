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
        return f"<span class='math-inline'><span class="math-inline">\{\{\{value\:,\.2f\}\}\}</span\>"  \# Corrected line
\# Function to format input strings as currency
def format\_input\_as\_currency\(input\_value\)\:
try\:
if not input\_value\:
return ""
input\_value \= input\_value\.replace\(",", ""\)\.replace\("</span>", "")
        value = float(input_value)
        return f"<span class="math-inline">\{value\:,\.2f\}"
except ValueError\:
return ""
\# Function to generate a downloadable PDF report
def generate\_pdf\(report\_title, df, total\_current\_tuition, total\_new\_tuition, avg\_increase\_percentage, tuition\_assistance\_ratio, strategic\_items\_df, summary\_text\)\:
buffer \= BytesIO\(\)
pdf \= canvas\.Canvas\(buffer, pagesize\=letter\)
width, height \= letter
\# Title of the report
pdf\.setFont\("Helvetica\-Bold", 16\)
pdf\.drawString\(50, height \- 50, f"Report Title\: \{report\_title\}"\)
\# Summary details
pdf\.setFont\("Helvetica", 12\)
pdf\.drawString\(50, height \- 80, f"Total Current Tuition\: \{format\_currency\(total\_current\_tuition\)\}"\)
pdf\.drawString\(50, height \- 100, f"Total New Tuition\: \{format\_currency\(total\_new\_tuition\)\}"\)
pdf\.drawString\(50, height \- 120, f"Average Tuition Increase Percentage\: \{avg\_increase\_percentage\:\.2f\}%"\)
pdf\.drawString\(50, height \- 140, f"Tuition Assistance Ratio\: \{tuition\_assistance\_ratio\:\.2f\}%"\)
\# Add the table for tuition by grade level
pdf\.drawString\(50, height \- 170, "Tuition by Grade Level\:"\)
row\_y \= height \- 190
pdf\.setFont\("Helvetica", 10\)
for i, row in df\.iterrows\(\)\:
pdf\.drawString\(50, row\_y, f"\{row\['Grade'\]\}\: \{row\['Number of Students'\]\} students, "
f"Current Tuition\: \{format\_currency\(row\['Current Tuition per Student'\]\)\}, "
f"Adjusted New Tuition\: \{format\_currency\(row\['Adjusted New Tuition per Student'\]\)\}"\)
row\_y \-\= 15
\# Strategic Items Section with descriptions
if not strategic\_items\_df\.empty\:
row\_y \-\= 20
pdf\.setFont\("Helvetica\-Bold", 12\)
pdf\.drawString\(50, row\_y, "Strategic Items, Costs, and Descriptions\:"\)
row\_y \-\= 20
pdf\.setFont\("Helvetica", 10\)
for i, row in strategic\_items\_df\.iterrows\(\)\:
pdf\.drawString\(50, row\_y, f"\{row\['Strategic Item'\]\}\: \{format\_currency\(row\['Cost \(</span>)'])}")
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
    tuition_input = st.text_input(f"Current Tuition per Student in {grade} (<span class="math-inline">\)", ""\)
formatted\_tuition \= format\_input\_as\_currency\(tuition\_input\)
st\.text\(f"Formatted Tuition\: \{formatted\_tuition\}"\)
tuition \= float\(formatted\_tuition\.replace\(",", ""\)\.replace\("</span>", "")) if formatted_tuition else 0.0
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
    item_cost_input = st.text_input(f"Cost of {item_name} (<span class="math-inline">\)", ""\)
formatted\_item\_cost \= format\_input\_as\_currency\(item\_cost\_input\)
st\.text\(f"Formatted Cost\: \{formatted\_item\_cost\}"\)
item\_cost \= float\(formatted\_item\_cost\.replace\(",", ""\)\.replace\("</span>", "")) if formatted_item_cost else 0.0
    item_description = st.text_area(f"Description for {item_name}", f"Enter a description for {item_name}")

    strategic_item_names.append(item_name)
    strategic_items_costs.append(item_cost)
    strategic_item_descriptions.append(item_description)

# Step 5: Previous Year’s Total Expenses
st.subheader("Step 5: Enter Previous Year's Total Expenses")
previous_expenses_input = st.text_input("Previous Year's Total Expenses (<span class="math-inline">\)", ""\)
formatted\_previous\_expenses \= format\_input\_as\_currency\(previous\_expenses\_input\)
st\.text\(f"Formatted Previous Expenses\: \{formatted\_previous\_expenses\}"\)
previous\_expenses \= float\(formatted\_previous\_expenses\.replace\(",", ""\)\.replace\("</span>", "")) if formatted_previous_expenses else 0.0

# Step 6: Operations Tuition Increase (OTI) and Final Increase Calculation
st.subheader("Step 6: Operations Tuition Increase (OTI) and Final Increase Calculation")
roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01, value=3.32)
rpi_percentage = st.number_input("Rate of Productivity Increase (RPI) %", min_value=0.0, step=0.01, value=2.08)
oti = roi
