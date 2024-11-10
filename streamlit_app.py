import streamlit as st
import pandas as pd

# Helper functions
def format_currency(value):
    """Formats a number as currency."""
    return f"${value:,.2f}"

def format_input_as_currency(input_value):
    """Converts and formats user input as currency."""
    try:
        if not input_value:
            return ""
        input_value = input_value.replace(",", "").replace("$", "")
        value = float(input_value)
        return f"${value:,.2f}"
    except ValueError:
        return ""

def format_percentage(value):
    """Formats a number as a percentage."""
    return f"{value:.2f}%"

# Initialize session state
if "grades_data" not in st.session_state:
    st.session_state.grades_data = {"grades": [], "num_students": [], "current_tuition": []}

if "strategic_items" not in st.session_state:
    st.session_state.strategic_items = {"names": [], "costs": [], "descriptions": []}

if "calculated_values" not in st.session_state:
    st.session_state.calculated_values = None

if "adjusted_tuition" not in st.session_state:
    st.session_state.adjusted_tuition = []

# Streamlit app layout
st.title("Tuition Calculation Tool")

# Step 1: Enter a Custom Title for the Report
st.subheader("Step 1: Enter a Custom Title for the Report")
report_title = st.text_input("Report Title", "2025-26 Tuition Projection")

# Step 2: Define Grades and Tuition Data
st.subheader("Step 2: Define Grades and Tuition Data")
grades_data = st.session_state.grades_data

num_grades = st.number_input(
    "Number of Grades",
    min_value=1,
    max_value=12,
    value=len(grades_data["grades"]) if grades_data["grades"] else 1,
    step=1
)

# Ensure grade data lists match the number of grades
while len(grades_data["grades"]) < num_grades:
    grades_data["grades"].append(f"Grade {len(grades_data['grades']) + 1}")
    grades_data["num_students"].append(0)
    grades_data["current_tuition"].append(0.0)

while len(grades_data["grades"]) > num_grades:
    grades_data["grades"].pop()
    grades_data["num_students"].pop()
    grades_data["current_tuition"].pop()

# Collect user input for each grade
for i in range(num_grades):
    grades_data["grades"][i] = st.text_input(f"Grade {i+1} Name", grades_data["grades"][i])
    grades_data["num_students"][i] = st.number_input(
        f"Number of Students in {grades_data['grades'][i]}",
        min_value=0,
        step=1,
        value=grades_data["num_students"][i]
    )
    tuition_input = st.text_input(
        f"Current Tuition for {grades_data['grades'][i]} (per student)", 
        value=format_currency(grades_data["current_tuition"][i])
    )
    formatted_tuition = format_input_as_currency(tuition_input)
    try:
        grades_data["current_tuition"][i] = float(formatted_tuition.replace("$", "").replace(",", ""))
    except ValueError:
        grades_data["current_tuition"][i] = 0.0

# Step 3: Strategic Items
st.subheader("Step 3: Define Strategic Items and Costs")
strategic_items = st.session_state.strategic_items

num_items = st.number_input(
    "Number of Strategic Items",
    min_value=0,
    step=1,
    value=len(strategic_items["names"])
)

# Ensure strategic items lists match the number of items
while len(strategic_items["names"]) < num_items:
    strategic_items["names"].append("")
    strategic_items["costs"].append(0.0)
    strategic_items["descriptions"].append("")

while len(strategic_items["names"]) > num_items:
    strategic_items["names"].pop()
    strategic_items["costs"].pop()
    strategic_items["descriptions"].pop()

# Collect user input for strategic items
strategic_items_list = []
for i in range(num_items):
    strategic_items["names"][i] = st.text_input(f"Strategic Item {i+1} Name", strategic_items["names"][i])
    cost_input = st.text_input(
        f"Cost of {strategic_items['names'][i]}",
        value=format_currency(strategic_items["costs"][i])
    )
    formatted_cost = format_input_as_currency(cost_input)
    try:
        strategic_items["costs"][i] = float(formatted_cost.replace("$", "").replace(",", ""))
    except ValueError:
        strategic_items["costs"][i] = 0.0
    strategic_items["descriptions"][i] = st.text_area(
        f"Description for {strategic_items['names'][i]}", strategic_items["descriptions"][i]
    )
    strategic_items_list.append({
        "Strategic Item": strategic_items["names"][i],
        "Cost": format_currency(strategic_items["costs"][i]),
        "Description": strategic_items["descriptions"][i]
    })

