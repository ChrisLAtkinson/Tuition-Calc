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

# Function to generate a downloadable PDF report
def generate_pdf(report_title, df, total_current_tuition, total_new_tuition, avg_increase_percentage, tuition_assistance_ratio, strategic_items_df, summary_text):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title of the report
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, f"Report Title: {report_title}")
    # [Add further details and finalize PDF]

    pdf.save()
    buffer.seek(0)
    return buffer

st.title("Tuition Calculation Tool")

# Inputs collected as before
# [Omitting the initial data input steps for brevity]

if st.button("Calculate New Tuition"):
    # Process calculations here as before
    # [Omitting calculation steps for brevity]

    # Define DataFrame for interactive adjustment
    if 'tuition_data' not in st.session_state or st.session_state.recalculate:
        st.session_state.tuition_data = {
            "Grade": grades,
            "Number of Students": num_students,
            "Current Tuition per Student": current_tuition,
            "Adjusted New Tuition per Student": new_tuition_per_student
        }

    df = pd.DataFrame(st.session_state.tuition_data)

    # Interactive adjustment
    for i in range(len(df)):
        df.at[i, "Adjusted New Tuition per Student"] = st.number_input(
            f"Adjusted Tuition for {df.at[i, 'Grade']}",
            value=df.at[i, "Adjusted New Tuition per Student"],
            min_value=0.0,
            step=0.01
        )
    
    # Update session state after adjustments
    st.session_state.tuition_data = df.to_dict()

    # Recalculate totals and display adjusted data
    df["Total Tuition for Grade"] = df["Number of Students"] * df["Adjusted New Tuition per Student"]
    st.write(df)
    # [Continue with additional calculations and outputs]

    # PDF generation and download button as before
    # [Omitting for brevity]

# To ensure session_state is reset appropriately if needed
if 'recalculate' not in st.session_state:
    st.session_state.recalculate = False

# Button to reset data
if st.button("Reset Data"):
    st.session_state.recalculate = True
