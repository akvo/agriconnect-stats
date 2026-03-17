import streamlit as st

st.set_page_config(
    page_title="AgriConnect Statistics",
    page_icon=":seedling:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load external CSS and icons
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
<style>
    .nav-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s;
    }
    .nav-card:hover {
        border-color: #3b82f6;
    }
    .nav-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .nav-desc {
        font-size: 0.875rem;
        color: #64748b;
        margin-bottom: 1rem;
    }
    .feature-item {
        font-size: 0.8rem;
        color: #64748b;
        padding: 0.25rem 0;
    }
    .tip-box {
        background: #f8fafc;
        border-left: 3px solid #64748b;
        padding: 1rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin: 0;">
        <i class="fa-solid fa-seedling" style="color: #64748b; margin-right: 0.5rem;"></i>
        AgriConnect Statistics
    </h1>
    <p style="color: #64748b; margin-top: 0.25rem; font-size: 0.875rem;">
        Farmer engagement and extension officer performance insights
    </p>
</div>
""", unsafe_allow_html=True)

# Navigation
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="nav-card">
        <p class="nav-title"><i class="fa-solid fa-wheat-awn" style="margin-right: 0.5rem; color: #64748b;"></i>Farmer Statistics</p>
        <p class="nav-desc">Onboarding, activity, and engagement metrics</p>
        <p class="feature-item"><i class="fa-solid fa-check" style="width: 1rem; color: #94a3b8;"></i> Onboarding completion rates</p>
        <p class="feature-item"><i class="fa-solid fa-check" style="width: 1rem; color: #94a3b8;"></i> Active vs dormant analysis</p>
        <p class="feature-item"><i class="fa-solid fa-check" style="width: 1rem; color: #94a3b8;"></i> Weather subscriptions</p>
        <p class="feature-item"><i class="fa-solid fa-check" style="width: 1rem; color: #94a3b8;"></i> Escalation tracking</p>
        <p class="feature-item"><i class="fa-solid fa-check" style="width: 1rem; color: #94a3b8;"></i> Registration trends</p>
        <p class="feature-item"><i class="fa-solid fa-check" style="width: 1rem; color: #94a3b8;"></i> Ward-level breakdown</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Open Farmer Statistics", use_container_width=True):
        st.switch_page("pages/1_Farmer_Statistics.py")

with col2:
    st.markdown("""
    <div class="nav-card">
        <p class="nav-title"><i class="fa-solid fa-user-tie" style="margin-right: 0.5rem; color: #64748b;"></i>DC/EO Statistics</p>
        <p class="nav-desc">Extension officer performance and ticket handling</p>
        <p class="feature-item"><i class="fa-solid fa-check" style="width: 1rem; color: #94a3b8;"></i> Open/closed tickets</p>
        <p class="feature-item"><i class="fa-solid fa-check" style="width: 1rem; color: #94a3b8;"></i> Response time analysis</p>
        <p class="feature-item"><i class="fa-solid fa-check" style="width: 1rem; color: #94a3b8;"></i> Resolution rates</p>
        <p class="feature-item"><i class="fa-solid fa-check" style="width: 1rem; color: #94a3b8;"></i> Bulk messaging stats</p>
        <p class="feature-item"><i class="fa-solid fa-check" style="width: 1rem; color: #94a3b8;"></i> EO distribution by area</p>
        <p class="feature-item"><i class="fa-solid fa-check" style="width: 1rem; color: #94a3b8;"></i> Performance rankings</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Open DC/EO Statistics", use_container_width=True):
        st.switch_page("pages/2_DC_EO_Statistics.py")

# Tips
st.markdown("""
<div class="tip-box">
    <p style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin-bottom: 0.5rem;">
        <i class="fa-solid fa-lightbulb"></i> Tips
    </p>
    <p style="font-size: 0.8rem; color: #64748b; margin: 0;">
        Use date filters to focus on specific periods · Drill down by location (Region → District → Ward) · Download data as CSV for further analysis
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("""
<p style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b;">
    <i class="fa-solid fa-compass"></i> Navigation
</p>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
Select a page from the sidebar to view statistics.

**Pages:**
- Farmer Statistics
- DC/EO Statistics
""")
