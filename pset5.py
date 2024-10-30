import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Title of the app
st.title("Customizable Data Input and Visualization App")

# Step 1: User selects number of rows and columns
num_rows = st.number_input("Number of rows", min_value=1, max_value=20, value=6)  # Default changed to 6
num_cols = st.number_input("Number of columns", min_value=1, max_value=5, value=4)  # Default changed to 4

# Step 2: User defines column names
st.write("### Define Column Names:")
column_names = []
for i in range(num_cols):
    col_name = st.text_input(f"Name for column {i+1}", f"Column_{i+1}")
    column_names.append(col_name)

# Initialize or update session state for row data if not already done
for row in range(num_rows):
    if f"row_data_{row}" not in st.session_state:
        # Initialize each row with default values (all 0s initially)
        st.session_state[f"row_data_{row}"] = [0] * num_cols
    # Adjust the number of columns in existing rows if num_cols has changed
    elif len(st.session_state[f"row_data_{row}"]) != num_cols:
        st.session_state[f"row_data_{row}"] = st.session_state[f"row_data_{row}"][:num_cols] + [0] * (num_cols - len(st.session_state[f"row_data_{row}"]))

# Step 3: Input Data Section with Row-Specific Randomization
st.write("### Input Data (Click 'Randomize Row' to fill the row with random values):")
data = []

# Loop through each row to display inputs or randomize as needed
for row in range(num_rows):
    row_data = []
    cols = st.columns(num_cols + 1)  # Extra column for the "Randomize" button

    # Check if the Randomize Row button was clicked for this row
    if cols[-1].button("Randomize Row", key=f"randomize_button_{row}"):
        # Generate random values for this row and store them in session state
        st.session_state[f"row_data_{row}"] = np.random.randint(1, 51, num_cols).tolist()

    # Display each cell, showing either manual inputs or randomized values
    for col in range(num_cols):
        value = cols[col].number_input(
            f"Row {row+1}, {column_names[col]}", 
            value=int(st.session_state[f"row_data_{row}"][col]), 
            key=f"{row}_{col}"
        )
        row_data.append(value)

    # Update session state with the new manual values (to keep if user changes them)
    st.session_state[f"row_data_{row}"] = row_data
    data.append(row_data)

# Create DataFrame with user inputs
df = pd.DataFrame(data, columns=column_names)

# Display the user-generated DataFrame
st.write("### Your Input Data:")
st.write(df)

# Define colors for the pie chart
colors = ['red'] + px.colors.qualitative.Set1[:num_rows-1]  # First row red, others from a color set

# Step 4: Choose chart type and plot data
chart_type = st.selectbox("Select Chart Type", ["Grouped Bar Chart", "Scatter Plot", "Pie Chart", "Correlation Matrix Heatmap"])

st.write("### Visualization:")

# Grouped Bar Chart - each column as a separate bar group
if chart_type == "Grouped Bar Chart":
    df_long = df.reset_index().melt(id_vars="index", var_name="Category", value_name="Value")
    fig = px.bar(df_long, x="index", y="Value", color="Category", barmode="group", labels={"index": "Rows"})

# Scatter Plot - choose two columns to plot against each other
elif chart_type == "Scatter Plot":
    x_column = st.selectbox("Select X-axis column", column_names, key="scatter_x")
    y_column = st.selectbox("Select Y-axis column", column_names, key="scatter_y")
    if x_column != y_column:
        fig = px.scatter(df, x=x_column, y=y_column)
    else:
        st.error("Please select two different columns for the scatter plot.")

# Pie Chart - visualize one column's values as proportions with fixed colors
elif chart_type == "Pie Chart":
    pie_column = st.selectbox("Select column for Pie Chart", column_names, key="pie_column")
    fig = px.pie(df, names=df.index, values=pie_column, color_discrete_sequence=colors, title=f"Pie Chart of {pie_column}")

# Correlation Matrix Heatmap
elif chart_type == "Correlation Matrix Heatmap":
    # Calculate the correlation matrix
    correlation_matrix = df.corr()
    fig = px.imshow(correlation_matrix, 
                    labels=dict(color="Correlation Coefficient"), 
                    x=correlation_matrix.columns, 
                    y=correlation_matrix.columns,
                    title="Correlation Matrix Heatmap",
                    color_continuous_scale='RdBu',
                    zmin=-1, zmax=1,
                    text_auto=True)  # Show correlation coefficients in each square

# Display the chart
st.plotly_chart(fig)
