# Step 5: Previous Year's Total Expenses and KPIs
st.subheader("Step 5: Enter Previous Year's Total Expenses")
previous_expenses_input = st.text_input("Previous Year's Total Expenses ($)", "")
formatted_previous_expenses = format_input_as_currency(previous_expenses_input)

# Ensure ROI and RPI are defined before this step
roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01, value=3.32)
rpi_percentage = st.number_input("Rate of Productivity Increase (RPI) %", min_value=0.0, step=0.01, value=2.08)

try:
    previous_expenses = float(formatted_previous_expenses.replace(",", "").replace("$", ""))
except ValueError:
    previous_expenses = 0.0

if previous_expenses > 0:
    # Calculate KPIs
    total_tuition = sum(grades_data["num_students"]) * avg_tuition
    tuition_to_expenses_ratio = (total_tuition / previous_expenses) * 100
    total_compensation = sum(strategic_items["costs"])
    compensation_to_expenses_ratio = (total_compensation / previous_expenses) * 100

    # Estimate Next Year's Expenses
    total_strategic_items_cost = sum(strategic_items["costs"])
    expense_increase_oti = previous_expenses * (roi_percentage / 100 + rpi_percentage / 100)
    next_year_expenses = previous_expenses + expense_increase_oti + total_strategic_items_cost

    # Display KPIs and next year’s budget
    st.write("**Key Performance Indicators (KPIs):**")
    st.write(f"- Tuition-to-Expenses Ratio: {tuition_to_expenses_ratio:.2f}% (Target: 100%-102%)")
    st.write(f"- Compensation-to-Expenses Ratio: {compensation_to_expenses_ratio:.2f}% (Target: 70%-80%)")
    st.write(f"**Projected Next Year's Expenses:** {format_currency(next_year_expenses)}")
else:
    st.error("Please enter a valid value for the previous year's total expenses.")

# Step 6: Operations Tuition Increase (OTI) and Final Increase Calculation
st.subheader("Step 6: Operations Tuition Increase (OTI) and Final Increase Calculation")

oti = roi_percentage + rpi_percentage

if avg_tuition > 0:
    si_percentage = (total_strategic_items_cost / (sum(grades_data["num_students"]) * avg_tuition)) * 100
else:
    si_percentage = 0.0

final_tuition_increase = oti + si_percentage

st.write(
    f"The tuition increase includes:\n"
    f"- Operations Tuition Increase (OTI): {oti:.2f}%\n"
    f"- Strategic Items Contribution: {si_percentage:.2f}%\n"
    f"Total Tuition Increase: {final_tuition_increase:.2f}%."
)

# Step 7: Financial Aid (Tuition Assistance) Calculation
st.subheader("Step 7: Financial Aid (Tuition Assistance)")
financial_aid_input = st.text_input("Total Financial Aid ($)", "")
formatted_financial_aid = format_input_as_currency(financial_aid_input)
try:
    financial_aid = float(formatted_financial_aid.replace(",", "").replace("$", ""))
except ValueError:
    financial_aid = 0.0

# Calculate and Display Results
if st.button("Calculate New Tuition"):
    total_current_tuition = sum(
        [students * tuition for students, tuition in zip(grades_data["num_students"], grades_data["current_tuition"])]
    )
    total_new_tuition = total_current_tuition * (1 + final_tuition_increase / 100)
    tuition_assistance_ratio = (financial_aid / total_new_tuition) * 100 if total_new_tuition > 0 else 0.0

    st.session_state.calculated_values = {
        "total_current_tuition": total_current_tuition,
        "total_new_tuition": total_new_tuition,
        "final_tuition_increase": final_tuition_increase,
        "tuition_assistance_ratio": tuition_assistance_ratio,
        "tuition_to_expenses_ratio": tuition_to_expenses_ratio,
        "compensation_to_expenses_ratio": compensation_to_expenses_ratio,
        "next_year_expenses": next_year_expenses
    }

    st.subheader("Results")
    st.write(f"**Total Current Tuition:** {format_currency(total_current_tuition)}")
    st.write(f"**Total New Tuition:** {format_currency(total_new_tuition)}")
    st.write(f"**Tuition Assistance Ratio:** {tuition_assistance_ratio:.2f}%")
    st.write(f"**Projected Next Year's Expenses:** {format_currency(next_year_expenses)}")

    # Generate Tuition Table
    adjusted_tuition_values = [
        tuition * (1 + final_tuition_increase / 100) for tuition in grades_data["current_tuition"]
    ]
    tuition_data = {
        "Grade": grades_data["grades"],
        "Number of Students": grades_data["num_students"],
        "Current Tuition per Student": [format_currency(val) for val in grades_data["current_tuition"]],
        "Adjusted Tuition per Student": [format_currency(val) for val in adjusted_tuition_values],
        "Total Tuition per Grade": [
            format_currency(students * adj_tuition)
            for students, adj_tuition in zip(grades_data["num_students"], adjusted_tuition_values)
        ]
    }
    df = pd.DataFrame(tuition_data)
    st.table(df)

    # PDF Report Generation
    if st.button("Download PDF Report"):
        pdf_buffer = generate_pdf(
            report_title,
            df,
            total_current_tuition,
            total_new_tuition,
            final_tuition_increase,
            tuition_assistance_ratio,
            strategic_items_df,
            st.session_state.calculated_values,
            financial_aid,
            next_year_expenses,
            tuition_to_expenses_ratio,
            compensation_to_expenses_ratio
        )
        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="tuition_report.pdf",
            mime="application/pdf"
        )
