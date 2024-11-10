import streamlit as st
import pandas as pd
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap

# Configure locale for currency formatting
locale.setlocale(locale.LC_ALL, '')

# Helper functions remain the same...

def main():
    st.title("Tuition Calculation Tool")

    # State management
    if "grades_data" not in st.session_state:
        st.session_state.grades_data = {"grades": [], "num_students": [], "current_tuition": [], "adjusted_tuition": []}
    
    if "strategic_items" not in st.session_state:
        st.session_state.strategic_items = {"names": [], "costs": [], "descriptions": []}

    # Step 1: Title for the Report
    report_title = st.text_input("Enter a Custom Title for the Report", "2025-26 Tuition Projection")

    # Step 2 & 3: Grade Levels, Tuition Rates, and Average Calculation
    num_grades = st.number_input("Number of Grade Levels", min_value=1, max_value=12, value=len(st.session_state.grades_data["grades"]), step=1)
    update_grades_data(num_grades)

    # Display and edit tuition data
    with st.form("tuition_form"):
        for i in range(num_grades):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.session_state.grades_data["grades"][i] = st.text_input(f"Grade Level {i+1} Name", st.session_state.grades_data["grades"][i])
            with col2:
                st.session_state.grades_data["num_students"][i] = st.number_input(
                    f"Number of Students in {st.session_state.grades_data['grades'][i]}", 
                    min_value=0, value=st.session_state.grades_data["num_students"][i], step=1
                )
            with col3:
                st.session_state.grades_data["current_tuition"][i] = st.number_input(
                    f"Current Tuition per Student in {st.session_state.grades_data['grades'][i]} ($)", 
                    min_value=0.0, value=st.session_state.grades_data["current_tuition"][i]
                )
        
        submitted = st.form_submit_button("Update Data")
        if submitted:
            calculate_average_tuition()  # Recalculate average tuition upon form submission

    # Step 4: Strategic Items
    num_items = st.number_input("Number of Strategic Items", min_value=0, max_value=10, value=len(st.session_state.strategic_items["names"]), step=1)
    update_strategic_items(num_items)

    # Step 5: Previous Year’s Total Expenses
    previous_expenses = st.number_input("Previous Year's Total Expenses ($)", min_value=0.0, step=1.0)

    # Step 6: Tuition Increase Calculation
    roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01, value=3.32)
    rpi_percentage = st.number_input("Rate of Productivity Increase (RPI) %", min_value=0.0, step=0.01, value=2.08)
    oti = roi_percentage + rpi_percentage
    total_strategic_items_cost = sum(st.session_state.strategic_items["costs"])
    si_percentage = (total_strategic_items_cost / (sum(st.session_state.grades_data["num_students"]) * avg_tuition())) * 100 if avg_tuition() > 0 else 0.0
    final_tuition_increase = oti + si_percentage

    # Step 7: Financial Aid
    financial_aid = st.number_input("Total Financial Aid ($)", min_value=0.0, step=1.0)

    # Display Results Button
    if st.button("Calculate New Tuition"):
        display_results(report_title, final_tuition_increase, financial_aid, previous_expenses)

def update_grades_data(num_grades):
    while len(st.session_state.grades_data["grades"]) < num_grades:
        st.session_state.grades_data["grades"].append(f"Grade {len(st.session_state.grades_data['grades']) + 1}")
        st.session_state.grades_data["num_students"].append(0)
        st.session_state.grades_data["current_tuition"].append(0.0)
        st.session_state.grades_data["adjusted_tuition"].append(0.0)
    while len(st.session_state.grades_data["grades"]) > num_grades:
        st.session_state.grades_data["grades"].pop()
        st.session_state.grades_data["num_students"].pop()
        st.session_state.grades_data["current_tuition"].pop()
        st.session_state.grades_data["adjusted_tuition"].pop()

