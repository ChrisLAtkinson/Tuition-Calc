import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap

# ... (your previous code remains unchanged up to this point)

# Step 8: Calculate New Tuition and Display Results
if st.button("Calculate New Tuition"):
    total_current_tuition = sum([students * tuition for students, tuition in zip(num_students, current_tuition)])
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

    # Interactive Adjustment Table
    st.subheader("Adjust Tuition by Grade Level")
    tuition_data = {
        "Grade": grades,
        "Number of Students": num_students,
        "Current Tuition per Student": current_tuition,
        "Adjusted New Tuition per Student": new_tuition_per_student
    }
    df = pd.DataFrame(tuition_data)

    # Use experimental_data_editor for interactive editing
    edited_df = st.experimental_data_editor(df, key="tuition_editor")

    # Recalculate based on edited data
    edited_df["Adjusted New Tuition per Student"] = edited_df["Adjusted New Tuition per Student"].replace('', 0).astype(float)
    edited_df["Total Tuition for Grade"] = edited_df["Number of Students"] * edited_df["Adjusted New Tuition per Student"]
    adjusted_total_tuition = edited_df["Total Tuition for Grade"].sum()

    # Show updated table
    st.write(edited_df[["Grade", "Number of Students", "Current Tuition per Student", "Adjusted New Tuition per Student", "Total Tuition for Grade"]])

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
