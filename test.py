import streamlit as st
import pandas as pd
import plotly.express as px

# App title
st.title("✅ Streamlit Test App")
st.write("If you can see this page in your browser, everything is working fine!")

# Create a simple DataFrame
data = pd.DataFrame({
    "Chainage (m)": [100, 120, 140, 160, 180],
    "P-wave Velocity (m/s)": [5200, 4800, 5000, 5300, 4900],
    "Dynamic Modulus (GPa)": [45, 38, 40, 48, 42]
})

# Show the data table
st.subheader("Sample Data")
st.dataframe(data)

# Create an interactive line chart using Plotly
fig = px.line(
    data,
    x="Chainage (m)",
    y=["P-wave Velocity (m/s)", "Dynamic Modulus (GPa)"],
    markers=True,
    title="P-wave Velocity and Dynamic Modulus vs Chainage"
)

# Display the chart
st.plotly_chart(fig, use_container_width=True)
