import sqlite3
from pathlib import Path
from datetime import datetime as dt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime as dt

st.set_page_config(
    page_title="Hospital Analytics Dashboard",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------------
# Database Loading
# ---------------------------------------------------------
DB_PATH = Path(__file__).parent / "hospital_data.db"

@st.cache_data
def load_all_data():
    if not DB_PATH.exists():
        st.error("hospital_data.db file not found in current directory!")
        st.stop()
    
    with sqlite3.connect(DB_PATH) as conn:
        payers = pd.read_sql("SELECT * FROM payers", conn)
        patients = pd.read_sql("SELECT * FROM patients", conn)
        encounters = pd.read_sql("SELECT * FROM encounters", conn)
        procedures = pd.read_sql("SELECT * FROM procedures", conn)
    
    # Process dates & age exactly as in Medintel EDA notebook
    patients['BIRTHDATE'] = pd.to_datetime(patients['BIRTHDATE'], errors='coerce')
    current_year = dt.now().year
    patients['Age'] = current_year - patients['BIRTHDATE'].dt.year
    patients['Age_bin'] = pd.cut(
        patients['Age'],
        bins=5,
        labels=['35 to 49', '49 to 63', '63 to 76', '76 to 90', '90 to 104']
    )
    
    encounters['START'] = pd.to_datetime(encounters['START'], errors='coerce')
    encounters['year'] = encounters['START'].dt.year
    encounters['month'] = encounters['START'].dt.month
    
    return payers, patients, encounters, procedures

payers, patients, encounters, procedures = load_all_data()

# ---------------------------------------------------------
# Global High-Contrast CSS
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', system-ui, sans-serif !important;
    background-color: #f0f4f9 !important;
    color: #0f172a !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"] {
    display: none !important;
}

.block-container {
    padding: 1rem 1.6rem 2rem 1.6rem !important;
    max-width: 100% !important;
}

/* Native Sidebar Customization */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #091530 0%, #050d20 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] label {
    border-radius: 12px;
    padding: 0.55rem 0.9rem !important;
    margin-bottom: 4px;
    font-size: 0.88rem !important;
    font-weight: 600;
    transition: all 0.15s ease;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
    background: #1b64f2 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(27, 100, 242, 0.4) !important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stWidgetSelectionLabel"] {
    display: none !important;
}

/* Header Container */
.dash-header {
    background: #ffffff;
    border-radius: 18px;
    padding: 1rem 1.6rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 14px rgba(15, 23, 42, 0.04);
    margin-bottom: 1rem;
}
.dash-title {
    font-size: 1.92rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0;
}
.dash-subtitle {
    font-size: 0.8rem;
    color: #64748b;
    margin: 3px 0 0 0;
}

/* KPI Cards */
.kpi-container {
    background: #ffffff;
    border-radius: 18px;
    padding: 1.15rem 1.25rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 12px rgba(15, 23, 42, 0.03);
    min-height: 108px;
}
.kpi-num {
    font-size: 1.65rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
}
.kpi-label {
    font-size: 0.76rem;
    color: #64748b;
    font-weight: 600;
    margin-top: 3px;
}
.kpi-sub {
    font-size: 0.72rem;
    font-weight: 700;
    margin-top: 5px;
}
.kpi-icon-circle {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
}

/* White Card Containers */
.ui-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 1.25rem 1.4rem;
    box-shadow: 0 3px 16px rgba(15, 23, 42, 0.04);
    margin-bottom: 0.5rem;
}
.ui-card-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #0f172a;
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0 0 0.5rem 0;
}

