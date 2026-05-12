import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from api import (
    get_crop_distribution,
    get_crop_distribution_matrix,
    get_administrative_by_parent,
)

st.set_page_config(
    page_title="Crop Statistics - AgriConnect",
    page_icon=":ear_of_rice:",
    layout="wide",
)

# Load external CSS and icons
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
<style>
    div[data-testid="stMetric"] {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        padding: 1rem;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #cbd5e1;
    }
    [data-testid="stMetricValue"] {
        font-weight: 600;
    }
    .section-title {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e2e8f0;
    }
    .info-banner {
        background: #f8fafc;
        border-left: 3px solid #3b82f6;
        padding: 1rem;
        margin: 1rem 0;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
    }
    .matrix-table {
        width: 100%;
        border-collapse: collapse;
    }
    .matrix-table th, .matrix-table td {
        border: 1px solid #e2e8f0;
        padding: 0.5rem;
        text-align: right;
    }
    .matrix-table th {
        background: #f8fafc;
        font-weight: 600;
    }
    .matrix-table td:first-child, .matrix-table th:first-child {
        text-align: left;
    }
    .matrix-table tr:last-child {
        font-weight: 600;
        background: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin: 0;">
        <i class="fa-solid fa-seedling" style="color: #64748b; margin-right: 0.5rem;"></i>
        Crop Statistics
    </h1>
    <p style="color: #64748b; margin-top: 0.25rem; font-size: 0.875rem;">
        Farmer distribution by crop type
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar filters
st.sidebar.markdown("""
<p style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b;">
    <i class="fa-regular fa-calendar"></i> Date Range
</p>
""", unsafe_allow_html=True)

col1, col2 = st.sidebar.columns(2)
first_of_last_month = date.today().replace(day=1) - date.resolution
first_of_last_month = first_of_last_month.replace(day=1)
with col1:
    start_date = st.date_input(
        "From",
        value=first_of_last_month,
        max_value=date.today(),
    )
with col2:
    end_date = st.date_input(
        "To",
        value=date.today(),
        max_value=date.today(),
    )

st.sidebar.markdown("---")
st.sidebar.markdown("""
<p style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b;">
    <i class="fa-solid fa-location-dot"></i> Location
</p>
""", unsafe_allow_html=True)

# Cascade admin filter
administrative_id = None
selected_region_name = "All Regions"
selected_district_name = "All Districts"

# Load regions
regions_data = get_administrative_by_parent(1)
region_options = {"All Regions": None}
if regions_data and "administrative" in regions_data:
    for r in sorted(regions_data["administrative"], key=lambda x: x["name"]):
        region_options[r["name"]] = r["id"]

selected_region_label = st.sidebar.selectbox(
    "Region",
    list(region_options.keys()),
    index=0,
)
selected_region_id = region_options[selected_region_label]
selected_region_name = selected_region_label

# Set administrative_id to region if selected
if selected_region_id:
    administrative_id = selected_region_id

    # Load districts
    districts_data = get_administrative_by_parent(selected_region_id)
    district_options = {"All Districts": None}
    if districts_data and "administrative" in districts_data:
        for d in sorted(districts_data["administrative"], key=lambda x: x["name"]):
            district_options[d["name"]] = d["id"]

    selected_district_label = st.sidebar.selectbox(
        "District",
        list(district_options.keys()),
    )
    selected_district_id = district_options[selected_district_label]
    selected_district_name = selected_district_label

    # Override administrative_id to district if selected
    if selected_district_id:
        administrative_id = selected_district_id

# Show filter path
filter_parts = []
if selected_region_name and selected_region_name != "All Regions":
    filter_parts.append(selected_region_name)
if selected_district_name and selected_district_name != "All Districts":
    filter_parts.append(selected_district_name)
if filter_parts:
    st.sidebar.caption(f"-> {' / '.join(filter_parts)}")

# Fetch data
with st.spinner("Loading..."):
    distribution_data = get_crop_distribution(
        start_date=start_date,
        end_date=end_date,
        administrative_id=administrative_id,
    )
    matrix_data = get_crop_distribution_matrix(
        start_date=start_date,
        end_date=end_date,
        administrative_id=administrative_id,
    )

if distribution_data and distribution_data.get("crops"):
    crops = distribution_data["crops"]
    total_farmers = distribution_data.get("total", 0)
    num_crop_types = len(crops)
    top_crop = crops[0]["crop"] if crops else "—"

    # Summary Cards
    st.markdown("""
    <p class="section-title"><i class="fa-solid fa-chart-simple"></i> Summary</p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Farmers", value=f"{total_farmers:,}")
    with col2:
        st.metric(label="Crop Types", value=f"{num_crop_types:,}")
    with col3:
        st.metric(label="Top Crop", value=top_crop)

    st.markdown("<br>", unsafe_allow_html=True)

    # Horizontal Bar Chart
    st.markdown("""
    <p class="section-title"><i class="fa-solid fa-chart-bar"></i> Farmer Distribution by Crop</p>
    """, unsafe_allow_html=True)

    df = pd.DataFrame(crops)
    fig = px.bar(
        df,
        x="count",
        y="crop",
        orientation="h",
        labels={"count": "Number of Farmers", "crop": "Crop Type"},
    )
    fig.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        height=max(300, len(crops) * 35),
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis_title=None,
        xaxis_title=None,
        plot_bgcolor="white",
    )
    fig.update_traces(
        marker_color="#3b82f6",
        text=df["count"],
        textposition="inside",
        textfont=dict(color="white"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    # Matrix Table
    if matrix_data and matrix_data.get("matrix"):
        matrix = matrix_data["matrix"]
        crop_types = matrix_data.get("crop_types", [])
        level_name = matrix_data.get("level_name", "County")

        st.markdown(f"""
        <p class="section-title"><i class="fa-solid fa-table-cells"></i> Crop Distribution by {level_name}</p>
        """, unsafe_allow_html=True)

        # Build rows for DataFrame
        rows = []
        for row in matrix:
            row_data = {level_name: row["county"]}
            for crop in crop_types:
                row_data[crop] = row["crops"].get(crop, 0)
            row_data["Total"] = row["total"]
            rows.append(row_data)

        matrix_df = pd.DataFrame(rows)

        # Add totals row
        totals = {level_name: "Total"}
        for crop in crop_types:
            totals[crop] = matrix_df[crop].sum()
        totals["Total"] = matrix_df["Total"].sum()
        matrix_df = pd.concat([matrix_df, pd.DataFrame([totals])], ignore_index=True)

        # Summary banner
        st.markdown(f"""
        <div class="info-banner">
            <strong>{len(matrix)}</strong> {level_name.lower()}s ·
            <strong>{len(crop_types)}</strong> crop types ·
            <strong>{totals['Total']:,}</strong> total farmers
        </div>
        """, unsafe_allow_html=True)

        # Display the dataframe
        st.dataframe(
            matrix_df,
            use_container_width=True,
            hide_index=True,
        )

        # Download button
        csv = matrix_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="crop_distribution_by_county.csv",
            mime="text/csv",
        )
    else:
        st.info("No location-level data available for selected filters.")

else:
    if distribution_data is None:
        st.error("Failed to load data. Check API connection.")
    else:
        st.info("No crop data available for selected filters.")