# Step 4: Operations Tuition Increase and Calculations
st.subheader("Step 4: Operations Tuition Increase and Calculations")
roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01, value=3.5)
rpi_percentage = st.number_input("Rate of Productivity Increase (RPI) %", min_value=0.0, step=0.01, value=2.0)
financial_aid_input = st.text_input("Total Financial Aid ($)", value="$100,000.00")
formatted_financial_aid = format_input_as_currency(financial_aid_input)

try:
    financial_aid = float(formatted_financial_aid.replace("$", "").replace(",", ""))
except ValueError:
    financial_aid = 0.0

# Perform calculations
total_tuition = sum(
    [students * tuition for students, tuition in zip(grades_data["num_students"], grades_data["current_tuition"])]
)
avg_tuition = total_tuition / sum(grades_data["num_students"]) if sum(grades_data["num_students"]) > 0 else 0.0
total_strategic_items_cost = sum(strategic_items["costs"])
si_percentage = (total_strategic_items_cost / (sum(grades_data["num_students"]) * avg_tuition)) * 100 if avg_tuition > 0 else 0.0
oti = roi_percentage + rpi_percentage
final_tuition_increase = oti + si_percentage
total_new_tuition = total_tuition * (1 + final_tuition_increase / 100)
tuition_assistance_ratio = (financial_aid / total_new_tuition) * 100 if total_new_tuition > 0 else 0.0

# Adjusted Tuition
adjusted_tuition_values = [tuition * (1 + final_tuition_increase / 100) for tuition in grades_data["current_tuition"]]
adjusted_total_tuition = sum([students * adj for students, adj in zip(grades_data["num_students"], adjusted_tuition_values)])
tuition_increase_percentage = ((adjusted_total_tuition - total_tuition) / total_tuition) * 100 if total_tuition > 0 else 0.0
updated_tuition_assistance_ratio = (financial_aid / adjusted_total_tuition) * 100 if adjusted_total_tuition > 0 else 0.0

# Step 5: Display Results
st.subheader("Results")
st.write(f"**Average Tuition:** {format_currency(avg_tuition)}")
st.write(f"**Strategic Items Percentage:** {format_percentage(si_percentage)}")
st.write(f"**Operations Tuition Increase (OTI):** {format_percentage(oti)}")
st.write(f"**Final Tuition Increase:** {format_percentage(final_tuition_increase)}")
st.write(f"**Total Current Tuition:** {format_currency(total_tuition)}")
st.write(f"**Total New Tuition:** {format_currency(total_new_tuition)}")
st.write(f"**Tuition Assistance Ratio:** {format_percentage(tuition_assistance_ratio)}")
st.write(f"**Adjusted Total Tuition:** {format_currency(adjusted_total_tuition)}")
st.write(f"**Tuition Increase Percentage:** {format_percentage(tuition_increase_percentage)}")
st.write(f"**Updated Tuition Assistance Ratio:** {format_percentage(updated_tuition_assistance_ratio)}")

# Grade-Level Data
grade_level_data = pd.DataFrame({
    "Grade": grades_data["grades"],
    "Number of Students": grades_data["num_students"],
    "Current Tuition per Student": [format_currency(tuition) for tuition in grades_data["current_tuition"]],
    "Adjusted Tuition per Student": [format_currency(adj) for adj in adjusted_tuition_values],
    "Difference": [format_currency(adj - curr) for adj, curr in zip(adjusted_tuition_values, grades_data["current_tuition"])],
    "Total Tuition for Grade": [format_currency(students * adj) for students, adj in zip(grades_data["num_students"], adjusted_tuition_values)],
})

st.subheader("Grade-Level Breakdown")
st.table(grade_level_data)