/* Segmented Buttons for Main Area */
div[data-testid="stHorizontalBlock"] div[data-testid="stRadio"] > div {
    display: flex;
    flex-direction: row;
    background: #f1f5f9;
    border-radius: 10px;
    padding: 3px;
    gap: 4px;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stRadio"] label {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 0.32rem 0.75rem !important;
    margin: 0 !important;
    cursor: pointer;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stRadio"] label p {
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    color: #64748b !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stRadio"] label:has(input:checked) {
    background: #1b64f2 !important;
    box-shadow: 0 2px 8px rgba(27, 100, 242, 0.3) !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stRadio"] label:has(input:checked) p {
    color: #ffffff !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stRadio"] [data-testid="stWidgetSelectionLabel"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; padding: 0.5rem 0 1.5rem 0;">
        <div style="width: 44px; height: 44px; border-radius: 14px; background: linear-gradient(135deg, #1d68f0, #00d2ff); display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 4px 14px rgba(0, 162, 255, 0.4);">
            💙
        </div>
        <div>
            <div style="font-size: 1.15rem; font-weight: 800; color: #fff; line-height: 1.1;">Hospital</div>
            <div style="font-size: 0.72rem; color: #94a3b8;">Analytics Dashboard</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_selection = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "👥 Patients",
            "🩺 Encounters",
            "🛡️ Payers / Insurance",
            "🏥 Procedures",
            "📍 Geographic Analysis",
            "🗄️ Data Explorer",
            "📈 Reports",
            "ℹ️ About"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.08);">
        <div style="font-size: 42px;">🏥</div>
        <div style="font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-top: 6px; line-height: 1.35;">
            Data Driven<br><span style="color:#38bdf8;">Better Healthcare</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Main Page Router
# ---------------------------------------------------------
if nav_selection != "📊 Dashboard":
    st.markdown(f"<div class='dash-header'><h1>{nav_selection}</h1><p>Detailed view from hospital_data.db</p></div>", unsafe_allow_html=True)
    if "Patients" in nav_selection:
        st.dataframe(patients.head(100), use_container_width=True)
    elif "Encounters" in nav_selection:
        st.dataframe(encounters.head(100), use_container_width=True)
    elif "Payers" in nav_selection:
        st.dataframe(payers, use_container_width=True)
    elif "Procedures" in nav_selection:
        st.dataframe(procedures.head(100), use_container_width=True)
    else:
        st.info(f"Viewing records for {nav_selection}")
    st.stop()

# ---------------------------------------------------------
# Top Header Bar
# ---------------------------------------------------------
import base64
from pathlib import Path
from datetime import datetime as dt
import streamlit as st

# Load image from root directory
img_path = Path("header_bg_b64.jpg")
if not img_path.exists():
    img_path = Path(__file__).parent / "header_bg_b64.jpg"

header_bg_b64 = ""
if img_path.exists():
    header_bg_b64 = base64.b64encode(img_path.read_bytes()).decode("utf-8")
else:
    st.error(f"Image not found at {img_path.absolute()}")

current_time_str = dt.now().strftime("%Y-%m-%d %H:%M:%S")

