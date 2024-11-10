import streamlit as st
import pandas as pd
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap

# [Previous helper functions remain the same until the Results section]
# ... [Keep all the previous code until the "Calculate New Tuition" button]

# Initialize session state for calculations if not present
if "calculated_values" not in st.session_state:
    st.session_state.calculated_values = None

# Initialize adjusted tuition state if not present
if "adjusted_tuition" not in st.session_state:
    st.session_state.adjusted_tuition = None

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
    st.write(df[["Grade", "Number of Students", "Current Tuition per Student", "Adjusted New Tuition per Student", "Total Tuition for Grade"]])
    st.write(f"**Adjusted Total Tuition:** {format_currency(adjusted_total_tuition)}")
    st.write(f"**Difference from Target Total Tuition:** {format_currency(st.session_state.calculated_values['total_new_tuition'] - adjusted_total_tuition)}")
    st.write(f"**Updated Tuition Assistance Ratio:** {updated_tuition_assistance_ratio:.2f}%")

    # Generate PDF with updated values
    strategic_items_df = pd.DataFrame({
        "Strategic Item": strategic_items["names"],
        "Cost ($)": strategic_items["costs"],
        "Description": strategic_items["descriptions"]
    })

    pdf_buffer = generate_pdf(
        report_title,
        df,
        st.session_state.calculated_values['total_current_tuition'],
        adjusted_total_tuition,
        st.session_state.calculated_values['final_tuition_increase'],
        updated_tuition_assistance_ratio,
        strategic_items_df,
        "Updated summary of tuition adjustment calculations based on user inputs."
    )

    st.download_button(
        label="Download Updated Report as PDF",
        data=pdf_buffer,
        file_name="adjusted_tuition_report.pdf",
        mime="application/pdf"
    )
