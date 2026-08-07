import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    if "factors" not in st.session_state:
        st.session_state.factors = {
            "Strengths": [],
            "Weaknesses": [],
            "Opportunities": [],
            "Threats": [],
        }

def factor_input_ui(category):

    """Renders the UI for adding and managing factors for a category."""
    st.subheader(category)

    # Input for new factor
    new_factor = st.text_input(
        f"Add a new factor for {category}", 
        key=f"new_{category}_{len(st.session_state.factors[category])}"
    )
    if st.button(f"Add Factor", key=f"add_{category}"):
        if new_factor:
            st.session_state.factors[category].append({"name": new_factor, "impact": 5, "probability": 0.5})
            # Clear the input box after adding
            st.rerun()

    # Display existing factors
    for i, factor in enumerate(st.session_state.factors[category]):
        # String 1: name of factor
        st.text(factor["name"])
        
        # String 2: Impact slider
        st.session_state.factors[category][i]["impact"] = st.slider(
            f"Impact", 1, 10, factor["impact"],
            key=f"{category}_{i}_impact_slider"
        )
        
        # String 3: Probability slider
        st.session_state.factors[category][i]["probability"] = st.slider(
            f"Probability", 0.1, 1.0, factor["probability"], step=0.1,
            key=f"{category}_{i}_probability_slider"
        )
        
        # String 4: button Remove
        if st.button("Remove", key=f"remove_{category}_{i}"):
            st.session_state.factors[category].pop(i)
            st.rerun()
        
        # Divider of factors (optional)
        st.markdown("---")

def calculate_multiplying_impact_prob(factors):
    """Calculates impact x probability for each individual factor."""
    all_factors_with_score = []
    
    for category, items in factors.items():
        for item in items:
            score = item["impact"] * item["probability"]
            all_factors_with_score.append({
                "category": category,
                "name": item["name"],
                "impact": item["impact"],
                "probability": item["probability"],
                "impact_prob": score
            })
    
    return all_factors_with_score

@st.cache_data
def convert_to_xlsx(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="SWOT Analysis")
    return output.getvalue()

