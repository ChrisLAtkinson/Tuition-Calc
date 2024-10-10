import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import locale

# Configure locale to display currency with commas and two decimal places
locale.setlocale(locale.LC_ALL, '')

# Helper function to format numbers as currency
def format_currency(value):
    try:
        return locale.currency(value, grouping=True)
    except:
        return f"${value:,.2f}"

# Title of the app
st.title("Tuition Calculation Tool")

# Step 1: Enter a Custom Title for the Report
report_title = st.text_input("Enter a Custom Title for the Report", "2025-26 Tuition Projection")

st.subheader("Step 2: Add Custom Grade Levels and Tuition Rates")
grades = []
num_students = []
current_tuition = []
num_grades = st.number_input("Number of Grade Levels", min_value=1, max_value=12, value=1)

for i in range(num_grades):
    grade = st.text_input(f"Grade Level {i+1} Name", f"Grade {i+1}")
    students = st.number_input(f"Number of Students in {grade}", min_value=1, step=1)
    tuition = st.number_input(f"Current Tuition per Student in {grade} ($)", min_value=0.0, step=0.01, format="%.2f")
    
    grades.append(grade)
    num_students.append(students)
    current_tuition.append(tuition)

# Step 3: Add Strategic Items
st.subheader("Step 3: Add Strategic Items")
strategic_items = []
num_items = st.number_input("Number of Strategic Items", min_value=0, max_value=10, value=0)

for i in range(num_items):
    item_name = st.text_input(f"Strategic Item {i+1} Name", f"Item {i+1}")
    item_cost = st.number_input(f"Cost of {item_name} ($)", min_value=0.0, step=0.01, format="%.2f")
    strategic_items.append(item_cost)

# Step 4: Previous Year's Expense Budget
st.subheader("Step 4: Enter the Previous Year's Total Expenses")
previous_expenses = st.number_input("Total Expenses ($)", min_value=0.0, step=0.01, format="%.2f")

# Step 5: Operations Tuition Increase (OTI) Calculation
st.subheader("Step 5: Operations Tuition Increase (OTI) Calculation")
roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01)
efficiency_rate = 2.08 / 100  # Fixed rate of efficiency

# Step 6: Compensation Percentage
st.subheader("Step 6: Enter Compensation as a Percentage of Expenses")
compensation_percentage = st.number_input("Compensation Percentage (%)", min_value=0.0, max_value=100.0, value=70.0, step=0.01)

# Step 7: Financial Aid (Tuition Assistance) Calculation
st.subheader("Step 7: Financial Aid (Tuition Assistance)")
financial_aid = st.number_input("Total Financial Aid ($)", min_value=0.0, step=0.01, format="%.2f")

# Calculate new tuition with average increase
if st.button("Calculate New Tuition"):
    # Prevent division by zero or missing data issues
    if sum(num_students) == 0 or len(current_tuition) == 0:
        st.error("Please provide valid inputs for all grade levels.")
    else:
        total_current_tuition = sum([students * tuition for students, tuition in zip(num_students, current_tuition)])
        total_students = sum(num_students)
        total_strategic_costs = sum(strategic_items)

        adjusted_inflation = roi_percentage / 100 + efficiency_rate
        total_new_tuition = total_current_tuition + (total_current_tuition * adjusted_inflation) + total_strategic_costs
        
        avg_increase_percentage = ((total_new_tuition - total_current_tuition) / total_current_tuition) * 100 if total_current_tuition > 0 else 0

        # Calculate tuition assistance ratio
        tuition_assistance_ratio = (financial_aid / total_new_tuition) * 100 if total_new_tuition > 0 else 0

        # Display Results
        st.subheader("Results")
        st.write(f"**Report Title:** {report_title}")
        st.write(f"**Total Current Tuition:** {format_currency(total_current_tuition)}")
        st.write(f"**Total New Tuition (with average increase):** {format_currency(total_new_tuition)}")
        st.write(f"**Average Tuition Increase Percentage:** {avg_increase_percentage:.2f}%")
        st.write(f"**Tuition Assistance Ratio:** {tuition_assistance_ratio:.2f}%")

        # Word summary of how the results were gathered
        st.write("""
        ### Summary of Calculation:
        The total current tuition was calculated based on the sum of tuition rates per student for each grade level. 
        The new tuition was calculated by applying an inflation rate (Rate of Inflation + 2.08% Efficiency Rate) to the total current tuition. 
        Additionally, strategic costs were distributed across all students. The average tuition increase percentage was then applied to each grade.
        The tuition assistance ratio represents the percentage of the new tuition allocated to financial aid.
        """)

        # Create a DataFrame for the tuition by grade level
        tuition_data = {
            "Grade": grades,
            "Number of Students": num_students,
            "Current Tuition per Student": [format_currency(tuition) for tuition in current_tuition],
        }

        df = pd.DataFrame(tuition_data)
        df["Total Current Tuition"] = [format_currency(students * tuition) for students, tuition in zip(num_students, current_tuition)]
        df["New Tuition per Student"] = [format_currency(tuition * (1 + avg_increase_percentage / 100)) for tuition in current_tuition]
        df["Increase per Student"] = [format_currency((tuition * (1 + avg_increase_percentage / 100)) - tuition) for tuition in current_tuition]

        # Show the table of results
        st.subheader("Tuition by Grade Level")
        st.write(df)

        # Plot graph for current and new tuition per grade
        st.subheader("Tuition Increase Graph")
        fig, ax = plt.subplots()
        ax.bar(df["Grade"], [float(tuition.replace('$', '').replace(',', '')) for tuition in df["Current Tuition per Student"]], label="Current Tuition", color="skyblue")
        ax.bar(df["Grade"], [float(tuition.replace('$', '').replace(',', '')) for tuition in df["New Tuition per Student"]], label="New Tuition", color="orange", alpha=0.7)
        ax.set_ylabel("Tuition ($)")
        ax.set_title("Current vs New Tuition by Grade Level")
        plt.xticks(rotation=45)
        ax.legend()

        st.pyplot(fig)

        # Show the total results in a formatted table
        total_table = pd.DataFrame({
            "Total Current Tuition": [format_currency(total_current_tuition)],
            "Total New Tuition": [format_currency(total_new_tuition)],
            "Average Increase %": [f"{avg_increase_percentage:.2f}%"],
            "Tuition Assistance Ratio": [f"{tuition_assistance_ratio:.2f}%"]
        })

        st.subheader("Overall Summary")
        st.table(total_table)

        # Show a breakdown of strategic costs and other items
        st.subheader("Strategic Items and Costs")
        strategic_costs_df = pd.DataFrame({
            "Strategic Item": [f"Item {i+1}" for i in range(num_items)],
            "Cost ($)": [format_currency(cost) for cost in strategic_items]
        })
        st.write(strategic_costs_df)