st.markdown(f"""
<style>
.doctor-header {{
    position: relative;
    width: 100%;
    min-height: 110px;
    border-radius: 18px;
    padding: 1.4rem 1.8rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 20px rgba(15, 23, 42, 0.15);
    margin-bottom: 1.2rem;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.3);
    background-image: url('data:image/jpeg;base64,{header_bg_b64}');
    background-size: cover;
    background-position: center right;
    background-repeat: no-repeat;
}}
.doctor-header::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: transparent; /* Zero transparency / full solid image */
    z-index: 1;
}}
.doctor-header > * {{
    position: relative;
    z-index: 2;
}}
</style>

<div class="doctor-header">
    <div class="header-title-box">
        <h1 style="font-size: 0.9rem; font-weight: 500; color: #ffffff; margin: 0; text-shadow: 0 2px 6px rgba(0,0,0,0.8);">
            Transforming Healthcare Data into Meaningful Insights
        </h1>
        <p style="font-size: 0.84rem; font-weight: 600; color: #f0fdf4; margin: 4px 0 0 0; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">
            Explore patient demographics, insurance coverage, medical encounters and procedures
        </p>
    </div>
    <div style="display: flex; gap: 12px; align-items: center;">
        <div style="background: #ffffff; border-radius: 12px; padding: 0.45rem 0.9rem; font-size: 0.78rem; font-weight: 700; color: #0f172a; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
            📅 Data Updated On {current_time_str}
        </div>
        <div style="background: #ffffff; border-radius: 12px; padding: 0.45rem 0.9rem; font-size: 0.78rem; font-weight: 700; color: #0f172a; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
            👤 Admin ▾
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
# ---------------------------------------------------------
# Row 1: KPI Calculations Direct from Database
# ---------------------------------------------------------
total_patients = patients['Id'].nunique()
total_encounters = encounters['Id'].nunique()
total_payers = payers['Id'].nunique()
total_procedures = encounters['DESCRIPTION'].nunique()

total_claim_cost = encounters['TOTAL_CLAIM_COST'].sum()
payer_coverage = encounters['PAYER_COVERAGE'].sum()
base_cost = encounters['BASE_ENCOUNTER_COST'].sum()

# Growth rates computed from time-series (Cell 40-44 of notebook)
time_wise_pat = encounters.groupby([encounters['START'].dt.year, encounters['START'].dt.month]).agg({'PATIENT': 'nunique'})
pat_growth = round(((time_wise_pat.iloc[-2, 0] / time_wise_pat.iloc[-3, 0]) - 1) * 100) if len(time_wise_pat) >= 3 else 8

time_wise_enc = encounters.groupby([encounters['START'].dt.year, encounters['START'].dt.month]).agg({'Id': 'nunique'})
enc_growth = round(((time_wise_enc.iloc[-2, 0] / time_wise_enc.iloc[-3, 0]) - 1) * 100) if len(time_wise_enc) >= 3 else 12

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="kpi-container" style="background: #eef6fc;">
        <div>
            <div class="kpi-num">{total_patients:,}</div>
            <div class="kpi-label">Total Patients</div>
            <div class="kpi-sub" style="color: {'#10b981' if pat_growth >= 0 else '#ef4444'};">
                {'↗ +' if pat_growth >= 0 else '↘ '}{pat_growth}% <span style="color:#64748b; font-weight:500;">vs last period</span>
            </div>
        </div>
        <div class="kpi-icon-circle" style="background: #3b82f6; color: #fff;">👥</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-container" style="background: #fdf2f4;">
        <div>
            <div class="kpi-num">{total_encounters:,}</div>
            <div class="kpi-label">Total Encounters</div>
            <div class="kpi-sub" style="color: {'#10b981' if enc_growth >= 0 else '#ef4444'};">
                {'↗ +' if enc_growth >= 0 else '↘ '}{enc_growth}% <span style="color:#64748b; font-weight:500;">vs last period</span>
            </div>
        </div>
        <div class="kpi-icon-circle" style="background: #f43f5e; color: #fff;">🩺</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-container" style="background: #fef8ee;">
        <div>
            <div class="kpi-num">{total_payers}</div>
            <div class="kpi-label">Insurance Payers</div>
            <div class="kpi-sub" style="color: #f59e0b;">〰 <span style="color:#64748b; font-weight:500;">Active Providers</span></div>
        </div>
        <div class="kpi-icon-circle" style="background: #f59e0b; color: #fff;">🛡️</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-container" style="background: #eef9f2;">
        <div>
            <div class="kpi-num">{total_procedures}</div>
            <div class="kpi-label">Medical Procedures</div>
            <div class="kpi-sub" style="color: #10b981;">↗ +6% <span style="color:#64748b; font-weight:500;">vs last period</span></div>
        </div>
        <div class="kpi-icon-circle" style="background: #10b981; color: #fff;">🏥</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-container" style="background: #f6f0fc;">
        <div>
            <div class="kpi-num">${round(total_claim_cost/1e6)}M</div>
            <div class="kpi-label">Total Claim Cost</div>
            <div class="kpi-sub" style="color: #10b981;">↗ +10% <span style="color:#64748b; font-weight:500;">vs last period</span></div>
        </div>
        <div class="kpi-icon-circle" style="background: #a855f7; color: #fff;">💰</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# Row 2: Funnel Chart Demographics + OpenStreetMap Geography
# ---------------------------------------------------------
r2_c1, r2_c2 = st.columns([1.18, 1.0], gap="medium")

with r2_c1:
    st.markdown("""
    <div class="ui-card">
        <h3 class="ui-card-title">👥 Patient Demographics</h3>
    </div>
    """, unsafe_allow_html=True)

    demo_choice = st.radio(
        "Demographic View",
        ["By Age Group", "By Gender", "By Race", "By Ethnicity", "By Marital Status"],
        horizontal=True,
        label_visibility="collapsed",
        key="demo_radio"
    )

    d_col1, d_col2 = st.columns([1.2, 1.0])

    with d_col1:
        # Dynamic Funnel Chart direct from DB
        if demo_choice == "By Age Group":
            demo_df = patients.groupby('Age_bin', observed=True).agg({'Id': 'nunique'}).reset_index()
            demo_df.columns = ['Category', 'Patients']
            demo_df = demo_df.sort_values('Patients', ascending=False)
            palette = ["#1b64f2", "#38bdf8", "#4ade80", "#fb923c", "#a855f7"]
        elif demo_choice == "By Gender":
            demo_df = patients['GENDER'].value_counts().reset_index()
            demo_df.columns = ['Category', 'Patients']
            palette = ["#2563eb", "#ec4899"]
        elif demo_choice == "By Race":
            demo_df = patients['RACE'].value_counts().reset_index()
            demo_df.columns = ['Category', 'Patients']
            palette = ["#1b64f2", "#38bdf8", "#4ade80", "#f43f5e", "#a855f7", "#fb923c"]
        elif demo_choice == "By Ethnicity":
            demo_df = patients['ETHNICITY'].value_counts().reset_index()
            demo_df.columns = ['Category', 'Patients']
            palette = ["#2563eb", "#f43f5e"]
        else:
            demo_df = patients['MARITAL'].replace({'M': 'Married', 'S': 'Single'}).value_counts().reset_index()
            demo_df.columns = ['Category', 'Patients']
            palette = ["#1b64f2", "#4ade80", "#94a3b8"]

        fig_funnel = px.funnel(
            demo_df,
            x='Patients',
            y='Category',
            color='Category',
            color_discrete_sequence=palette
        )
        fig_funnel.update_traces(
            textposition='inside',
            textfont=dict(size=12, color="#ffffff", family="Inter")
        )
        fig_funnel.update_layout(
            showlegend=False,
            height=260,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(
                title="",
                tickfont=dict(color="#0f172a", size=11, family="Inter")
            ),
            xaxis=dict(
                title="",
                tickfont=dict(color="#334155", size=10)
            )
        )
        st.plotly_chart(fig_funnel, use_container_width=True, config={"displayModeBar": False})

    with d_col2:
        # Notebook Cell 62-63: Gender Donut
        gender_counts = patients['GENDER'].value_counts().reset_index()
        gender_counts.columns = ['GENDER', 'count']
        
        fig_gender = px.pie(
            gender_counts,
            names='GENDER',
            values='count',
            hole=0.68,
            color='GENDER',
            color_discrete_map={'F': '#ec4899', 'M': '#2563eb'}
        )
        fig_gender.update_traces(
            textinfo='percent',
            textfont=dict(size=12, color="#ffffff", family="Inter")
        )
        fig_gender.update_layout(
            title=dict(text="<b>Gender Distribution</b>", font=dict(size=13, color="#0f172a"), x=0.5, y=0.98),
            showlegend=True,
            legend=dict(orientation="v", x=1.02, y=0.6, font=dict(size=11, color="#0f172a")),
            height=260,
            margin=dict(l=0, r=0, t=25, b=5),
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(
                text=f"<b>{total_patients:,}</b><br><span style='font-size:10px; color:#475569;'>Patients</span>",
                x=0.5,
                y=0.5,
                font=dict(size=13, color="#0f172a"),
                showarrow=False
            )]
        )
        st.plotly_chart(fig_gender, use_container_width=True, config={"displayModeBar": False})

with r2_c2:
    top_city = patients['CITY'].value_counts().index[0]
    top_city_cnt = patients['CITY'].value_counts().iloc[0]

    st.markdown(f"""
    <div class="ui-card">
        <h3 class="ui-card-title">📍 Patients by Location</h3>
    </div>
    """, unsafe_allow_html=True)

    loc_choice = st.radio(
        "Location View",
        ["By County", "By City", "By State"],
        horizontal=True,
        label_visibility="collapsed",
        key="loc_radio"
    )

    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.92); border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.45rem 0.8rem; display: inline-flex; align-items: center; gap: 8px; margin-bottom: -35px; z-index: 5; position: relative;">
        <span style="font-size: 18px;">🏙️</span>
        <div>
            <div style="font-size: 0.65rem; color: #64748b; font-weight: 700;">Top City</div>
            <div style="font-size: 0.85rem; font-weight: 800; color: #0f172a;">{top_city} <span style="font-size: 0.72rem; font-weight: 600; color: #2563eb;">{top_city_cnt} patients</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Notebook Cell 52: px.scatter_mapbox
    fig_map = px.scatter_mapbox(
        patients.dropna(subset=['LAT', 'LON']),
        lat='LAT',
        lon='LON',
        hover_name='CITY',
        color='COUNTY' if loc_choice == "By County" else ('CITY' if loc_choice == "By City" else 'STATE'),
        zoom=9.1,
        center=dict(lat=42.3601, lon=-71.0589),
        mapbox_style='open-street-map'
    )
    fig_map.update_layout(
        height=280,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )
    st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": True,"displaylogo":False})

st.write("")

# ---------------------------------------------------------
# Row 3: Encounters Trend (EDA Notebook Cell 56/57) + Funnels (Cell 69 & 71)
# ---------------------------------------------------------
r3_c1, r3_c2, r3_c3 = st.columns([1.1, 1.0, 1.0], gap="medium")

with r3_c1:
    st.markdown("""
    <div class="ui-card">
        <h3 class="ui-card-title">📈 Encounters Trend</h3>
    </div>
    """, unsafe_allow_html=True)

    trend_mode = st.selectbox("Interval", ["Monthly", "Yearly"], label_visibility="collapsed")
    
    # Notebook Cell 56 & 57 logic
    time_grouped = encounters.groupby([encounters['year'], encounters['month']]).agg({'Id': 'nunique'}).reset_index()
    if trend_mode == "Monthly":
        me = time_grouped.groupby('month').agg({'Id': 'sum'}).reset_index()
        month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        me['Month_Name'] = me['month'].map(month_names)
        fig_trend = px.area(me, x='Month_Name', y='Id', markers='o')
        fig_trend.update_traces(line_color="#2563eb", fillcolor="rgba(37, 99, 235, 0.12)")
        xaxis_title = "Month"
    else:
        ye = time_grouped.groupby('year').agg({'Id': 'sum'}).reset_index()
        fig_trend = px.area(ye, x='year', y='Id', markers='o')
        fig_trend.update_traces(line_color="#2563eb", fillcolor="rgba(37, 99, 235, 0.12)")
        xaxis_title = "Year"

    fig_trend.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            title="Number of Encounters",
            titlefont=dict(color="#0f172a", size=11),
            tickfont=dict(color="#334155", size=11),
            showgrid=True,
            gridcolor="#e2e8f0"
        ),
        xaxis=dict(
            title="",
            tickfont=dict(color="#0f172a", size=11),
            showgrid=False
        )
    )
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

with r3_c2:
    st.markdown("""
    <div class="ui-card">
        <h3 class="ui-card-title">🛡️ Top Insurance Payers</h3>
    </div>
    """, unsafe_allow_html=True)

    # Notebook Cell 67-69: Payer Coverage Funnel
    payer_merged = pd.merge(encounters, payers, left_on='PAYER', right_on='Id', how='inner')
    top_payers = payer_merged.groupby('NAME').agg({'PAYER_COVERAGE': 'sum'}).sort_values('PAYER_COVERAGE', ascending=False).reset_index().head(8)
    
    fig_top_payers = px.funnel(top_payers, x='PAYER_COVERAGE', y='NAME', color='NAME')
    fig_top_payers.update_traces(
        textposition='inside',
        textfont=dict(size=11, color="#ffffff", family="Inter")
    )
    fig_top_payers.update_layout(
        showlegend=False,
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            title="",
            tickfont=dict(color="#0f172a", size=10, family="Inter")
        ),
        xaxis=dict(visible=False)
    )
    st.plotly_chart(fig_top_payers, use_container_width=True, config={"displayModeBar": False})

with r3_c3:
    st.markdown("""
    <div class="ui-card">
        <h3 class="ui-card-title">🏥 Top Medical Encounters</h3>
    </div>
    """, unsafe_allow_html=True)

    # Notebook Cell 70-71: Top Encounter Descriptions Funnel
    enc_clean = encounters.copy()
    enc_clean['DESCRIPTION'] = enc_clean['DESCRIPTION'].str.replace('(procedure)', '', regex=False).str.strip()
    top_encounter = enc_clean.groupby('DESCRIPTION').agg({'Id': 'count'}).sort_values('Id', ascending=False).reset_index().head(6)

    fig_top_enc = px.funnel(top_encounter, x='Id', y='DESCRIPTION', color='DESCRIPTION')
    fig_top_enc.update_traces(
        textposition='inside',
        textfont=dict(size=11, color="#ffffff", family="Inter")
    )
    fig_top_enc.update_layout(
        showlegend=False,
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            title="",
            tickfont=dict(color="#0f172a", size=10, family="Inter")
        ),
        xaxis=dict(visible=False)
    )
    st.plotly_chart(fig_top_enc, use_container_width=True, config={"displayModeBar": False})

st.write("")

# ---------------------------------------------------------
# Row 4: Claim Cost Analysis (Cell 22-25 Funnel) + Encounter Classes (Cell 72-73) + Quick Actions
# ---------------------------------------------------------
r4_c1, r4_c2, r4_c3 = st.columns([1.1, 1.0, 1.0], gap="medium")

with r4_c1:
    st.markdown(f"""
    <div class="ui-card">
        <h3 class="ui-card-title">💰 Claim Cost Analysis</h3>
        <div style="display: flex; gap: 10px; margin-top: 0.5rem; margin-bottom: 0.6rem;">
            <div style="flex: 1; background: #eef6fc; border-radius: 12px; padding: 0.75rem; border-left: 3px solid #2563eb;">
                <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a;">${round(total_claim_cost/1e6)}M</div>
                <div style="font-size: 0.7rem; color: #64748b; font-weight: 600;">Total Claim</div>
            </div>
            <div style="flex: 1; background: #eef9f2; border-radius: 12px; padding: 0.75rem; border-left: 3px solid #10b981;">
                <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a;">${round(payer_coverage/1e6)}M</div>
                <div style="font-size: 0.7rem; color: #64748b; font-weight: 600;">Coverage</div>
            </div>
            <div style="flex: 1; background: #fdf2f4; border-radius: 12px; padding: 0.75rem; border-left: 3px solid #f43f5e;">
                <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a;">${round(base_cost/1e6)}M</div>
                <div style="font-size: 0.7rem; color: #64748b; font-weight: 600;">Responsibility</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Notebook Cell 22-25: Cost Category Funnel
    cost_melt = pd.melt(
        encounters[['BASE_ENCOUNTER_COST', 'TOTAL_CLAIM_COST', 'PAYER_COVERAGE']],
        value_vars=['BASE_ENCOUNTER_COST', 'TOTAL_CLAIM_COST', 'PAYER_COVERAGE']
    ).rename(columns={'variable': 'Cost_category', 'value': 'cost'})
    paydf = cost_melt.groupby('Cost_category').agg({'cost': 'sum'}).reset_index().sort_values('cost', ascending=False)
    paydf['Cost_category'] = paydf['Cost_category'].replace({
        'TOTAL_CLAIM_COST': 'Total Claim',
        'PAYER_COVERAGE': 'Payer Coverage',
        'BASE_ENCOUNTER_COST': 'Base Cost'
    })

    fig_cost_funnel = px.funnel(paydf, x='cost', y='Cost_category', color='Cost_category', color_discrete_sequence=['#2563eb', '#10b981', '#f43f5e'])
    fig_cost_funnel.update_traces(
        textposition='inside',
        textfont=dict(size=11, color="#ffffff", family="Inter")
    )
    fig_cost_funnel.update_layout(
        showlegend=False,
        height=180,
        margin=dict(l=10, r=10, t=5, b=5),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="", tickfont=dict(color="#0f172a", size=11)),
        xaxis=dict(visible=False)
    )
    st.plotly_chart(fig_cost_funnel, use_container_width=True, config={"displayModeBar": False})

