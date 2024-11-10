# Step 4: Add Strategic Items and Descriptions
st.subheader("Step 4: Add Strategic Items and Descriptions")
strategic_items = st.session_state.strategic_items
num_items = st.number_input("Number of Strategic Items", min_value=0, max_value=10, value=len(strategic_items["names"]), step=1)

# Adjust strategic items lists to match the number of items
while len(strategic_items["names"]) < num_items:
    strategic_items["names"].append(f"Item {len(strategic_items['names']) + 1}")
    strategic_items["costs"].append(0.0)
    strategic_items["descriptions"].append("")

while len(strategic_items["names"]) > num_items:
    strategic_items["names"].pop()
    strategic_items["costs"].pop()
    strategic_items["descriptions"].pop()

strategic_items_list = []
for i in range(num_items):
    strategic_items["names"][i] = st.text_input(f"Strategic Item {i+1} Name", strategic_items["names"][i])
    cost_input = st.text_input(f"Cost of {strategic_items['names'][i]} ($)", value=format_currency(strategic_items["costs"][i]))
    formatted_cost = format_input_as_currency(cost_input)
    try:
        strategic_items["costs"][i] = float(formatted_cost.replace(",", "").replace("$", ""))
    except ValueError:
        strategic_items["costs"][i] = 0.0
    strategic_items["descriptions"][i] = st.text_area(
        f"Description for {strategic_items['names'][i]}", value=strategic_items["descriptions"][i]
    )
    strategic_items_list.append({
        "Strategic Item": strategic_items["names"][i],
        "Cost": strategic_items["costs"][i],
        "Description": strategic_items["descriptions"][i]
    })

strategic_items_df = pd.DataFrame(strategic_items_list)

# Step 5: Previous Year's Total Expenses
st.subheader("Step 5: Enter Previous Year's Total Expenses")
previous_expenses_input = st.text_input("Previous Year's Total Expenses ($)", "")
formatted_previous_expenses = format_input_as_currency(previous_expenses_input)
try:
    previous_expenses = float(formatted_previous_expenses.replace(",", "").replace("$", ""))
except ValueError:
    previous_expenses = 0.0

# Step 6: Operations Tuition Increase (OTI) and Final Increase Calculation
st.subheader("Step 6: Operations Tuition Increase (OTI) and Final Increase Calculation")
roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01, value=3.32)
rpi_percentage = st.number_input("Rate of Productivity Increase (RPI) %", min_value=0.0, step=0.01, value=2.08)
oti = roi_percentage + rpi_percentage
total_strategic_items_cost = sum(strategic_items["costs"])
si_percentage = (
    (total_strategic_items_cost / (sum(grades_data["num_students"]) * avg_tuition)) * 100 if avg_tuition > 0 else 0.0
)
final_tuition_increase = oti + si_percentage

# Step 7: Financial Aid (Tuition Assistance) Calculation
st.subheader("Step 7: Financial Aid (Tuition Assistance)")
financial_aid_input = st.text_input("Total Financial Aid ($)", "")
formatted_financial_aid = format_input_as_currency(financial_aid_input)
try:
    financial_aid = float(formatted_financial_aid.replace(",", "").replace("$", ""))
except ValueError:
    financial_aid = 0.0

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
    if len(st.session_state.adjusted_tuition) != len(grades_data["current_tuition"]):
        st.session_state.adjusted_tuition = [
            tuition * (1 + final_tuition_increase / 100) for tuition in grades_data["current_tuition"]
        ]

# Display results if calculations have been performed
if st.session_state.calculated_values is not None:
    st.subheader("Results")
    st.write(f"**Report Title:** {report_title}")
    
    # Display original calculated results
    st.write("**Original Calculated Results:**")
    st.write(f"**Total Current Tuition:** {format_currency(st.session_state.calculated_values['total_current_tuition'])}")
    st.write(f"**Total New Tuition:** {format_currency(st.session_state.calculated_values['total_new_tuition'])}")
    st.write(f"**Final Tuition Increase Percentage:** {st.session_state.calculated_values['final_tuition_increase']:.2f}%")
    st.write(f"**Tuition Assistance Ratio:** {st.session_state.calculated_values['tuition_assistance_ratio']:.2f}%")
    
    # Original vs Adjusted Tuition Comparison Table
    st.subheader("Original vs Adjusted Tuition by Grade Level (Initial Results)")
    original_tuition_data = {
        "Grade": grades_data["grades"],
        "Number of Students": grades_data["num_students"],
        "Original Tuition per Student": grades_data["current_tuition"],
        "Adjusted Tuition per Student (Initial)": [
            tuition * (1 + st.session_state.calculated_values['final_tuition_increase'] / 100) 
            for tuition in grades_data["current_tuition"]
        ]
    }
    original_comparison_df = pd.DataFrame(original_tuition_data)
    original_comparison_df["Difference"] = original_comparison_df["Adjusted Tuition per Student (Initial)"] - original_comparison_df["Original Tuition per Student"]
    st.dataframe(original_comparison_df)

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

    # Calculate updated totals and metrics
    total_current_tuition = sum(df["Number of Students"] * df["Current Tuition per Student"])
    adjusted_total_tuition = sum(df["Total Tuition for Grade"])
    tuition_increase_percentage = ((adjusted_total_tuition - total_current_tuition) / total_current_tuition) * 100 if total_current_tuition > 0 else 0.0
    updated_tuition_assistance_ratio = (financial_aid / adjusted_total_tuition) * 100 if adjusted_total_tuition > 0 else 0.0

    # Display updated totals
    st.write("**Adjusted Results:**")
    st.write(f"**Total Current Tuition:** {format_currency(total_current_tuition)}")
    st.write(f"**Adjusted Total Tuition:** {format_currency(adjusted_total_tuition)}")
    st.write(f"**Final Tuition Increase Percentage:** {tuition_increase_percentage:.2f}%")
    st.write(f"**Final Tuition Assistance Ratio:** {updated_tuition_assistance_ratio:.2f}%")
    
    # Comparison Table for Grade-Level Adjustments
    st.subheader("Comparison of Tuition Before and After Adjustments")
    adjustment_comparison_data = {
 
