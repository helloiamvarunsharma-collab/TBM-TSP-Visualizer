import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np   # ✅ Added import
import re

# -------------------- Streamlit Page Setup --------------------
st.set_page_config(page_title="TSP–TBM Correlation Visualizer", layout="wide")
st.title("🧭 TSP–TBM Correlation Visualizer")
st.markdown("Upload your combined correlation sheet to explore TBM–TSP relationships clearly and simply.")

# -------------------- File Upload --------------------
uploaded_file = st.file_uploader("📂 Upload your Excel file (.xlsx)", key="file_uploader_main")

if uploaded_file:
    try:
        # Read and clean
        data = pd.read_excel(uploaded_file)
        data.columns = data.columns.str.strip().str.lower()

        chain_col = next((c for c in data.columns if "chain" in c), None)
        if chain_col is None:
            st.error("❌ 'Chainage' column not found. Please include it in your file.")
            st.stop()

        # Clean chainage values
        def clean_chainage(v):
            if pd.isna(v): return None
            if isinstance(v, (int, float)): return v
            v = re.sub(r"[^0-9.]", "", str(v))
            try: return float(v)
            except: return None

        data[chain_col] = data[chain_col].apply(clean_chainage)
        data = data.dropna(subset=[chain_col])
        data = data.sort_values(by=chain_col)

        # Sidebar filters
        st.sidebar.header("Filter Options")
        min_c, max_c = float(data[chain_col].min()), float(data[chain_col].max())
        selected_range = st.sidebar.slider(
            "Select Chainage Range (m)",
            min_c, max_c, (min_c, max_c),
            key="range_slider"
        )

        filtered = data[
            (data[chain_col] >= selected_range[0]) &
            (data[chain_col] <= selected_range[1])
        ]

        # Axis selection
        numeric_cols = filtered.select_dtypes(include=['float64', 'int64']).columns.tolist()
        if len(numeric_cols) < 2:
            st.error("❌ Not enough numeric columns for visualization.")
            st.stop()

        st.sidebar.header("Visualization Controls")
        x_axis = st.sidebar.selectbox("X-axis", numeric_cols, index=0, key="x_axis")
        y_axis = st.sidebar.selectbox("Y-axis", numeric_cols, index=1, key="y_axis")
        z_axis = st.sidebar.selectbox("Z-axis (optional 3D)", [None] + numeric_cols, key="z_axis")

        # -------------------- 2D Scatter Plot --------------------
        st.subheader("📈 2D Correlation Plot")

        fig2d = go.Figure()
        fig2d.add_trace(go.Scatter(
            x=filtered[x_axis],
            y=filtered[y_axis],
            mode='markers',
            marker=dict(color='lightblue', size=6, line=dict(width=0.5, color='white')),
            name='Data Points'
        ))

        # Add linear trendline + label
        if len(filtered) > 2:
            z = np.polyfit(filtered[x_axis], filtered[y_axis], 1)
            p = np.poly1d(z)
            slope, intercept = round(z[0], 3), round(z[1], 3)
            corr_val = filtered[x_axis].corr(filtered[y_axis])

            fig2d.add_trace(go.Scatter(
                x=filtered[x_axis],
                y=p(filtered[x_axis]),
                mode='lines',
                line=dict(color='gray', width=2),
                name=f"Trendline (r={corr_val:.2f})"
            ))

            # Add equation text
            eq_text = f"y = {slope}x + {intercept} | r = {corr_val:.2f}"
            fig2d.add_annotation(
                xref="paper", yref="paper",
                x=0.05, y=0.95,
                text=eq_text,
                showarrow=False,
                font=dict(color="white", size=12)
            )

        fig2d.update_layout(
            template="plotly_dark",
            xaxis_title=x_axis,
            yaxis_title=y_axis,
            margin=dict(l=40, r=40, t=40, b=40),
            height=500
        )
        st.plotly_chart(fig2d, use_container_width=True)

        # -------------------- 3D Scatter Plot --------------------
        if z_axis:
            st.subheader("🌐 3D Correlation Plot")

            fig3d = go.Figure(data=[go.Scatter3d(
                x=filtered[x_axis],
                y=filtered[y_axis],
                z=filtered[z_axis],
                mode='markers',
                marker=dict(
                    size=4,
                    color='lightblue',
                    opacity=0.8
                )
            )])
            fig3d.update_layout(
                scene=dict(
                    xaxis_title=x_axis,
                    yaxis_title=y_axis,
                    zaxis_title=z_axis,
                    xaxis=dict(showgrid=True, gridcolor='gray'),
                    yaxis=dict(showgrid=True, gridcolor='gray'),
                    zaxis=dict(showgrid=True, gridcolor='gray')
                ),
                margin=dict(l=0, r=0, b=0, t=30),
                template="plotly_dark",
                height=600
            )
            st.plotly_chart(fig3d, use_container_width=True)

        # -------------------- Data Table --------------------
        with st.expander("📋 View Filtered Data"):
            st.dataframe(filtered)

        # -------------------- Summary Statistics --------------------
        st.subheader("📊 Correlation Summary")
        corr_val = filtered[x_axis].corr(filtered[y_axis])
        st.metric(label=f"Correlation between {x_axis} and {y_axis}", value=round(corr_val, 3))
        st.write(filtered.describe().T)

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
else:
    st.info("👆 Upload your Excel file to start the visualization.")
