import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import locale
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap

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

# Function to generate a downloadable PDF report
def generate_pdf(report_title, df, total_current_tuition, total_new_tuition, avg_increase_percentage, tuition_assistance_ratio, strategic_items_df, summary_text):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title of the report
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, f"Report Title: {report_title}")

    # Summary details
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 80, f"Total Current Tuition: {format_currency(total_current_tuition)}")
    pdf.drawString(50, height - 100, f"Total New Tuition: {format_currency(total_new_tuition)}")
    pdf.drawString(50, height - 120, f"Average Tuition Increase Percentage: {avg_increase_percentage:.2f}%")
    pdf.drawString(50, height - 140, f"Tuition Assistance Ratio: {tuition_assistance_ratio:.2f}%")

    # Add the table for tuition by grade level
    pdf.drawString(50, height - 170, "Tuition by Grade Level:")
    row_y = height - 190
    pdf.setFont("Helvetica", 10)
    for i, row in df.iterrows():
        pdf.drawString(50, row_y, f"{row['Grade']}: {row['Number of Students']} students, "
                                  f"Current Tuition: {row['Current Tuition per Student']}, "
                                  f"New Tuition: {row['New Tuition per Student']}")
        row_y -= 15

    # Strategic Items Section
    if not strategic_items_df.empty:
        row_y -= 20
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, row_y, "Strategic Items and Costs:")
        row_y -= 20
        pdf.setFont("Helvetica", 10)
        for i, row in strategic_items_df.iterrows():
            pdf.drawString(50, row_y, f"{row['Strategic Item']}: {row['Cost ($)']}")
            row_y -= 15

    # Add the calculation summary text
    row_y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, row_y, "Summary of Calculations:")
    row_y -= 20
    pdf.setFont("Helvetica", 10)
    for line in textwrap.wrap(summary_text, width=90):
        pdf.drawString(50, row_y, line)
        row_y -= 15

    # Finalize PDF
    pdf.save()
    buffer.seek(0)
    return buffer

# Streamlit App Start
st.title("Tuition Calculation Tool")

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

# Step 4: Add Strategic Items
st.subheader("Step 4: Add Strategic Items")
strategic_items_costs = []
strategic_item_names = []
num_items = st.number_input("Number of Strategic Items", min_value=0, max_value=10, value=0, step=1)

for i in range(int(num_items)):
    item_name = st.text_input(f"Strategic Item {i+1} Name", f"Item {i+1}")
    item_cost_input = st.text_input(f"Cost of {item_name} ($)", "")
    formatted_item_cost = format_input_as_currency(item_cost_input)
    st.text(f"Formatted Cost: {formatted_item_cost}")
    item_cost = float(formatted_item_cost.replace(",", "").replace("$", "")) if formatted_item_cost else 0.0
    strategic_item_names.append(item_name)
    strategic_items_costs.append(item_cost)

# Step 5: Previous Year’s Expenses
st.subheader("Step 5: Previous Year's Total Expenses")
previous_expenses_input = st.text_input("Previous Year's Total Expenses ($)", "")
formatted_previous_expenses = format_input_as_currency(previous_expenses_input)
st.text(f"Formatted Previous Expenses: {formatted_previous_expenses}")
previous_expenses = float(formatted_previous_expenses.replace(",", "").replace("$", "")) if formatted_previous_expenses else 0.0

# Step 6: Operations Tuition Increase (OTI) Calculation
st.subheader("Step 6: Operations Tuition Increase (OTI) Calculation")
roi_percentage = st.number_input("Rate of Inflation (ROI) %", min_value=0.0, step=0.01, value=3.32)
rpi_percentage = st.number_input("Rate of Productivity Increase (RPI) %", min_value=0.0, step=0.01, value=2.08)
oti = roi_percentage + rpi_percentage
st.text(f"Operations Tuition Increase (OTI): {oti:.2f}%")

# Step 7: Automatically Calculate Strategic Items (SI) Percentage
st.subheader("Step 7: Automatically Calculate Strategic Items (SI) Percentage")
total_strategic_items_cost = sum(strategic_items_costs)
num_total_students = sum(num_students)

if avg_tuition > 0 and num_total_students > 0:
    cost_per_student = total_strategic_items_cost / num_total_students
    si_percentage = (cost_per_student / avg_tuition) * 100
else:
    si_percentage = 0.0

st.text(f"Strategic Items (SI) Percentage: {si_percentage:.2f}%")

# Step 8: Calculate Final Tuition Increase
st.subheader("Step 8: Calculate Final Tuition Increase")
final_tuition_increase = oti + si_percentage
st.text(f"Final Tuition Increase: {final_tuition_increase:.2f}%")