def update_strategic_items(num_items):
    while len(st.session_state.strategic_items["names"]) < num_items:
        st.session_state.strategic_items["names"].append(f"Item {len(st.session_state.strategic_items['names']) + 1}")
        st.session_state.strategic_items["costs"].append(0.0)
        st.session_state.strategic_items["descriptions"].append("")
    while len(st.session_state.strategic_items["names"]) > num_items:
        st.session_state.strategic_items["names"].pop()
        st.session_state.strategic_items["costs"].pop()
        st.session_state.strategic_items["descriptions"].pop()

def avg_tuition():
    students = sum(st.session_state.grades_data["num_students"])
    total_tuition = sum([students * tuition for students, tuition in zip(st.session_state.grades_data["num_students"], st.session_state.grades_data["current_tuition"])])
    return total_tuition / students if students > 0 else 0

def calculate_average_tuition():
    avg_tuition_val = avg_tuition()
    st.write(f"Automatically Calculated Average Tuition per Student: {format_currency(avg_tuition_val)}")

def display_results(report_title, final_tuition_increase, financial_aid, previous_expenses):
    # Total calculations here
    total_current_tuition = sum([students * tuition for students, tuition in zip(st.session_state.grades_data["num_students"], st.session_state.grades_data["current_tuition"])])
    total_new_tuition = total_current_tuition * (1 + final_tuition_increase / 100)
    tuition_assistance_ratio = (financial_aid / total_new_tuition) * 100 if total_new_tuition > 0 else 0.0

    st.subheader("Results")
    st.write(f"**Report Title:** {report_title}")
    st.write(f"**Total Current Tuition:** {format_currency(total_current_tuition)}")
    st.write(f"**Total New Tuition:** {format_currency(total_new_tuition)}")
    st.write(f"**Final Tuition Increase Percentage:** {final_tuition_increase:.2f}%")
    st.write(f"**Tuition Assistance Ratio:** {tuition_assistance_ratio:.2f}%")

    # Display and edit adjusted tuition
    df = pd.DataFrame({
        "Grade": st.session_state.grades_data["grades"],
        "Number of Students": st.session_state.grades_data["num_students"],
        "Current Tuition per Student": [format_currency(tuition) for tuition in st.session_state.grades_data["current_tuition"]],
        "Adjusted New Tuition per Student": [format_currency(tuition * (1 + final_tuition_increase / 100)) for tuition in st.session_state.grades_data["current_tuition"]]
    })
    
    edited_df = st.data_editor(df)
    if edited_df is not None:
        for i, row in edited_df.iterrows():
            # Assuming the adjusted tuition is in the last column
            st.session_state.grades_data["adjusted_tuition"][i] = float(row.iloc[-1].replace("$", "").replace(",", ""))
    
        st.write("Updated Tuition Table:")
        st.write(edited_df)
    
        # Update summary with adjusted values
        total_adjusted_tuition = sum(edited_df["Adjusted New Tuition per Student"] * edited_df["Number of Students"])
        st.write(f"**Adjusted Total New Tuition:** {format_currency(total_adjusted_tuition)}")
        st.write(f"**Difference from Initial Calculation:** {format_currency(total_new_tuition - total_adjusted_tuition)}")

    # Generate and download PDF with updated values
    strategic_items_df = pd.DataFrame({
        "Strategic Item": st.session_state.strategic_items["names"],
        "Cost ($)": st.session_state.strategic_items["costs"],
        "Description": st.session_state.strategic_items["descriptions"],
    })
    
    pdf_buffer = generate_pdf(
        report_title, edited_df, total_current_tuition, total_adjusted_tuition, 
        final_tuition_increase, tuition_assistance_ratio, strategic_items_df,
        "This report includes the tuition adjustments made by the user."
    )
    
    st.download_button(
        label="Download PDF Report",
        data=pdf_buffer.getvalue(),
        file_name="adjusted_tuition_report.pdf",
        mime="application/pdf",
    )

if __name__ == "__main__":
    main()
