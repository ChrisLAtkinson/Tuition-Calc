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
    # ... (PDF generation remains the same)

# Streamlit App Start
st.title("Tuition Calculation Tool")

# ... (Steps 1 through 7 remain the same)

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
    edited_df = pd.DataFrame(json.loads(st.session_state['adjusted_tuition_df']))

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
