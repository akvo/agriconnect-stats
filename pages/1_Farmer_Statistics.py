import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from api import (
    get_farmer_stats,
    get_farmer_stats_by_ward,
    get_farmer_registrations,
    get_administrative_by_parent,
    get_aggregate_farmers,
)

st.set_page_config(
    page_title="Farmer Statistics - AgriConnect",
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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin: 0;">
        <i class="fa-solid fa-wheat-awn" style="color: #64748b; margin-right: 0.5rem;"></i>
        Farmer Statistics
    </h1>
    <p style="color: #64748b; margin-top: 0.25rem; font-size: 0.875rem;">
        Onboarding, activity, and engagement metrics
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

# Fetch aggregate data first to get available crop types
initial_aggregate = get_aggregate_farmers(level="region")
all_crop_types = initial_aggregate.get("available", {}).get("crop_types", []) if initial_aggregate else []

# Crop type filter (shown first so it can affect location options)
st.sidebar.markdown("---")
selected_crop_type = None
if all_crop_types:
    st.sidebar.markdown("""
    <p style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b;">
        <i class="fa-solid fa-seedling"></i> Crop Type
    </p>
    """, unsafe_allow_html=True)

    crop_options = ["All Crops"] + sorted(all_crop_types)
    selected_crop = st.sidebar.selectbox(
        "Crop",
        crop_options,
        index=0,
        label_visibility="collapsed",
    )
    if selected_crop != "All Crops":
        selected_crop_type = selected_crop

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

# Fetch aggregate data with crop filter to get available areas
aggregate_data = get_aggregate_farmers(level="region", crop_type=selected_crop_type)
available = aggregate_data.get("available", {}) if aggregate_data else {}
available_region_ids = {r["id"] for r in available.get("regions", [])}
available_district_ids = {d["id"] for d in available.get("districts", [])}
available_ward_ids = {w["id"] for w in available.get("wards", [])}

# Load regions - show all, mark those without data with indicator
regions_data = get_administrative_by_parent(1)
region_options = {"All Regions": None}
if regions_data and "administrative" in regions_data:
    for r in sorted(regions_data["administrative"], key=lambda x: x["name"]):
        has_data = r["id"] in available_region_ids
        label = r["name"] if has_data else f"{r['name']} (no data)"
        region_options[label] = r["id"]

selected_region_label = st.sidebar.selectbox(
    "Region",
    list(region_options.keys()),
    index=0,
)
selected_region_id = region_options[selected_region_label]
# Extract clean name for filter path display
selected_region_name = selected_region_label.replace(" (no data)", "")

# Set administrative_id to region if selected
if selected_region_id:
    administrative_id = selected_region_id

    # Load districts - show all, mark those without data
    districts_data = get_administrative_by_parent(selected_region_id)
    district_options = {"All Districts": None}
    if districts_data and "administrative" in districts_data:
        for d in sorted(districts_data["administrative"], key=lambda x: x["name"]):
            has_data = d["id"] in available_district_ids
            label = d["name"] if has_data else f"{d['name']} (no data)"
            district_options[label] = d["id"]

    selected_district_label = st.sidebar.selectbox(
        "District",
        list(district_options.keys()),
    )
    selected_district_id = district_options[selected_district_label]
    selected_district_name = selected_district_label.replace(" (no data)", "")

    # Override administrative_id to district if selected
    if selected_district_id:
        administrative_id = selected_district_id

        # Load wards - show all, mark those without data
        wards_data = get_administrative_by_parent(selected_district_id)
        ward_options = {"All Wards": None}
        if wards_data and "administrative" in wards_data:
            for w in sorted(wards_data["administrative"], key=lambda x: x["name"]):
                has_data = w["id"] in available_ward_ids
                label = w["name"] if has_data else f"{w['name']} (no data)"
                ward_options[label] = w["id"]

        selected_ward_label = st.sidebar.selectbox(
            "Ward",
            list(ward_options.keys()),
        )
        selected_ward_id = ward_options[selected_ward_label]
        selected_ward_name = selected_ward_label.replace(" (no data)", "")

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

# Determine the breakdown level based on current selection
# We fetch the 2nd lower level to create stacked bars grouped by 1st lower level
if selected_ward_name != "All Wards":
    breakdown_level = None  # Ward selected, no further breakdown
    breakdown_admin_id = None
    group_by_level = None
elif selected_district_name != "All Districts":
    breakdown_level = "ward"  # Fetch wards, but no grouping (single district)
    breakdown_admin_id = selected_district_id
    group_by_level = None
elif selected_region_name != "All Regions":
    breakdown_level = "ward"  # Fetch wards, group by district
    breakdown_admin_id = selected_region_id
    group_by_level = "district"
else:
    breakdown_level = "district"  # Fetch districts, group by region
    breakdown_admin_id = None
    group_by_level = "region"

# Fetch data with administrative_id and crop_type filters
with st.spinner("Loading..."):
    stats = get_farmer_stats(
        start_date=start_date,
        end_date=end_date,
        administrative_id=administrative_id,
        phone_prefix="+254",
        crop_type=selected_crop_type,
    )
    stats_by_ward = get_farmer_stats_by_ward(
        start_date=start_date,
        end_date=end_date,
        administrative_id=administrative_id,
        phone_prefix="+254",
        crop_type=selected_crop_type,
    )
    registrations = get_farmer_registrations(
        start_date=start_date,
        end_date=end_date,
        administrative_id=administrative_id,
        phone_prefix="+254",
        crop_type=selected_crop_type,
        group_by="day",
    )
    # Fetch aggregate data for breakdown chart
    breakdown_data = None
    if breakdown_level:
        breakdown_data = get_aggregate_farmers(
            level=breakdown_level,
            administrative_id=breakdown_admin_id,
            crop_type=selected_crop_type,
            start_date=start_date,
            end_date=end_date,
        )

if stats:
    # Breakdown stacked bar chart
    if breakdown_data and breakdown_data.get("data"):
        breakdown_df = pd.DataFrame(breakdown_data["data"])
        if not breakdown_df.empty:
            fig = go.Figure()

            if group_by_level:
                # Extract parent from path for grouping
                # Path format: "Kenya > Region > District > Ward"
                path_parts = breakdown_df["path"].str.split(" > ")
                if group_by_level == "region":
                    breakdown_df["parent"] = path_parts.str[1]  # Region is 2nd part
                    level_label = "Region"
                elif group_by_level == "district":
                    breakdown_df["parent"] = path_parts.str[2]  # District is 3rd part
                    level_label = "District"

                # Get unique parents and children
                parents = breakdown_df["parent"].unique()
                parents_sorted = sorted(parents, key=lambda p: breakdown_df[breakdown_df["parent"] == p]["farmer_count"].sum(), reverse=False)

                # Create color palette for children
                colors = px.colors.qualitative.Set2

                # Get all unique children with their paths for legend
                # Create a mapping of name to path for legend labels
                child_paths = breakdown_df.drop_duplicates("name").set_index("name")["path"].to_dict()
                # Sort children by path to group them by parent in legend
                all_children = sorted(breakdown_df["name"].unique(), key=lambda x: child_paths.get(x, x))
                child_colors = {child: colors[i % len(colors)] for i, child in enumerate(all_children)}

                # Add traces for each child (stacked within parent)
                for child in all_children:
                    child_data = breakdown_df[breakdown_df["name"] == child]
                    x_vals = []
                    y_vals = []
                    text_vals = []
                    for parent in parents_sorted:
                        parent_child = child_data[child_data["parent"] == parent]
                        if not parent_child.empty:
                            x_vals.append(parent_child["farmer_count"].values[0])
                            text_vals.append(str(parent_child["farmer_count"].values[0]))
                        else:
                            x_vals.append(0)
                            text_vals.append("")
                        y_vals.append(parent)

                    # Use path for legend (remove "Kenya > " prefix for brevity)
                    legend_label = child_paths.get(child, child)
                    if legend_label.startswith("Kenya > "):
                        legend_label = legend_label[8:]  # Remove "Kenya > "

                    fig.add_trace(go.Bar(
                        y=y_vals,
                        x=x_vals,
                        name=legend_label,
                        orientation="h",
                        marker_color=child_colors[child],
                        text=text_vals,
                        textposition="inside",
                        textfont=dict(color="white", size=10),
                    ))

                chart_height = max(200, len(parents_sorted) * 40)
            else:
                # No grouping - just show breakdown level directly
                level_label = breakdown_level.title() if breakdown_level else ""
                chart_df = breakdown_df[["name", "farmer_count"]].copy()
                chart_df = chart_df.sort_values("farmer_count", ascending=True)

                fig.add_trace(go.Bar(
                    y=chart_df["name"],
                    x=chart_df["farmer_count"],
                    name="Farmers",
                    orientation="h",
                    marker_color="#3b82f6",
                    text=chart_df["farmer_count"],
                    textposition="inside",
                    textfont=dict(color="white"),
                ))
                chart_height = max(200, len(chart_df) * 35)

            st.markdown(f"""
            <p class="section-title"><i class="fa-solid fa-chart-bar"></i> Farmers by {level_label}</p>
            """, unsafe_allow_html=True)

            fig.update_layout(
                barmode="stack",
                height=chart_height,
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02,
                    font=dict(size=10),
                ),
                xaxis=dict(showgrid=True, gridcolor="#f1f5f9", fixedrange=True),
                yaxis=dict(showgrid=False, fixedrange=True),
                plot_bgcolor="white",
            )
            st.plotly_chart(fig, use_container_width=True, config={
                "displayModeBar": False,
                "scrollZoom": False,
            })

            # Additional charts for questions and escalations
            additional_metrics = [
                ("questions_count", "Questions", "#10b981"),
                ("escalations_count", "Escalations", "#f59e0b"),
            ]

            for metric_key, metric_label, metric_color in additional_metrics:
                fig_metric = go.Figure()

                if group_by_level:
                    for child in all_children:
                        child_data = breakdown_df[breakdown_df["name"] == child]
                        x_vals = []
                        y_vals = []
                        text_vals = []
                        for parent in parents_sorted:
                            parent_child = child_data[child_data["parent"] == parent]
                            if not parent_child.empty:
                                val = parent_child[metric_key].values[0]
                                x_vals.append(val)
                                text_vals.append(str(val) if val > 0 else "")
                            else:
                                x_vals.append(0)
                                text_vals.append("")
                            y_vals.append(parent)

                        legend_label = child_paths.get(child, child)
                        if legend_label.startswith("Kenya > "):
                            legend_label = legend_label[8:]

                        fig_metric.add_trace(go.Bar(
                            y=y_vals,
                            x=x_vals,
                            name=legend_label,
                            orientation="h",
                            marker_color=child_colors[child],
                            text=text_vals,
                            textposition="inside",
                            textfont=dict(color="white", size=10),
                        ))
                else:
                    chart_df_metric = breakdown_df[["name", metric_key]].copy()
                    chart_df_metric = chart_df_metric.sort_values(metric_key, ascending=True)

                    fig_metric.add_trace(go.Bar(
                        y=chart_df_metric["name"],
                        x=chart_df_metric[metric_key],
                        name=metric_label,
                        orientation="h",
                        marker_color=metric_color,
                        text=chart_df_metric[metric_key],
                        textposition="inside",
                        textfont=dict(color="white"),
                    ))

                st.markdown(f"""
                <p class="section-title"><i class="fa-solid fa-chart-bar"></i> {metric_label} by {level_label}</p>
                """, unsafe_allow_html=True)

                fig_metric.update_layout(
                    barmode="stack",
                    height=chart_height,
                    margin=dict(l=0, r=0, t=10, b=0),
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.02,
                        font=dict(size=10),
                    ),
                    xaxis=dict(showgrid=True, gridcolor="#f1f5f9", fixedrange=True),
                    yaxis=dict(showgrid=False, fixedrange=True),
                    plot_bgcolor="white",
                )
                st.plotly_chart(fig_metric, use_container_width=True, config={
                    "displayModeBar": False,
                    "scrollZoom": False,
                })

            st.markdown("<br>", unsafe_allow_html=True)
    # Onboarding Section
    st.markdown("""
    <p class="section-title"><i class="fa-solid fa-clipboard-check"></i> Onboarding</p>
    """, unsafe_allow_html=True)

    onboarding = stats.get("onboarding", {})
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Started",
            value=f"{onboarding.get('started', 0):,}",
        )
    with col2:
        st.metric(
            label="Completed",
            value=f"{onboarding.get('completed', 0):,}",
        )
    with col3:
        completion_rate = onboarding.get("completion_rate", 0)
        started = onboarding.get("started", 0)
        completed = onboarding.get("completed", 0)
        st.metric(
            label="Completion Rate",
            value=f"{completion_rate * 100:.1f}%",
        )
        st.markdown(f"""
        <div class="metric-info">
            <i class="fa-solid fa-circle-info"></i>
            <span class="tooltip-text">{completed:,} completed ÷ {started:,} started × 100</span>
        </div>
        """, unsafe_allow_html=True)

    # Activity Section
    st.markdown("""
    <p class="section-title"><i class="fa-solid fa-chart-line"></i> Activity (30 days)</p>
    """, unsafe_allow_html=True)

    activity = stats.get("activity", {})
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Active Farmers",
            value=f"{activity.get('active_farmers', 0):,}",
        )
    with col2:
        st.metric(
            label="Dormant Farmers",
            value=f"{activity.get('dormant_farmers', 0):,}",
        )
    with col3:
        active_rate = activity.get("active_rate", 0)
        active_farmers = activity.get("active_farmers", 0)
        completed = onboarding.get("completed", 0)
        st.metric(
            label="Active Rate",
            value=f"{active_rate * 100:.1f}%",
        )
        st.markdown(f"""
        <div class="metric-info">
            <i class="fa-solid fa-circle-info"></i>
            <span class="tooltip-text">{active_farmers:,} active ÷ {completed:,} completed × 100</span>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        avg_days = activity.get("avg_days_to_first_question")
        st.metric(
            label="Avg Days to First Question",
            value=f"{avg_days:.1f}" if avg_days else "—",
        )
    with col2:
        avg_questions = activity.get("avg_questions_per_farmer")
        st.metric(
            label="Avg Questions per Farmer",
            value=f"{avg_questions:.1f}" if avg_questions else "—",
        )

    # Features & Escalations
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <p class="section-title"><i class="fa-solid fa-cloud-sun"></i> Features</p>
        """, unsafe_allow_html=True)
        features = stats.get("features", {})
        st.metric(
            label="Weather Subscribers",
            value=f"{features.get('weather_subscribers', 0):,}",
        )

    with col2:
        st.markdown("""
        <p class="section-title"><i class="fa-solid fa-arrow-up-right-from-square"></i> Escalations</p>
        """, unsafe_allow_html=True)
        escalations = stats.get("escalations", {})
        c1, c2 = st.columns(2)
        with c1:
            st.metric(
                label="Total Escalated",
                value=f"{escalations.get('total_escalated', 0):,}",
            )
        with c2:
            st.metric(
                label="Farmers Escalated",
                value=f"{escalations.get('farmers_who_escalated', 0):,}",
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Registration charts
    if registrations and registrations.get("data"):
        reg_df = pd.DataFrame(registrations["data"])
        reg_df["date"] = pd.to_datetime(reg_df["date"])
        reg_df = reg_df.sort_values("date")
        reg_df["cumulative"] = reg_df["count"].cumsum()

        # Cumulative chart
        st.markdown("""
        <p class="section-title"><i class="fa-solid fa-chart-area"></i> Cumulative Registrations</p>
        """, unsafe_allow_html=True)

        fig = px.area(
            reg_df,
            x="date",
            y="cumulative",
            labels={"date": "", "cumulative": ""},
        )
        fig.update_traces(
            fill="tozeroy",
            fillcolor="rgba(59, 130, 246, 0.1)",
            line_color="#3b82f6",
            line_width=2,
        )
        fig.update_layout(
            hovermode="x unified",
            height=250,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Daily chart
        st.markdown("""
        <p class="section-title"><i class="fa-solid fa-chart-line"></i> Daily Registrations</p>
        """, unsafe_allow_html=True)

        fig2 = px.line(
            reg_df,
            x="date",
            y="count",
            labels={"date": "", "count": ""},
        )
        fig2.update_traces(
            line_color="#3b82f6",
            line_width=2,
        )
        fig2.update_layout(
            hovermode="x unified",
            height=200,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            plot_bgcolor="white",
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", f"{registrations.get('total', 0):,}")
        with col2:
            if len(reg_df) > 0:
                peak_date = reg_df.loc[reg_df["count"].idxmax(), "date"].strftime("%b %d")
                peak_count = reg_df["count"].max()
                st.metric("Peak Day", f"{peak_count:,} ({peak_date})")
        with col3:
            if len(reg_df) > 0:
                st.metric("Daily Avg", f"{reg_df['count'].mean():.1f}")
    else:
        st.info("No registration data for selected period.")

    # Stats by ward table - show breakdown for region/district level
    if stats_by_ward and stats_by_ward.get("data"):
        ward_df = pd.DataFrame(stats_by_ward["data"])

        if not ward_df.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <p class="section-title"><i class="fa-solid fa-table"></i> Breakdown by Ward</p>
            """, unsafe_allow_html=True)

            display_df = ward_df.rename(
                columns={
                    "ward_name": "Ward",
                    "ward_path": "Location",
                    "registered_farmers": "Registered",
                    "incomplete_registration": "Incomplete",
                    "farmers_with_questions": "Asked",
                    "total_questions": "Questions",
                    "farmers_who_escalated": "Escalated",
                    "total_escalations": "Escalations",
                }
            )

            columns_to_show = [
                "Ward", "Location", "Registered", "Incomplete",
                "Asked", "Questions", "Escalated", "Escalations",
            ]
            columns_available = [c for c in columns_to_show if c in display_df.columns]

            # Summary
            st.markdown(f"""
            <div class="info-banner">
                <strong>{len(display_df)}</strong> wards ·
                <strong>{display_df['Registered'].sum():,}</strong> farmers ·
                <strong>{display_df['Questions'].sum():,}</strong> questions ·
                <strong>{display_df['Escalations'].sum():,}</strong> escalations
            </div>
            """, unsafe_allow_html=True)

            st.dataframe(
                display_df[columns_available],
                use_container_width=True,
                hide_index=True,
            )

            csv = display_df[columns_available].to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="farmer_stats_by_ward.csv",
                mime="text/csv",
            )

else:
    st.error("Failed to load data. Check API connection.")