# Step 9: Financial Aid (Tuition Assistance) Calculation
st.subheader("Step 9: Financial Aid (Tuition Assistance)")
financial_aid_input = st.text_input("Total Financial Aid ($)", "")
formatted_financial_aid = format_input_as_currency(financial_aid_input)
st.text(f"Formatted Financial Aid: {formatted_financial_aid}")
financial_aid = float(formatted_financial_aid.replace(",", "").replace("$", "")) if formatted_financial_aid else 0.0

# Step 10: Calculate New Tuition and Display Results
if st.button("Calculate New Tuition"):
    try:
        if sum(num_students) == 0 or len(current_tuition) == 0:
            st.error("Please provide valid inputs for all grade levels.")
        else:
            # Calculate total current tuition
            total_current_tuition = sum([students * tuition for students, tuition in zip(num_students, current_tuition)])
            
            # Calculate the new total tuition by applying the final increase
            total_new_tuition = total_current_tuition * (1 + final_tuition_increase / 100)
            
            # Calculate the average increase per student
            new_tuition_per_student = [(tuition * (1 + final_tuition_increase / 100)) for tuition in current_tuition]
            tuition_assistance_ratio = (financial_aid / total_new_tuition) * 100 if total_new_tuition > 0 else 0.0

            # Display Results
            st.subheader("Results")
            st.write(f"**Report Title:** {report_title}")
            st.write(f"**Total Current Tuition:** {format_currency(total_current_tuition)}")
            st.write(f"**Total New Tuition:** {format_currency(total_new_tuition)}")
            st.write(f"**Final Tuition Increase Percentage:** {final_tuition_increase:.2f}%")
            st.write(f"**Tuition Assistance Ratio:** {tuition_assistance_ratio:.2f}%")

            # Create DataFrame for tuition by grade level
            tuition_data = {
                "Grade": grades,
                "Number of Students": num_students,
                "Current Tuition per Student": [format_currency(tuition) for tuition in current_tuition],
                "New Tuition per Student": [format_currency(nt) for nt in new_tuition_per_student],
                "Increase per Student": [format_currency(nt - tuition) for nt, tuition in zip(new_tuition_per_student, current_tuition)]
            }
            df = pd.DataFrame(tuition_data)

            st.subheader("Tuition by Grade Level")
            st.write(df)

            # Display all Strategic Items added by the user
            strategic_items_df = pd.DataFrame({
                "Strategic Item": strategic_item_names,  # Display all entered strategic items
                "Cost ($)": [format_currency(cost) for cost in strategic_items_costs]
            })

            st.subheader("Strategic Items")
            st.write(strategic_items_df)

            # Plotly bar chart to compare current and new tuition, including SI%
            st.subheader("Interactive Tuition Increase Chart with SI%")
            fig = go.Figure(data=[
                go.Bar(name='Current Tuition', x=grades, y=[float(tuition.replace('$', '').replace(',', '')) for tuition in df["Current Tuition per Student"]], marker_color='skyblue'),
                go.Bar(name='New Tuition with SI%', x=grades, y=[float(nt.replace('$', '').replace(',', '')) for nt in df["New Tuition per Student"]], marker_color='orange'),
                go.Bar(name='SI % Increase', x=grades, y=[si_percentage] * len(grades), marker_color='lightgreen')
            ])
            fig.update_layout(barmode='group', title_text="Current vs New Tuition with SI% by Grade Level")
            st.plotly_chart(fig)

            # Summary of Calculation Steps (Narrative)
            summary_text = f"""
            ### Summary of Calculations:
            The tuition calculation for the 2025-26 school year was completed by considering several key factors. 
            
            First, we calculated the **Operations Tuition Increase (OTI)**, which reflects the impact of inflation on costs. The Rate of Inflation (ROI) was set at {roi_percentage:.2f}%, and a productivity adjustment of {rpi_percentage:.2f}% was added. Together, these factors resulted in an OTI of {oti:.2f}%.

            Next, we factored in the costs of **Strategic Items**. These are investments the school plans to make to improve facilities, curriculum, or other areas. The total strategic item cost was spread across all students, resulting in a Strategic Items (SI) percentage increase of {si_percentage:.2f}%.

            By combining the OTI and the SI percentage, the total tuition increase was calculated to be {final_tuition_increase:.2f}%.

            Lastly, we considered financial aid. The total amount of financial aid was calculated to account for {tuition_assistance_ratio:.2f}% of the new total tuition.
            """

            st.subheader("Summary of Calculations")
            st.markdown(summary_text)

            # Generate the PDF report
            pdf_buffer = generate_pdf(
                report_title, df, total_current_tuition, total_new_tuition,
                final_tuition_increase, tuition_assistance_ratio, strategic_items_df,
                summary_text
            )

            # Download button for the PDF report
            st.download_button(
                label="Download Report as PDF",
                data=pdf_buffer,
                file_name="tuition_report.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"An error occurred during calculation: {str(e)}")
