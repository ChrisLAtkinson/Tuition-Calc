import streamlit as st
import pandas as pd
import plotly.express as px
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import textwrap

# Configure locale for currency formatting
locale.setlocale(locale.LC_ALL, '')

# Helper function to format numbers as currency
def format_currency(value):
    try:
        return locale.currency(value, grouping=True)
    except:
        return f"${value:,.2f}"

# Function to generate a comprehensive PDF report
def generate_comprehensive_pdf(report_title, df, total_current_tuition, total_new_tuition, 
                                adjusted_total_tuition, final_tuition_increase, 
                                adjusted_final_tuition_increase, tuition_assistance_ratio, 
                                adjusted_tuition_assistance_ratio, strategic_items_df, 
                                summary_text, bar_chart, line_chart):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title Page
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, height - 50, f"{report_title}")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 80, "A Comprehensive Tuition Analysis Report")
    pdf.drawString(50, height - 100, "Generated using Tuition Calculation Tool")
    pdf.showPage()

    # Initial Results Summary
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Initial Tuition Summary")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 80, f"Total Current Tuition: {format_currency(total_current_tuition)}")
    pdf.drawString(50, height - 100, f"Projected Total New Tuition: {format_currency(total_new_tuition)}")
    pdf.drawString(50, height - 120, f"Final Tuition Increase Percentage: {final_tuition_increase:.2f}%")
    pdf.drawString(50, height - 140, f"Tuition Assistance Ratio: {tuition_assistance_ratio:.2f}%")
    pdf.showPage()

    # Adjusted Results Summary
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Adjusted Tuition Summary")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 80, f"Adjusted Total Tuition: {format_currency(adjusted_total_tuition)}")
    pdf.drawString(50, height - 100, f"Adjusted Final Tuition Increase Percentage: {adjusted_final_tuition_increase:.2f}%")
    pdf.drawString(50, height - 120, f"Adjusted Tuition Assistance Ratio: {adjusted_tuition_assistance_ratio:.2f}%")
    pdf.showPage()

    # Tuition by Grade Level
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Tuition by Grade Level")
    row_y = height - 80
    pdf.setFont("Helvetica", 10)
    for i, row in df.iterrows():
        pdf.drawString(50, row_y, f"{row['Grade']}: {row['Number of Students']} students, "
                                  f"Current Tuition: {format_currency(row['Current Tuition per Student'])}, "
                                  f"Adjusted Tuition: {format_currency(row['Adjusted New Tuition per Student'])}")
        row_y -= 15
        if row_y < 50:
            pdf.showPage()
            row_y = height - 50

    # Strategic Items Summary
    if not strategic_items_df.empty:
        pdf.showPage()
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, height - 50, "Strategic Items Summary")
        row_y = height - 80
        pdf.setFont("Helvetica", 10)
        for i, row in strategic_items_df.iterrows():
            pdf.drawString(50, row_y, f"{row['Strategic Item']}: {format_currency(row['Cost ($)'])}")
            row_y -= 15
            description_lines = textwrap.wrap(row['Description'], width=90)
            for line in description_lines:
                pdf.drawString(70, row_y, line)
                row_y -= 15
            if row_y < 50:
                pdf.showPage()
                row_y = height - 50

    # Charts and Graphs
    pdf.showPage()
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Charts and Graphs")
    
    # Save bar chart as an image and embed it
    bar_chart_image = BytesIO()
    bar_chart.write_image(bar_chart_image, format="PNG")
    bar_chart_image.seek(0)
    bar_chart_path = "bar_chart.png"
    with open(bar_chart_path, "wb") as f:
        f.write(bar_chart_image.read())
    pdf.drawImage(bar_chart_path, 50, height - 350, width=500, height=300)

    # Save line chart as an image and embed it
    pdf.showPage()
    line_chart_image = BytesIO()
    line_chart.write_image(line_chart_image, format="PNG")
    line_chart_image.seek(0)
    line_chart_path = "line_chart.png"
    with open(line_chart_path, "wb") as f:
        f.write(line_chart_image.read())
    pdf.drawImage(line_chart_path, 50, height - 350, width=500, height=300)

    # Detailed Summary of Calculations
    pdf.showPage()
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Detailed Summary of Calculations")
    pdf.setFont("Helvetica", 12)
    row_y = height - 80
    for line in textwrap.wrap(summary_text, width=90):
        pdf.drawString(50, row_y, line)
        row_y -= 15
        if row_y < 50:
            pdf.showPage()
            row_y = height - 50

    # Finalize PDF
    pdf.save()
    buffer.seek(0)
    return buffer

# Streamlit App Start
st.title("Tuition Calculation Tool")

# Placeholder sections to collect inputs
st.subheader("Step 1: Enter Grade and Tuition Data")
grades = ["Grade 1", "Grade 2"]
num_students = [30, 40]
current_tuition = [10000, 12000]

# Perform calculations for initial results
total_current_tuition = sum([students * tuition for students, tuition in zip(num_students, current_tuition)])
final_tuition_increase = 8.5
total_new_tuition = total_current_tuition * (1 + final_tuition_increase / 100)

# Create data frame
tuition_data = {
    "Grade": grades,
    "Number of Students": num_students,
    "Current Tuition per Student": current_tuition,
    "Adjusted New Tuition per Student": [tuition * 1.1 for tuition in current_tuition]
}
df = pd.DataFrame(tuition_data)
df["Total Tuition for Grade"] = df["Number of Students"] * df["Adjusted New Tuition per Student"]

# Create bar chart
bar_chart = px.bar(
    df,
    x="Grade",
    y="Total Tuition for Grade",
    title="Total Tuition by Grade",
    labels={"Total Tuition for Grade": "Total Tuition ($)", "Grade": "Grade Level"},
    text="Total Tuition for Grade"
)

# Create line chart
line_chart = px.line(
    df,
    x="Grade",
    y=["Current Tuition per Student", "Adjusted New Tuition per Student"],
    title="Tuition Comparison",
    labels={"value": "Tuition ($)", "Grade": "Grade Level", "variable": "Type"}
)

# Generate PDF
strategic_items_df = pd.DataFrame({
    "Strategic Item": ["New Facilities", "Staff Training"],
    "Cost ($)": [50000, 20000],
    "Description": ["New classrooms and labs", "Advanced teacher training programs"]
})
summary_text = "This report provides a detailed analysis of current and adjusted tuition data by grade level."
pdf_buffer = generate_comprehensive_pdf(
    "Comprehensive Tuition Report",
    df,
    total_current_tuition,
    total_new_tuition,
    df["Total Tuition for Grade"].sum(),
    final_tuition_increase,
    10.0,  # Example adjusted increase percentage
    15.0,  # Example initial assistance ratio
    13.0,  # Example adjusted assistance ratio
    strategic_items_df,
    summary_text,
    bar_chart,
    line_chart
)

st.download_button(
    label="Download Comprehensive PDF Report",
    data=pdf_buffer,
    file_name="comprehensive_tuition_report.pdf",
    mime="application/pdf"
)
