import streamlit as st
import pandas as pd
import plotly.graph_objects as go  # For interactive graphs
import locale
from io import BytesIO  # For generating the PDF in memory
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas  # For creating the PDF
from reportlab.lib import colors  # For adding colors to the PDF
from reportlab.lib.utils import ImageReader  # For adding images to PDF
import tempfile

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

# Function to generate a downloadable PDF report
def generate_pdf(report_title, df, total_current_tuition, total_new_tuition, avg_increase_percentage, tuition_assistance_ratio, strategic_items_df, graph_image, summary_text, csm_quote):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title of the report
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, height - 50, f"Report Title: {report_title}")

    # Summary details
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, height - 80, f"Total Current Tuition: {format_currency(total_current_tuition)}")
    pdf.drawString(100, height - 100, f"Total New Tuition: {format_currency(total_new_tuition)}")
    pdf.drawString(100, height - 120, f"Average Tuition Increase Percentage: {avg_increase_percentage:.2f}%")
    pdf.drawString(100, height - 140, f"Tuition Assistance Ratio: {tuition_assistance_ratio:.2f}%")

    # Add a header for the table
    pdf.drawString(100, height - 160, "Tuition by Grade Level:")

    # Draw table for tuition by grade level
    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(colors.black)

    row_y = height - 180
    for i, row in df.iterrows():
        pdf.drawString(100, row_y, f"{row['Grade']}: {row['Number of Students']} students, Current Tuition: {row['Current Tuition per Student']}, New Tuition: {row['New Tuition per Student']}")
        row_y -= 20

    # Strategic Items Section
    row_y -= 20  # Adding space between sections
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, row_y, "Strategic Items and Costs:")

    pdf.setFont("Helvetica", 10)
    row_y -= 20
    for i, row in strategic_items_df.iterrows():
        pdf.drawString(100, row_y, f"{row['Strategic Item']}: {row['Cost ($)']}")
        row_y -= 20

    # Add the calculation summary text
    row_y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, row_y, "Summary of Calculations:")
    pdf.setFont("Helvetica", 10)
    row_y -= 20
    for line in summary_text.split('\n'):
        pdf.drawString(100, row_y, line)
        row_y -= 20

    # Embed the Christian School Management quote
    row_y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, row_y, "Quote from Christian School Management:")
    pdf.setFont("Helvetica", 10)
    row_y -= 20
    for line in csm_quote.split('\n'):
        pdf.drawString(100, row_y, line)
        row_y -= 20

    # Embed the graph image in the PDF
    pdf.drawImage(ImageReader(graph_image), 100, row_y - 200, width=400, height=200)

    # Finalize PDF
    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer

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

# Christian School Management Quote
csm_quote = """
"The Christian school budget is a Kingdom document, a moral document, and an arithmetic document. Its primary purpose is to empower the school to deliver its mission with excellence (Kingdom). Its secondary purpose is to ensure that the school acts in a Christian way in all its actions and, in particular, in relation to its employees (moral). Its final purpose is to ensure that Trustees carry out their fiscal responsibility in balancing the school’s finances. In other words, it is not just a balance sheet or an audit statement. It is, rather, the expression of the mission and a clear statement of the priorities set by the school to fulfill that mission. “For where your treasure is, there your heart will be also” (Matthew 6:21).

Tuition is the primary source of income the school has. It must be set with the strategic interests of the next generation of children in mind. It must meet today’s needs with an understanding of the future. It must be both a today and a next-five/ten-years decision.

Tuition setting is a formula, not a conversation. That doesn’t make it easy. It does make it simple. Like it or not, the Christian school’s tuition must go up by the Operations Tuition Increase. This number is based on the external economic realities of inflation and the rate of productivity increase. The annual tuition increase maintains the power of the school’s current operations budget. It allows you to continue to do what you are doing at the same level of excellence."
"""

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
        summary_text = """
        ### Summary of Calculation:
        The total current tuition was calculated based on the sum of tuition rates per student for each grade level. 
        The new tuition was calculated by applying an inflation rate (Rate of Inflation + 2.08% Efficiency Rate) to the total current tuition. 
        Additionally, strategic costs were distributed across all students. The average tuition increase percentage was then applied to each grade.
        The tuition assistance ratio represents the percentage of the new tuition allocated to financial aid.
        """
        st.write(summary_text)

        # Include the Christian School Management quote
        st.subheader("Quote from Christian School Management")
        st.write(csm_quote)

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

        # Save the graph to an image file for PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            fig.write_image(temp_file.name)
            graph_image = temp_file.name

        # Show the total results in a formatted table
        total_table = pd.DataFrame({
            "Total Current Tuition": [format_currency(total_current_tuition)],
            "Total New Tuition": [format_currency(total_new_tuition)],
            "Average Increase %": [f"{avg_increase_percentage:.2f}%"],
            "Tuition Assistance Ratio": [f"{tuition_assistance_ratio:.2f}%"]
        })

        st.subheader("Overall Summary")
        st.table(total_table)

        # Generate the downloadable PDF report
        pdf_buffer = generate_pdf(report_title, df, total_current_tuition, total_new_tuition, avg_increase_percentage, tuition_assistance_ratio, strategic_items_df, graph_image, summary_text, csm_quote)
        
        # Create a download button for the PDF report
        st.download_button(
            label="Download Report as PDF",
            data=pdf_buffer,
            file_name="tuition_report.pdf",
            mime="application/pdf"
        )
