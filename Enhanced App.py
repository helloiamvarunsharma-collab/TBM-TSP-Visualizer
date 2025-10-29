import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF

# Streamlit Page Setup
st.set_page_config(page_title="Enhanced TBM–TSP Visualizer", layout="wide")
st.title("🪨 Enhanced TBM–TSP Correlation Visualizer")
st.caption("Visualize TBM and TSP parameters, detect weak zones, and generate correlation summaries.")

# File upload
uploaded_file = st.file_uploader("📂 Upload your combined Excel sheet (.xlsx)", type=["xlsx"], key="file_upload")
if uploaded_file:
    # Read Excel
    data = pd.read_excel(uploaded_file)
    data.columns = data.columns.str.strip().str.lower()

    # Detect chainage column
    chain_col = next((c for c in data.columns if "chain" in c), None)
    if chain_col:
        data[chain_col] = pd.to_numeric(data[chain_col], errors='coerce')

    # Clean numeric data
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()

    # Sidebar controls
    st.sidebar.header("🔧 Controls")
    x_axis = st.sidebar.selectbox("X-axis", numeric_cols, index=0)
    y_axis = st.sidebar.selectbox("Y-axis", numeric_cols, index=1)
    z_axis = st.sidebar.selectbox("Z-axis (3D)", [None] + numeric_cols)
    color_by = st.sidebar.selectbox("Color By", [None] + data.columns.tolist())

    if chain_col:
        min_c, max_c = float(data[chain_col].min()), float(data[chain_col].max())
        selected_range = st.sidebar.slider("Select Chainage Range (m)", min_c, max_c, (min_c, max_c), key="chain_slider")
        data = data[(data[chain_col] >= selected_range[0]) & (data[chain_col] <= selected_range[1])]

    st.divider()

    # ======= Section 1: Key Insights =======
    st.subheader("📊 Key Insights")
    col1, col2, col3 = st.columns(3)

    corr_val = data[x_axis].corr(data[y_axis]) if x_axis in data and y_axis in data else 0
    mean_penetration = data[y_axis].mean() if y_axis in data else 0
    min_velocity = data[numeric_cols].min().min() if len(numeric_cols) > 0 else 0

    col1.metric("Correlation", f"{corr_val:.3f}")
    col2.metric("Avg. Value", f"{mean_penetration:.2f}")
    col3.metric("Min. Velocity", f"{min_velocity:.2f}")

    st.divider()

    # ======= Section 2: 2D and 3D Visualization =======
    st.subheader("📈 Correlation Visualizations")

    # --- 2D Scatter Plot ---
    fig2d = px.scatter(
        data,
        x=x_axis,
        y=y_axis,
        color=color_by if color_by else None,
        trendline="ols",
        template="plotly_white",
        title=f"{x_axis} vs {y_axis} Correlation"
    )
    fig2d.update_traces(marker=dict(size=8, line=dict(width=1, color="DarkSlateGrey")))
    fig2d.update_layout(height=500, title_x=0.4)
    st.plotly_chart(fig2d, use_container_width=True)

    # --- 3D Scatter Plot ---
    if z_axis:
        st.subheader("🌐 3D Correlation Plot")
        fig3d = px.scatter_3d(
            data,
            x=x_axis,
            y=y_axis,
            z=z_axis,
            color=color_by if color_by else None,
            template="plotly_white",
            title=f"{x_axis}, {y_axis}, and {z_axis} (3D View)"
        )
        fig3d.update_traces(marker=dict(size=4))
        st.plotly_chart(fig3d, use_container_width=True)

    st.divider()

    # ======= Section 3: Weak Zone Detection =======
    if "velocity" in " ".join(data.columns):
        st.subheader("⚠️ Weak Zone Detection (Low Velocity Areas)")
        velocity_cols = [c for c in data.columns if "velocity" in c]
        for col in velocity_cols:
            fig_v = px.line(data, x=chain_col, y=col, title=f"{col} vs Chainage", template="plotly_white")
            fig_v.update_traces(line=dict(color="red", width=3))
            st.plotly_chart(fig_v, use_container_width=True)

    # ======= Section 4: TBM Parameter Profiles =======
    tbm_cols = [c for c in data.columns if any(k in c for k in ["penetration", "torque", "thrust", "revolution"])]
    if tbm_cols:
        st.subheader("🧱 TBM Operational Parameters")
        for col in tbm_cols:
            fig_tbm = px.line(data, x=chain_col, y=col, title=f"{col} vs Chainage", template="plotly_white")
            fig_tbm.update_traces(line=dict(width=3))
            st.plotly_chart(fig_tbm, use_container_width=True)

    st.divider()

    # ======= Section 5: Data Table =======
    with st.expander("🗂 View Filtered Data"):
        st.dataframe(data, use_container_width=True)

    # ======= Section 6: PDF Export =======
     # ======= Section 6: PDF Export =======
    if st.button("📄 Export Summary PDF"):

        def safe_text(text):
            """Convert text safely to ASCII for FPDF."""
            # Replace common unicode dashes, degree, etc.
            replacements = {
                "–": "-",
                "—": "-",
                "°": " deg",
                "±": "+/-",
                "×": "x",
                "•": "*",
                "’": "'",
                "‘": "'",
                "“": '"',
                "”": '"',
                "→": "->",
            }
            text = str(text)
            for k, v in replacements.items():
                text = text.replace(k, v)
            return text.encode("latin-1", "replace").decode("latin-1")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, safe_text("TBM–TSP Correlation Summary Report"), ln=True, align="C")

        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 10, safe_text(f"Chainage Range: {selected_range[0]} - {selected_range[1]} m"), ln=True)
        pdf.cell(0, 10, safe_text(f"X-axis: {x_axis}, Y-axis: {y_axis}, Z-axis: {z_axis if z_axis else 'None'}"), ln=True)
        pdf.cell(0, 10, safe_text(f"Correlation ({x_axis} vs {y_axis}): {round(corr_val, 3)}"), ln=True)

        # Add correlation summary
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, safe_text("Top Parameter Correlations:"), ln=True)
        pdf.set_font("Arial", "", 10)
        corr_matrix = data.corr(numeric_only=True).abs().unstack().sort_values(ascending=False)
        corr_matrix = corr_matrix[corr_matrix < 1].dropna().head(5)
        for (a, b), val in corr_matrix.items():
            pdf.cell(0, 8, safe_text(f"{a} - {b}: {val:.3f}"), ln=True)

        try:
            pdf.output("TBM_TSP_Summary.pdf")
            st.success("✅ PDF exported successfully! File: TBM_TSP_Summary.pdf")
        except Exception as e:
            st.error(f"⚠️ PDF export failed: {e}")

else:
    st.info("📤 Please upload your Excel file to start visualizing correlations.")
