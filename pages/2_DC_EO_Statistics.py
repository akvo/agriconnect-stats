import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from api import (
    get_eo_stats,
    get_eo_stats_by_eo,
    get_eo_count,
    get_administrative_by_parent,
)

st.set_page_config(
    page_title="DC/EO Statistics - AgriConnect",
    page_icon=":seedling:",
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
    .metric-info {
        position: relative;
        margin-top: -3.5rem;
        margin-bottom: 2rem;
        text-align: right;
        padding-right: 0.5rem;
        z-index: 100;
    }
    .metric-info i {
        color: #94a3b8;
        cursor: help;
        font-size: 0.75rem;
    }
    .metric-info:hover i {
        color: #64748b;
    }
    .metric-info .tooltip-text {
        visibility: hidden;
        background-color: #1e293b;
        color: #fff;
        text-align: left;
        padding: 0.5rem 0.75rem;
        border-radius: 4px;
        position: absolute;
        z-index: 1000;
        top: 1.25rem;
        right: 0.5rem;
        width: max-content;
        max-width: 200px;
        font-size: 0.75rem;
        font-weight: 400;
        line-height: 1.4;
        opacity: 0;
        transition: opacity 0.2s;
    }
    .metric-info:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
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
    .status-good { color: #16a34a; }
    .status-warning { color: #ca8a04; }
    .status-poor { color: #dc2626; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin: 0;">
        <i class="fa-solid fa-user-tie" style="color: #64748b; margin-right: 0.5rem;"></i>
        DC/EO Statistics
    </h1>
    <p style="color: #64748b; margin-top: 0.25rem; font-size: 0.875rem;">
        Extension officer performance and ticket metrics
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

# Cascade admin filter - track the selected administrative_id at any level
administrative_id = None
selected_region_name = "All Regions"
selected_district_name = "All Districts"
selected_ward_name = "All Wards"

# Load regions (children of parent_id=1)
regions_data = get_administrative_by_parent(1)
region_options = {"All Regions": None}
if regions_data and "administrative" in regions_data:
    for r in sorted(regions_data["administrative"], key=lambda x: x["name"]):
        region_options[r["name"]] = r["id"]

selected_region_name = st.sidebar.selectbox(
    "Region",
    list(region_options.keys()),
    index=0,
)
selected_region_id = region_options[selected_region_name]

# Set administrative_id to region if selected
if selected_region_id:
    administrative_id = selected_region_id

    # Load districts for drill-down
    districts_data = get_administrative_by_parent(selected_region_id)
    district_options = {"All Districts": None}
    if districts_data and "administrative" in districts_data:
        for d in sorted(districts_data["administrative"], key=lambda x: x["name"]):
            district_options[d["name"]] = d["id"]

    selected_district_name = st.sidebar.selectbox(
        "District",
        list(district_options.keys()),
    )
    selected_district_id = district_options[selected_district_name]

    # Override administrative_id to district if selected
    if selected_district_id:
        administrative_id = selected_district_id

        # Load wards for drill-down
        wards_data = get_administrative_by_parent(selected_district_id)
        ward_options = {"All Wards": None}
        if wards_data and "administrative" in wards_data:
            for w in sorted(wards_data["administrative"], key=lambda x: x["name"]):
                ward_options[w["name"]] = w["id"]

        selected_ward_name = st.sidebar.selectbox(
            "Ward",
            list(ward_options.keys()),
        )
        selected_ward_id = ward_options[selected_ward_name]

        # Override administrative_id to ward if selected
        if selected_ward_id:
            administrative_id = selected_ward_id

# Show filter path
filter_parts = []
if selected_region_name and selected_region_name != "All Regions":
    filter_parts.append(selected_region_name)
if selected_district_name and selected_district_name != "All Districts":
    filter_parts.append(selected_district_name)
if selected_ward_name and selected_ward_name != "All Wards":
    filter_parts.append(selected_ward_name)
if filter_parts:
    st.sidebar.caption(f"→ {' / '.join(filter_parts)}")

# Fetch data with administrative_id filter
with st.spinner("Loading..."):
    stats = get_eo_stats(
        start_date=start_date,
        end_date=end_date,
        administrative_id=administrative_id,
    )
    stats_by_eo = get_eo_stats_by_eo(
        start_date=start_date,
        end_date=end_date,
        administrative_id=administrative_id,
    )
    eo_count = get_eo_count(administrative_id=administrative_id)

if stats:
    # Tickets Section
    st.markdown("""
    <p class="section-title"><i class="fa-solid fa-ticket"></i> Tickets</p>
    """, unsafe_allow_html=True)

    tickets = stats.get("tickets", {})
    open_tickets = tickets.get("open", 0)
    closed_tickets = tickets.get("closed", 0)
    total_tickets = open_tickets + closed_tickets
    resolution_rate = (closed_tickets / total_tickets * 100) if total_tickets > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Open", value=f"{open_tickets:,}")
    with col2:
        st.metric(label="Closed", value=f"{closed_tickets:,}")
    with col3:
        st.metric(label="Resolution Rate", value=f"{resolution_rate:.1f}%")
        st.markdown(f"""
        <div class="metric-info">
            <i class="fa-solid fa-circle-info"></i>
            <span class="tooltip-text">{closed_tickets:,} closed ÷ {total_tickets:,} total × 100</span>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        avg_response = tickets.get("avg_response_time_hours")
        st.metric(
            label="Avg Response Time",
            value=f"{avg_response:.1f}h" if avg_response else "—",
        )

    # Ticket charts
    if total_tickets > 0:
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure(data=[go.Pie(
                labels=["Closed", "Open"],
                values=[closed_tickets, open_tickets],
                hole=0.6,
                marker_colors=["#3b82f6", "#e2e8f0"],
                textinfo="percent",
                textposition="inside",
            )])
            fig.update_layout(
                height=280,
                margin=dict(l=40, r=40, t=40, b=60),
                showlegend=True,
                legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5),
                annotations=[dict(text=f"{resolution_rate:.0f}%", x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with col2:
            if avg_response:
                if avg_response <= 4:
                    status = "Excellent"
                    status_class = "status-good"
                elif avg_response <= 12:
                    status = "Good"
                    status_class = "status-good"
                elif avg_response <= 24:
                    status = "Fair"
                    status_class = "status-warning"
                else:
                    status = "Needs Improvement"
                    status_class = "status-poor"

                st.markdown(f"""
                <div style="text-align: center; padding: 2rem;">
                    <p style="font-size: 3rem; font-weight: 600; color: #1e293b; margin: 0;">{avg_response:.1f}h</p>
                    <p style="color: #64748b; margin: 0.5rem 0;">Average Response Time</p>
                    <p class="{status_class}" style="font-weight: 600;">{status}</p>
                </div>
                """, unsafe_allow_html=True)

    # Messages & EO Count Section
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <p class="section-title"><i class="fa-solid fa-envelope"></i> Bulk Messaging</p>
        """, unsafe_allow_html=True)
        messages = stats.get("messages", {})
        st.metric(label="Messages Sent", value=f"{messages.get('bulk_messages_sent', 0):,}")

    with col2:
        st.markdown("""
        <p class="section-title"><i class="fa-solid fa-users"></i> Extension Officers</p>
        """, unsafe_allow_html=True)
        if eo_count:
            st.metric(label="Total EOs", value=f"{eo_count.get('count', 0):,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats by EO
    if stats_by_eo and stats_by_eo.get("data"):
        eo_df = pd.DataFrame(stats_by_eo["data"])

        if not eo_df.empty:
            st.markdown("""
            <p class="section-title"><i class="fa-solid fa-ranking-star"></i> Performance by Officer</p>
            """, unsafe_allow_html=True)

            eo_df = eo_df.sort_values("eo_name")

            total_replies = eo_df["total_replies"].sum()
            total_closed = eo_df["tickets_closed"].sum()

            st.markdown(f"""
            <div class="info-banner">
                <strong>{len(eo_df)}</strong> officers ·
                <strong>{total_replies:,}</strong> replies ·
                <strong>{total_closed:,}</strong> tickets closed
            </div>
            """, unsafe_allow_html=True)

            display_df = eo_df.rename(
                columns={
                    "eo_name": "Name",
                    "district": "Sub-County",
                    "total_replies": "Replies",
                    "tickets_closed": "Closed",
                }
            )
            columns_to_show = ["Name", "Sub-County", "Replies", "Closed"]
            columns_available = [c for c in columns_to_show if c in display_df.columns]

            st.dataframe(
                display_df[columns_available],
                use_container_width=True,
                hide_index=True,
            )

            # Charts
            col1, col2 = st.columns(2)
            with col1:
                chart_df = display_df.sort_values("Replies", ascending=True).tail(10)
                fig = px.bar(
                    chart_df,
                    y="Name",
                    x="Replies",
                    orientation="h",
                    labels={"Name": "", "Replies": ""},
                )
                fig.update_traces(marker_color="#3b82f6")
                fig.update_layout(
                    title=dict(text="Top 10 by Replies", font=dict(size=12, color="#64748b")),
                    height=350,
                    margin=dict(l=0, r=0, t=30, b=0),
                    xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
                    yaxis=dict(showgrid=False),
                    plot_bgcolor="white",
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            with col2:
                chart_df = display_df.sort_values("Closed", ascending=True).tail(10)
                fig = px.bar(
                    chart_df,
                    y="Name",
                    x="Closed",
                    orientation="h",
                    labels={"Name": "", "Closed": ""},
                )
                fig.update_traces(marker_color="#64748b")
                fig.update_layout(
                    title=dict(text="Top 10 by Tickets Closed", font=dict(size=12, color="#64748b")),
                    height=350,
                    margin=dict(l=0, r=0, t=30, b=0),
                    xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
                    yaxis=dict(showgrid=False),
                    plot_bgcolor="white",
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            csv = display_df[columns_available].to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="eo_statistics.csv",
                mime="text/csv",
            )

else:
    st.error("Failed to load data. Check API connection.")