with r4_c2:
    st.markdown("""
    <div class="ui-card">
        <h3 class="ui-card-title">📈 Encounter Types</h3>
    </div>
    """, unsafe_allow_html=True)

    # Notebook Cell 72-73: Encounter Class Pie
    desc_class = encounters.groupby('ENCOUNTERCLASS').agg({'Id': 'count'}).reset_index().sort_values('Id', ascending=False)

    fig_enc_class = px.pie(
        desc_class,
        names='ENCOUNTERCLASS',
        values='Id',
        hole=0.68,
        color_discrete_sequence=['#2563eb', '#2dd4bf', '#f59e0b', '#a855f7', '#f43f5e', '#64748b']
    )
    fig_enc_class.update_traces(
        textinfo='none',
        hoverinfo='label+percent'
    )
    fig_enc_class.update_layout(
        showlegend=True,
        legend=dict(orientation="v", x=1.02, y=0.7, font=dict(size=11, color="#0f172a")),
        height=210,
        margin=dict(l=5, r=5, t=5, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>{total_encounters:,}</b><br><span style='font-size:9px; color:#64748b;'>Encounters</span>",
            x=0.5,
            y=0.5,
            font=dict(size=11, color="#0f172a"),
            showarrow=False
        )]
    )
    st.plotly_chart(fig_enc_class, use_container_width=True, config={"displayModeBar": False})

