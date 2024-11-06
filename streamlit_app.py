import streamlit as st
import pandas as pd
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json

# Configure locale for currency formatting
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Helper function to format numbers as currency
def format_currency(value):
    try:
        return locale.currency(value, grouping=True)
    except Exception:
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

    # Add content (implement remaining PDF content generation here)
    pdf.save()
    buffer.seek(0)
    return buffer

st.title("Tuition Calculation Tool")

# Step 1: Enter a Custom Title for the Report
report_title = st.text_input("Enter a Custom Title for the Report", "2025-26 Tuition Projection")

# Example inputs (replace these with dynamic user inputs)
grades = ["Grade 1", "Grade 2", "Grade 3"]
num_students = [30, 25, 20]
current_tuition = [10000, 12000, 15000]
final_tuition_increase = 5  # in percentage
financial_aid = 50000  # example value
strategic_item_names = ["New Lab Equipment", "Library Upgrade"]
strategic_items_costs = [20000, 15000]
strategic_item_descriptions = ["Lab equipment for STEM programs", "Enhancing library resources"]

# Step 8: Calculate New Tuition and Display Results
if st.button("Calculate New Tuition"):
    try:
        total_current_tuition = sum(students * tuition for students, tuition in zip(num_students, current_tuition))
        total_new_tuition = total_current_tuition * (1 + final_tuition_increase / 100)
        new_tuition_per_student = [tuition * (1 + final_tuition_increase / 100) for tuition in current_tuition]
        tuition_assistance_ratio = (financial_aid / total_new_tuition) * 100 if total_new_tuition > 0 else 0.0

        # Display Summary Prior to Interactive Adjustment
        st.subheader("Summary Prior to Interactive Adjustment")
        st.write(f"**Report Title:** {report_title}")
        st.write(f"**Total Current Tuition:** {format_currency(total_current_tuition)}")
        st.write(f"**Total New Tuition:** {format_currency(total_new_tuition)}")
        st.write(f"**Final Tuition Increase Percentage:** {final_tuition_increase:.2f}%")
        st.write(f"**Tuition Assistance Ratio:** {tuition_assistance_ratio:.2f}%")

        # Prepare DataFrame for editing
        tuition_data = {
            "Grade": grades,
            "Number of Students": num_students,
            "Current Tuition per Student": current_tuition,
            "Adjusted New Tuition per Student": new_tuition_per_student,
        }
        df = pd.DataFrame(tuition_data)

        # Interactive Adjustment Table
        st.subheader("Adjust Tuition by Grade Level")
        edited_df = st.data_editor(df, use_container_width=True)

        # Calculate adjusted totals and differences
        edited_df["Total Tuition for Grade"] = (
            edited_df["Number of Students"] * edited_df["Adjusted New Tuition per Student"]
        )
        adjusted_total_tuition = edited_df["Total Tuition for Grade"].sum()

        st.write("**Adjusted Tuition Data:**")
        st.dataframe(edited_df)
        st.write(f"**Adjusted Total Tuition:** {format_currency(adjusted_total_tuition)}")
        st.write(f"**Difference from Target Total Tuition:** {format_currency(total_new_tuition - adjusted_total_tuition)}")

        # Generate the PDF report
        strategic_items_df = pd.DataFrame({
            "Strategic Item": strategic_item_names,
            "Cost ($)": strategic_items_costs,
            "Description": strategic_item_descriptions,
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
    except Exception as e:
        st.error(f"An error occurred: {e}")
