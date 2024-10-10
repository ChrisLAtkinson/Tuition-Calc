import streamlit as st
import pandas as pd
import plotly.graph_objects as go  # For interactive graphs
import locale
from io import StringIO  # For handling text output as a downloadable file

# Configure locale to display currency with commas and two decimal places
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
        input_value = input_value.replace(",", "").replace("$", "")
        value = float(input_value)
        return f"${value:,.2f}"
    except ValueError:
        return ""

# Function to generate a downloadable summary of the results
def generate_downloadable_summary(report_title, df, total_current_tuition, total_new_tuition, avg_increase_percentage, tuition_assistance_ratio, strategic_items_df):
    output = StringIO()
    output.write(f"Report Title: {report_title}\n")
    output.write(f"Total Current Tuition: {format_currency(total_current_tuition)}\n")
    output.write(f"Total New Tuition: {format_currency(total_new_tuition)}\n")
    output.write(f"Average Tuition Increase Percentage: {avg_increase_percentage:.2f}%\n")
    output.write(f"Tuition Assistance Ratio: {tuition_assistance_ratio:.2f}%\n")
    output.write("\nTuition by Grade Level:\n")
    output.write(df.to_string(index=False))
    output.write("\n\nStrategic Items and Costs:\n")
    output.write(strategic_items_df.to_string(index=False))
    return output.getvalue()

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
    
    tuition_input = st.text_input(f"Current Tuition per Student in {grade} ($)", "")
    formatted_tuition = format_input_as_currency(tuition_input)
    st.text(f"Formatted: {formatted_tuition}")
    
    if formatted_tuition:
        tuition = float(formatted_tuition.replace(",", "").replace("$", ""))
    else:
        tuition = 0.0

    grades.append(grade)
    num_students.append(students)
    current_tuition.append(tuition)

# Step 3: Add Strategic Items
st.subheader("Step 3: Add Strategic Items")
strategic_items = []
strategic_item_names = []
num_items = st.number_input("Number of Strategic Items", min_value=0, max_value=10, value=0)

for i in range(num_items):
    item_name = st.text_input(f"Strategic Item {i+1} Name", f"Item {i+1}")
    strategic_item_names.append(item_name)
    
    item_cost_input = st.text_input(f"Cost of {item_name} ($)", "")
    formatted_item_cost = format_input_as_currency(item_cost_input)
    st.text(f"Formatted: {formatted_item_cost}")

    if formatted_item_cost:
        item_cost = float(formatted_item_cost.replace(",", "").replace("$", ""))
    else:
        item_cost = 0.0

    strategic_items.append(item_cost)

# Step 4: Previous Year's Expense Budget
st.subheader("Step 4: Enter the Previous Year's Total Expenses")
total_expenses_input = st.text_input("Total Expenses ($)", "")
formatted_expenses = format_input_as_currency(total_expenses_input)
st.text(f"Formatted: {formatted_expenses}")

if formatted_expenses:
    previous_expenses = float(formatted_expenses.replace(",", "").replace("$", ""))
else:
    previous_expenses = 0.0

# Step 5: Operations Tuition Increase (OTI) Calculation
st.subheader("Step 5: Operations Tuition Increase (OTI) Calculation")
roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01)
efficiency_rate = 2.08 / 100  # Fixed rate of efficiency

# Step 6: Compensation Percentage
st.subheader("Step 6: Enter Compensation as a Percentage of Expenses")
compensation_percentage = st.number_input("Compensation Percentage (%)", min_value=0.0, max_value=100.0, value=70.0, step=0.01)

# Step 7: Financial Aid (Tuition Assistance) Calculation
st.subheader("Step 7: Financial Aid (Tuition Assistance)")
financial_aid_input = st.text_input("Total Financial Aid ($)", "")
formatted_financial_aid = format_input_as_currency(financial_aid_input)
st.text(f"Formatted: {formatted_financial_aid}")

if formatted_financial_aid:
    financial_aid = float(formatted_financial_aid.replace(",", "").replace("$", ""))
else:
    financial_aid = 0.0

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

        # Show strategic items with names and costs
        st.subheader("Strategic Items")
        strategic_items_df = pd.DataFrame({
            "Strategic Item": strategic_item_names,
            "Cost ($)": [format_currency(cost) for cost in strategic_items]
        })
        st.write(strategic_items_df)

        # Create an interactive side-by-side bar graph using Plotly
        st.subheader("Interactive Tuition Increase Graph")
        fig = go.Figure(data=[
            go.Bar(name='Current Tuition', x=grades, y=[float(tuition.replace('$', '').replace(',', '')) for tuition in df["Current Tuition per Student"]], marker_color='skyblue'),
            go.Bar(name='New Tuition', x=grades, y=[float(tuition.replace('$', '').replace(',', '')) for tuition in df["New Tuition per Student"]], marker_color='orange')
        ])
        # Change the bar mode
        fig.update_layout(barmode='group', title_text="Current vs New Tuition by Grade Level")
        st.plotly_chart(fig)

        # Show the total results in a formatted table
        total_table = pd.DataFrame({
            "Total Current Tuition": [format_currency(total_current_tuition)],
            "Total New Tuition": [format_currency(total_new_tuition)],
            "Average Increase %": [f"{avg_increase_percentage:.2f}%"],
            "Tuition Assistance Ratio": [f"{tuition_assistance_ratio:.2f}%"]
        })

        st.subheader("Overall Summary")
        st.table(total_table)

        # Generate the downloadable summary
        summary_text = generate_downloadable_summary(report_title, df, total_current_tuition, total_new_tuition, avg_increase_percentage, tuition_assistance_ratio, strategic_items_df)
        
        # Create a download button for the report
        st.download_button(
            label="Download Report",
            data=summary_text,
            file_name="tuition_report.txt",
            mime="text/plain"
        )
