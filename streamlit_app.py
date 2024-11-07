import streamlit as st
import pandas as pd
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt

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

# Enhanced PDF generation function
def generate_pdf_with_graphs_and_tables(report_title, df, total_current_tuition, total_new_tuition,
                                        avg_increase_percentage, tuition_assistance_ratio, strategic_items_df, summary_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph(f"<b>Report Title:</b> {report_title}", styles['Title']))

    # Summary section
    summary_data = [
        ["Total Current Tuition", format_currency(total_current_tuition)],
        ["Total New Tuition", format_currency(total_new_tuition)],
        ["Average Tuition Increase (%)", f"{avg_increase_percentage:.2f}%"],
        ["Tuition Assistance Ratio (%)", f"{tuition_assistance_ratio:.2f}%"]
    ]
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)

    # Tuition by grade level table
    tuition_data = df[["Grade", "Number of Students", "Current Tuition per Student", "Adjusted New Tuition per Student"]].values.tolist()
    tuition_table = Table([["Grade", "Students", "Current Tuition", "Adjusted Tuition"]] + tuition_data)
    tuition_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)
    ]))
    elements.append(Paragraph("<b>Tuition by Grade Level:</b>", styles['Heading2']))
    elements.append(tuition_table)

    # Strategic items table
    if not strategic_items_df.empty:
        strategic_items_data = strategic_items_df.values.tolist()
        strategic_table = Table([["Item", "Cost", "Description"]] + strategic_items_data)
        strategic_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)
        ]))
        elements.append(Paragraph("<b>Strategic Items:</b>", styles['Heading2']))
        elements.append(strategic_table)

    # Add graphs as images
    fig, ax = plt.subplots()
    df.plot(kind='bar', x='Grade', y='Total Tuition for Grade', ax=ax, title='Total Tuition by Grade')
    graph_path = "/tmp/graph.png"
    plt.savefig(graph_path, bbox_inches='tight')
    plt.close()
    elements.append(Image(graph_path, width=400, height=200))

    # Calculation summary
    elements.append(Paragraph("<b>Calculation Summary:</b>", styles['Heading2']))
    elements.append(Paragraph(summary_text, styles['Normal']))

    # Build the PDF
    doc.build(elements)
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

    tuition_data = {
        "Grade": grades,
        "Number of Students": num_students,
        "Current Tuition per Student": current_tuition,
        "Adjusted New Tuition per Student": [
            tuition * (1 + final_tuition_increase / 100) for tuition in current_tuition
        ],
    }
    df = pd.DataFrame(tuition_data)
    df["Total Tuition for Grade"] = df["Number of Students"] * df["Adjusted New Tuition per Student"]

    # Create strategic items DataFrame
    strategic_items_df = pd.DataFrame({
        "Strategic Item": strategic_item_names,
        "Cost ($)": strategic_items_costs,
        "Description": strategic_item_descriptions
    })

    # Generate PDF
    summary_text = f"""
    This report calculates the tuition projections for the upcoming academic year. It includes strategic items,
    adjustments by grade level, and financial aid impacts.
    """
    pdf_buffer = generate_pdf_with_graphs_and_tables(
        report_title, df, total_current_tuition, total_new_tuition,
        final_tuition_increase, (financial_aid / total_new_tuition) * 100 if total_new_tuition > 0 else 0.0,
        strategic_items_df, summary_text
    )

    st.download_button(
        label="Download Report as PDF",
        data=pdf_buffer,
        file_name="tuition_report.pdf",
        mime="application/pdf"
    )