def main():
    """The main function that runs the Streamlit application."""
    st.set_page_config(page_title="SWOT Analysis Generator", page_icon="🔎", layout="wide")

    initialize_session_state()

    # --- Sidebar ---
    st.sidebar.image("assets/swot_logo.png", caption="")
    st.sidebar.subheader("The purpose of the SWOT Analysis Generator")
    st.sidebar.markdown(
        """
        The purpose of the SWOT Analysis Generator is to support the identification of potential strategic actions aimed at strengthening the competitive position of the object of analysis and achieving the strategic goals set for the object of analysis.
        """
    )

    # --- Main Content ---
    st.title("SWOT Analysis Generator")
    # Form fields for Company and Environment
    st.subheader("Subject of SWOT Analysis")
    st.write("It is important for the analyst to clearly identify the subject of the SWOT analysis and define the market or environment in which it operates.")
    st.write("Examples: Company ABC in the European insurance market, Project XYZ within the IT department, or John Smith within the sales team.")
    
    # Create two columns for parallel input
    col_company, col_env = st.columns(2)

    with col_company:
        st.session_state.company = st.text_input(
            "Enter Analysis Subject (Company / Project / Person)", 
            value=st.session_state.get("company", ""),
            key="company_input"
        )

    with col_env:
        st.session_state.environment = st.text_input(
            "Describe the market or environment in which the subject operates", 
            value=st.session_state.get("environment", ""),
            key="environment_input"
        )

    st.write("Add factors for each category and set their impact on competitive position from 1 (Lowest) to 10 (Highest). Also assess the probability of occurrence or continuation for each factor from 0.1 (Low/unlikely) to 1.0 (High/likely).")

    # --- Factor Input ---
    cols = st.columns(4)
    categories = ["Strengths", "Weaknesses", "Opportunities", "Threats"]
    for i, category in enumerate(categories):
        with cols[i]:
            factor_input_ui(category)

    # ---Table, Chart and Export ---
    # Displaying Company and Environment in the results
    st.header(f"Results of the SWOT Analysis for {st.session_state.company}")
    st.subheader(f"Market or Environment: {st.session_state.environment}")

    factors_with_score = calculate_multiplying_impact_prob(st.session_state.factors)

    if factors_with_score:
        # Generating the results table
        st.subheader("SWOT Factors Ranked by Priority Score")
    
        df = pd.DataFrame(factors_with_score)
        df = df.sort_values("impact_prob", ascending=False)  # Sorting in descending order
        
        # Start the ranking from 1 rather than 0
        df.insert(0, "Rank", range(1, len(df) + 1))

        # Rename columns for display
        df_display = df.rename(columns={
            "Rank": "Rank",
            "category": "Category",
            "name": "Factor",
            "impact": "Impact",
            "probability": "Probability",
            "impact_prob": "Priority Score (Impact x Probability)"
        })

        # Copy the table
        table_df = df_display.copy()

        # Reset the pandas index
        table_df = table_df.reset_index(drop=True)

        # Generate HTML without the index
        table_html = table_df.to_html(
            index=False,
            formatters={
                "Probability": lambda value: f"{value:.1f}",
                "Priority Score (Impact x Probability)": lambda value: f"{value:.1f}"
            },
            border=0,
            classes="swot-table"
        )

        # Add visible borders and styling
        table_html = f"""
        <style>
        .swot-table {{
            width: 100%;
            border-collapse: collapse;
            border: 2px solid #555555;
            font-size: 14px;
        }}

        .swot-table th,
        .swot-table td {{
            border: 1px solid #777777;
            padding: 8px;
        }}

        .swot-table th {{
            background-color: #e9ecef;
            color: #000000;
            font-weight: bold;
            text-align: center;
        }}

        .swot-table td {{
            background-color: white;
            color: #000000;
        }}

        .swot-table td:first-child {{
            text-align: center;
        }}

        .swot-table td:nth-child(5),
        .swot-table td:nth-child(6) {{
            text-align: right;
        }}
        </style>

        {table_html}
        """

        # Displaying the HTML table
        st.html(table_html)

        # Displaying the scatterplot chart with Rank
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["impact"],
            y=df["probability"],
            text=df["Rank"],
            mode="markers+text",
            textposition="top right",
            textfont=dict(size=14, color="black"),
            marker=dict(
                size=30,
                color=df["impact_prob"],
                colorscale="Greys",
                showscale=True,
                colorbar=dict(title="Priority Score<br>(Impact × Probability)"),
                line=dict(width=2, color="black")
            ),
            name="SWOT Factors"
        ))


        # Adding horizontal lines (from x=1 to x=10)
        fig.add_shape(type="line", x0=1, x1=10, y0=0.1, y1=0.1, line=dict(dash="solid", color="gray", width=2))
        fig.add_shape(type="line", x0=1, x1=10, y0=0.55, y1=0.55, line=dict(dash="dot", color="gray"))
        fig.add_shape(type="line", x0=1, x1=10, y0=1.0, y1=1.0, line=dict(dash="solid", color="gray", width=2))

        # Adding vertical lines (from y=1 to y=1)
        fig.add_shape(type="line", x0=1, x1=1, y0=0.1, y1=1, line=dict(dash="solid", color="gray", width=2))
        fig.add_shape(type="line", x0=5.5, x1=5.5, y0=0.1, y1=1, line=dict(dash="dot", color="gray"))
        fig.add_shape(type="line", x0=10, x1=10, y0=0.1, y1=1, line=dict(dash="solid", color="gray", width=2))

        fig.add_annotation(
            text="Average<br>Impact",
            x=5.5,
            y=1.05,
            xref="x",
            yref="y",
            showarrow=False,
            font=dict(size=12, color="light grey"),
        )
        fig.add_annotation(
            text="Average<br>Probability",
            x=11,
            y=0.55,
            xref="x",
            yref="y",
            showarrow=False,
            font=dict(size=12, color="light grey"),
        )
        fig.add_annotation(
            text="Immediate<br>Priority",
            x=7.75,
            y=0.775,
            xref="x",
            yref="y",
            showarrow=False,
            font=dict(size=26, color="gainsboro"),
        )
        fig.add_annotation(
            text="Strategic<br>Monitoring",
            x=7.75,
            y=0.325,
            xref="x",
            yref="y",
            showarrow=False,
            font=dict(size=26, color="gainsboro"),
        )
        fig.add_annotation(
            text="Operational<br>Management",
            x=3.25,
            y=0.775,
            xref="x",
            yref="y",
            showarrow=False,
            font=dict(size=26, color="gainsboro"),
        )
        fig.add_annotation(
            text="Low<br>Priority",
            x=3.25,
            y=0.325,
            xref="x",
            yref="y",
            showarrow=False,
            font=dict(size=26, color="gainsboro"),
        )

        fig.update_layout(
            title="SWOT Factors: Impact vs. Probability",
            xaxis_title="Impact (on competitive position)               ",
            yaxis_title="Probability (of occurrence or continuation)",
            hovermode="x unified",
            width=685,
            height=600 ,
            yaxis=dict(  # Removing the horizontal grid lines
                gridcolor="white",
                gridwidth=0
            )
        )

        st.plotly_chart(fig, width="content")

        # --- Exporting ---
        st.subheader("Export Your Analysis")

        # Export Data
        if factors_with_score:
            df = pd.DataFrame(factors_with_score, columns=[
            "Rank", "category", "name", "impact", "probability", "impact_prob"
            ])
            df.columns = ["Rank", "Category", "Factor", "Impact", "Probability", "Priority Score (Impact x Probability)"]
            # CSV
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name="swot_analysis_data.csv",
                mime="text/csv",
            )

            # XLSX
            xlsx_data = convert_to_xlsx(df_display)
            st.download_button(
                label="Download Data as XLSX",
                data=xlsx_data,
                file_name="swot_analysis_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        # Export Chart
        # Export Chart as HTML (without Kaleido)
        html_bytes = fig.to_html(include_plotlyjs=True, full_html=False)
        st.download_button(
            label="Download Chart as HTML",
            data=html_bytes,
            file_name="swot_scatter_chart.html",
            mime="text/html"
        )

        # Defining data for the recommendation table
        advice_data = [
            {
                "Quadrant": "Immediate Priority (High Impact / High Probability)",
                "Strengths": "Leverage and invest. Maximize the strategic value of key strengths.",
                "Weaknesses": "Mitigate immediately. Allocate resources to reduce critical weaknesses.",
                "Opportunities": "Pursue immediately. Invest in capturing high-value opportunities.",
                "Threats": "Respond immediately. Implement mitigation measures and contingency plans."
            },
            {
                "Quadrant": "Strategic Monitoring (High Impact / Low Probability)",
                "Strengths": "Preserve and develop. Maintain capabilities and strengthen strategic advantages.",
                "Weaknesses": "Monitor and prepare mitigation plans. Be ready to respond if their likelihood increases.",
                "Opportunities": "Monitor and prepare. Develop capabilities to exploit opportunities if conditions become favorable.",
                "Threats": "Monitor closely and prepare contingency plans. Review regularly and update response scenarios."
            },
            {
                "Quadrant": "Operational Management (Low Impact / High Probability)",
                "Strengths": "Utilize routinely. Apply strengths in day-to-day operations to maintain performance.",
                "Weaknesses": "Improve incrementally. Address weaknesses through continuous operational improvements.",
                "Opportunities": "Exploit selectively. Capture opportunities when implementation is cost-effective.",
                "Threats": "Manage routinely. Reduce operational impacts through standard management practices."
            },
            {
                "Quadrant": "Low Priority (Low Impact / Low Probability)",
                "Strengths": "Maintain awareness. Preserve strengths with minimal investment.",
                "Weaknesses": "Accept and review periodically. Monitor for changes before allocating significant resources.",
                "Opportunities": "Observe. Reassess if probability or impact increases.",
                "Threats": "Accept and monitor. Periodically reassess risk exposure and external conditions."
            }
        ]

        advice_df = pd.DataFrame(advice_data)

        st.subheader("Recommendations for Interpreting the Results")
        st.table(advice_df)

    else:
        st.info("Add some factors to see the results of the analysis.")

if __name__ == "__main__":
    main()

