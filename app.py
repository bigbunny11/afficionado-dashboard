# ── app.py — Afficionado Coffee Roasters Dashboard ───────────────────────────
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Afficionado Coffee Roasters",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS for a clean look ───────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #4E342E;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #8D6E63;
        margin-top: 0;
    }
    .metric-card {
        background-color: #FFF8F5;
        border-left: 4px solid #795548;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stSelectbox label { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    daily    = pd.read_csv('dashboard_daily_revenue.csv', parse_dates=['date'])
    hourly   = pd.read_csv('dashboard_hourly.csv')
    cats     = pd.read_csv('dashboard_categories.csv')
    models   = pd.read_csv('dashboard_model_results.csv')
    return daily, hourly, cats, models

daily, hourly, cats, models = load_data()

STORE_COLORS = {
    'Astoria':          '#2196F3',
    "Hell's Kitchen":   '#4CAF50',
    'Lower Manhattan':  '#FF9800'
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## ☕ Afficionado Coffee")
st.sidebar.markdown("**Data-Driven Demand Forecasting**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Overview", "⏰ Hourly Demand", "💰 Revenue Trends", "🤖 Model Comparison"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Dataset**")
st.sidebar.markdown("📅 Jan – Jun 2025")
st.sidebar.markdown("🏪 3 Store locations")
st.sidebar.markdown("🧾 149,116 transactions")
st.sidebar.markdown("💵 $698,812 total revenue")

# ════════════════════════════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ════════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":

    st.markdown('<p class="main-header">☕ Afficionado Coffee Roasters</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Data-Driven Forecasting & Peak Demand Prediction | Jan–Jun 2025</p>', unsafe_allow_html=True)
    st.markdown("---")

    # KPI row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", "$698,812", "+growing trend ↑")
    with col2:
        st.metric("Total Transactions", "149,116", "across 3 stores")
    with col3:
        st.metric("Peak Hour", "10:00 AM", "all 3 stores")
    with col4:
        st.metric("Avg Daily Error (baseline)", "~$232", "12-13% MAPE")

    st.markdown("---")

    # Revenue by store — side by side bars
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Total Revenue by Store")
        rev_by_store = daily.groupby('store')['revenue'].sum().reset_index()
        fig = px.bar(
            rev_by_store, x='store', y='revenue',
            color='store',
            color_discrete_map=STORE_COLORS,
            text_auto='$.0f',
            labels={'revenue': 'Total Revenue ($)', 'store': ''}
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, height=350,
                          yaxis_range=[0, rev_by_store['revenue'].max() * 1.15])
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Revenue Share by Category")
        cat_total = cats.groupby('product_category')['revenue'].sum().reset_index()
        fig2 = px.pie(
            cat_total, values='revenue', names='product_category',
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4
        )
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        fig2.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Key findings box
    st.markdown("---")
    st.subheader("🔍 Key EDA Findings")
    f1, f2, f3 = st.columns(3)
    with f1:
        st.info("**10AM Rush is Universal**\nAll 3 stores peak at 10am. Hell's Kitchen hits 106% above its hourly average — the most volatile store.")
    with f2:
        st.info("**Stores Are Revenue-Equal**\nDespite different demand shapes, all 3 stores earn within 3% of each other (~$230–236K over 6 months).")
    with f3:
        st.info("**Business is Growing**\nClear upward revenue trend across all locations from January to June 2025.")

# ════════════════════════════════════════════════════════════════════════════════
# PAGE 2: HOURLY DEMAND
# ════════════════════════════════════════════════════════════════════════════════
elif page == "⏰ Hourly Demand":

    st.markdown('<p class="main-header">⏰ Hourly Demand Patterns</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">When do customers arrive — and which store feels it most?</p>', unsafe_allow_html=True)
    st.markdown("---")

    store_filter = st.selectbox(
        "Select store to highlight",
        ["All Stores"] + list(STORE_COLORS.keys())
    )

    if store_filter == "All Stores":
        hourly_agg = hourly.groupby('hour')['transactions'].sum().reset_index()
        fig = px.bar(
            hourly_agg, x='hour', y='transactions',
            labels={'hour': 'Hour of Day', 'transactions': 'Total Transactions'},
            title='All Stores Combined — Transactions by Hour',
            color='transactions',
            color_continuous_scale='Oranges'
        )
    else:
        hourly_store = hourly[hourly['store'] == store_filter]
        fig = px.bar(
            hourly_store, x='hour', y='transactions',
            labels={'hour': 'Hour of Day', 'transactions': 'Total Transactions'},
            title=f'{store_filter} — Transactions by Hour',
            color='transactions',
            color_continuous_scale='Blues'
        )

    fig.update_layout(height=400, coloraxis_showscale=False)
    fig.add_vline(x=10, line_dash='dash', line_color='red', annotation_text='10AM Peak')
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap
    st.subheader("📊 Demand Heatmap — Hour × Store")
    heatmap_data = hourly.pivot(index='store', columns='hour', values='transactions')
    fig_heat = px.imshow(
        heatmap_data,
        color_continuous_scale='YlOrRd',
        labels={'x': 'Hour of Day', 'y': 'Store', 'color': 'Transactions'},
        title='Transaction Volume Heatmap',
        aspect='auto'
    )
    fig_heat.update_layout(height=300)
    st.plotly_chart(fig_heat, use_container_width=True)

    # Insight box
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Hell's Kitchen Peak", "6,957 txns", "106% above avg")
    with col2:
        st.metric("Lower Manhattan Peak", "6,297 txns", "98% above avg")
    with col3:
        st.metric("Astoria Peak", "5,291 txns", "36% above avg ← steadier")

# ════════════════════════════════════════════════════════════════════════════════
# PAGE 3: REVENUE TRENDS
# ════════════════════════════════════════════════════════════════════════════════
elif page == "💰 Revenue Trends":

    st.markdown('<p class="main-header">💰 Revenue Trends</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Daily revenue patterns, growth trajectory, and day-of-week effects</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Rolling average slider
    roll_window = st.slider("Smoothing window (days)", min_value=1, max_value=14, value=7)

    # Daily revenue trend
    st.subheader("Daily Revenue Trend by Store")
    fig = go.Figure()

    for store, color in STORE_COLORS.items():
        store_data = daily[daily['store'] == store].sort_values('date').copy()
        store_data['smoothed'] = store_data['revenue'].rolling(roll_window, min_periods=1).mean()

        # Raw line (faint)
        fig.add_trace(go.Scatter(
            x=store_data['date'], y=store_data['revenue'],
            mode='lines', name=f'{store} (actual)',
            line=dict(color=color, width=1),
            opacity=0.3, showlegend=False
        ))
        # Smoothed line (bold)
        fig.add_trace(go.Scatter(
            x=store_data['date'], y=store_data['smoothed'],
            mode='lines', name=store,
            line=dict(color=color, width=2.5)
        ))

    fig.update_layout(
        height=420,
        xaxis_title='Date',
        yaxis_title='Daily Revenue ($)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Day of week
    st.subheader("Average Revenue by Day of Week")
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    daily['day_of_week'] = pd.to_datetime(daily['date']).dt.day_name()
    dow = daily.groupby('day_of_week')['revenue'].mean().reindex(day_order).reset_index()

    fig2 = px.bar(
        dow, x='day_of_week', y='revenue',
        labels={'day_of_week': '', 'revenue': 'Avg Revenue ($)'},
        color='day_of_week',
        color_discrete_sequence=['#2196F3']*5 + ['#FF5722']*2
    )
    fig2.update_layout(showlegend=False, height=320)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Note: Weekday vs weekend difference is less than 4% — demand is driven by time of day, not day of week.")

# ════════════════════════════════════════════════════════════════════════════════
# PAGE 4: MODEL COMPARISON
# ════════════════════════════════════════════════════════════════════════════════
elif page == "🤖 Model Comparison":

    st.markdown('<p class="main-header">🤖 Forecasting Model Comparison</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Baseline vs Prophet vs XGBoost — which model forecasts best?</p>', unsafe_allow_html=True)
    st.markdown("---")

    # MAPE comparison chart
    st.subheader("MAPE by Model & Store (lower = better)")

    mape_data = pd.DataFrame({
        'Store':   ['Astoria', "Hell's Kitchen", 'Lower Manhattan'] * 3,
        'Model':   ['Baseline']*3 + ['Prophet']*3 + ['XGBoost']*3,
        'MAPE':    [12.4, 13.2, 12.7, 14.4, 14.4, 13.9, 13.3, 16.3, 12.0]
    })

    fig = px.bar(
        mape_data, x='Model', y='MAPE', color='Store',
        barmode='group',
        color_discrete_map=STORE_COLORS,
        labels={'MAPE': 'MAPE (%)', 'Model': ''},
        text='MAPE'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.add_hline(y=12, line_dash='dot', line_color='red',
                  annotation_text='Target <12%')
    fig.update_layout(height=420, yaxis_range=[0, 20])
    st.plotly_chart(fig, use_container_width=True)

    # Results table
    st.subheader("Detailed Results")
    results_table = pd.DataFrame({
        'Store':            ['Astoria', "Hell's Kitchen", 'Lower Manhattan'],
        'Baseline MAPE':    ['12.4%', '13.2%', '12.7%'],
        'Prophet MAPE':     ['14.4%', '14.4%', '13.9%'],
        'XGBoost MAPE':     ['13.3%', '16.3%', '12.0%'],
        'Winner':           ['Baseline', 'Baseline', 'XGBoost'],
        'MAE (best model)': ['$228', '$243', '$231']
    })
    st.dataframe(results_table, use_container_width=True, hide_index=True)

    # Honest conclusion
    st.markdown("---")
    st.subheader("📝 Honest Model Conclusion")
    st.warning("""
    **Why the baseline is hard to beat with 6 months of data:**
    All three models perform within 12–16% MAPE. The XGBoost feature importance
    revealed that *week number* and *month* dominate predictions — meaning the
    primary signal is the business growth trend, which the moving average already
    partially captures.

    **What 12+ months of data would unlock:**
    Yearly seasonality (summer vs winter demand), holiday effects, and stronger
    weekly patterns — all of which would give Prophet and XGBoost a clear edge.

    **The real value of this project is the VISIBILITY it creates** — not the
    marginal accuracy improvement, but the ability to quantify the 10AM rush,
    identify Hell's Kitchen as the highest-risk store, and measure $130K+ in
    annual planning risk.
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ Best overall model: **XGBoost** (Lower Manhattan, 12.0% MAPE)")
    with col2:
        st.error("⚠️ Hardest to forecast: **Hell's Kitchen** (most volatile, 16.3%)")
        