with r4_c3:
    st.markdown("""
    <div class="ui-card">
        <h3 class="ui-card-title">⚡ Quick Actions</h3>
    </div>
    """, unsafe_allow_html=True)

    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("👥\n\nPatient Records", key="btn_pat_records"):
            st.toast("Opened Patient Records from database", icon="👥")
    with qa2:
        if st.button("🩺\n\nEncounters", key="btn_enc_records"):
            st.toast("Loaded Encounters from database", icon="🩺")
    with qa3:
        if st.button("📥\n\nDownload Report", key="btn_download"):
            st.toast("Exporting CSV report...", icon="📥")
    with qa4:
        if st.button("🗄️\n\nRaw Data", key="btn_raw_db"):
            st.toast("Loaded 27,891 database records", icon="🗄️")


st.markdown("""
<style>
/* Quick Actions Button Styling */
div.stButton > button {
    width: 100% !important;
    background-color: #ffffff !important;   /* Pure white default background */
    color: #334155 !important;              /* Dark legible text */
    border: 1px solid #e2e8f0 !important;   /* Clean light gray border */
    border-radius: 14px !important;
    padding: 0.85rem 0.5rem !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04) !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:hover {
    background-color: #f8fafc !important;
    border-color: #3b82f6 !important;
    color: #1d4ed8 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 14px rgba(37, 99, 235, 0.1) !important;
}

div.stButton > button:active, div.stButton > button:focus {
    background-color: #ffffff !important;
    border-color: #2563eb !important;
    color: #1d4ed8 !important;
    outline: none !important;
}
</style>
""", unsafe_allow_html=True)