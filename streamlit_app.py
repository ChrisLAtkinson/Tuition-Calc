import streamlit as st
import pandas as pd
import locale

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

# Streamlit App Start
st.title("Tuition Adjustment Tool")

# Step 1: Enter a Custom Title for the Report
st.subheader("Step 1: Enter a Custom Title for the Report")
report_title = st.text_input("Enter a Custom Title for the Report", "2025-26 Tuition Projection")

# Step 2: Add Custom Grade Levels and Tuition Rates
st.subheader("Step 2: Add Custom Grade Levels and Tuition Rates")
grades = []
num_students = []
current_tuition = []
num_grades = st.number_input("Number of Grade Levels", min_value=1, max_value=12, value=1, step=1)

for i in range(num_grades):
    grade = st.text_input(f"Grade Level {i+1} Name", f"Grade {i+1}")
    students = st.number_input(f"Number of Students in {grade}", min_value=0, step=1, value=0)
    tuition_input = st.text_input(f"Current Tuition per Student in {grade} ($)", "")
    formatted_tuition = format_input_as_currency(tuition_input)
    st.text(f"Formatted Tuition: {formatted_tuition}")
    tuition = float(formatted_tuition.replace(",", "").replace("$", "")) if formatted_tuition else 0.0
    grades.append(grade)
    num_students.append(students)
    current_tuition.append(tuition)

# Step 3: Automatically Calculate Average Tuition
st.subheader("Step 3: Automatically Calculate Average Tuition")
if sum(num_students) > 0:
    total_tuition = sum([students * tuition for students, tuition in zip(num_students, current_tuition)])
    avg_tuition = total_tuition / sum(num_students)
    st.text(f"Automatically Calculated Average Tuition per Student: {format_currency(avg_tuition)}")
else:
    avg_tuition = 0.0
    st.error("Please enter valid student numbers and tuition rates to calculate average tuition.")

# Step 4: Calculate New Tuition and Display Results
if st.button("Calculate New Tuition"):
    # Mock calculation of a tuition increase (for demonstration purposes)
    tuition_increase_percentage = 5.0  # Example value
    new_tuition_per_student = [(tuition * (1 + tuition_increase_percentage / 100)) for tuition in current_tuition]
    
    # Interactive Adjustment Table
    st.subheader("Adjust Tuition by Grade Level")
    tuition_data = {
        "Grade": grades,
        "Number of Students": num_students,
        "Current Tuition per Student": current_tuition,
        "Adjusted New Tuition per Student": new_tuition_per_student
    }
    df = pd.DataFrame(tuition_data)
    
    # Collect adjusted tuition inputs directly into the DataFrame
    adjusted_tuition_values = []
    for i in range(len(grades)):
        adjusted_tuition = st.number_input(
            f"Adjusted Tuition for {grades[i]}",
            value=df.at[i, "Adjusted New Tuition per Student"],
            min_value=0.0,
            step=0.01,
            key=f"adjusted_tuition_{i}"  # Use unique keys to retain values
        )
        adjusted_tuition_values.append(adjusted_tuition)

    # Update DataFrame with adjusted tuition values
    df["Adjusted New Tuition per Student"] = adjusted_tuition_values
    df["Total Tuition for Grade"] = df["Number of Students"] * df["Adjusted New Tuition per Student"]

    # Display the updated DataFrame
    st.write(df[["Grade", "Number of Students", "Current Tuition per Student", "Adjusted New Tuition per Student", "Total Tuition for Grade"]])

    # Calculate adjusted totals and differences
    adjusted_total_tuition = df["Total Tuition for Grade"].sum()
    st.write(f"**Adjusted Total Tuition:** {format_currency(adjusted_total_tuition)}")

    # Mock target tuition for difference calculation
    target_total_tuition = total_tuition * (1 + tuition_increase_percentage / 100)  # Example target
    st.write(f"**Difference from Target Total Tuition:** {format_currency(target_total_tuition - adjusted_total_tuition)}")
