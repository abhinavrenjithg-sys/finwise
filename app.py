"""
FinWise – Smart Financial Calculator
====================================

A Loan EMI Calculator and SIP Calculator built with Python, Streamlit,
Plotly and NumPy.

Run with:
    streamlit run app.py

Project layout (everything lives in this one file, split into sections):
    1. Page configuration and theme (CSS)
    2. Helper functions  -> Indian Rupee formatting, CSV reports
    3. Calculation logic -> EMI, amortization schedule, SIP
    4. Chart builders    -> Plotly figures
    5. UI components     -> input rows with sliders, metric cards
    6. Pages             -> EMI page, SIP page, About page
    7. Main              -> sidebar navigation and footer
"""

import csv
import io
from datetime import date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# 1. PAGE CONFIGURATION AND THEME
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="FinWise – Smart Financial Calculator",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="auto",  # open on desktop, collapsed on phones,
)

# Brand colours (our own palette – not copied from any other company)
PRIMARY = "#0E9F6E"        # main green
PRIMARY_DARK = "#065F46"   # dark green for headings
PRIMARY_LIGHT = "#ECFDF5"  # very light green for backgrounds
SECONDARY = "#9ADBC3"      # soft green used for "interest" / "invested" parts
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#64748B"
BORDER = "#E2E8F0"

# Default values used on first load and when "Reset" is pressed
EMI_DEFAULTS = {"loan_amount": 1_000_000, "loan_rate": 8.5, "loan_years": 5}
SIP_DEFAULTS = {"sip_amount": 10_000, "sip_rate": 12.0, "sip_years": 10}

# Simple inline SVG icons (drawn as plain strokes, so they take the CSS colour)
ICONS = {
    "logo": '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="white" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 16 9 11 13 14 20 7"/><polyline points="15 7 20 7 20 12"/></svg>',
    "emi": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/><line x1="7" y1="15" x2="11" y2="15"/></svg>',
    "principal": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10l9-6 9 6"/><line x1="5" y1="10" x2="5" y2="18"/><line x1="10" y1="10" x2="10" y2="18"/><line x1="14" y1="10" x2="14" y2="18"/><line x1="19" y1="10" x2="19" y2="18"/><line x1="3" y1="20" x2="21" y2="20"/></svg>',
    "interest": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="5" x2="5" y2="19"/><circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="17" r="2.5"/></svg>',
    "total": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 7H5a2 2 0 0 1 0-4h13v4"/><path d="M3 5v14a2 2 0 0 0 2 2h15V7"/><circle cx="16" cy="14" r="1.5"/></svg>',
    "growth": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 17 9 11 13 15 21 7"/><polyline points="15 7 21 7 21 13"/></svg>',
    "invest": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9 8h6M9 11h6M13 11c0 3-4 3-4 3l5 4"/></svg>',
    "info": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="11" x2="12" y2="16"/><circle cx="12" cy="8" r="0.6" fill="currentColor"/></svg>',
}

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, .stText, button, input, label {{
    font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}}
.stApp {{ background: #F7FAF9; }}
.block-container {{ padding-top: 2rem; padding-bottom: 1rem; max-width: 1250px; }}
#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {{
    background: #FFFFFF;
    border-right: 1px solid {BORDER};
}}
.brand {{ display: flex; align-items: center; gap: 10px; padding: 4px 0 18px 0; }}
.brand-logo {{
    width: 40px; height: 40px; border-radius: 12px;
    background: linear-gradient(135deg, {PRIMARY}, {PRIMARY_DARK});
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 6px 16px rgba(14,159,110,0.30);
}}
.brand-name {{ font-size: 1.35rem; font-weight: 800; color: {TEXT_DARK}; line-height: 1.1; }}
.brand-tag {{ font-size: 0.75rem; color: {TEXT_MUTED}; }}
.side-note {{
    background: {PRIMARY_LIGHT}; border: 1px solid #C6F0DF; border-radius: 12px;
    padding: 12px 14px; font-size: 0.82rem; color: {PRIMARY_DARK}; line-height: 1.5;
}}

/* ---------- Page header ---------- */
.page-title {{ font-size: 1.9rem; font-weight: 800; color: {TEXT_DARK}; margin: 0; }}
.page-sub {{ color: {TEXT_MUTED}; font-size: 0.98rem; margin: 4px 0 18px 0; }}
.pill {{
    display: inline-block; background: {PRIMARY_LIGHT}; color: {PRIMARY_DARK};
    border: 1px solid #C6F0DF; border-radius: 999px; padding: 3px 12px;
    font-size: 0.75rem; font-weight: 600; margin-bottom: 8px;
}}

/* ---------- Bordered containers (Streamlit cards) ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: #FFFFFF; border-radius: 16px !important;
    border: 1px solid {BORDER} !important;
    box-shadow: 0 1px 3px rgba(15,23,42,0.04);
}}
.card-title {{ font-size: 1.05rem; font-weight: 700; color: {TEXT_DARK}; margin-bottom: 6px; }}

/* ---------- Input rows ---------- */
.input-label {{ font-size: 0.92rem; font-weight: 600; color: {TEXT_DARK}; padding-top: 6px; }}
.input-hint {{ font-size: 0.78rem; color: {TEXT_MUTED}; }}
div[data-testid="stNumberInput"] input {{
    font-weight: 700; color: {PRIMARY_DARK}; background: {PRIMARY_LIGHT};
    text-align: right;
}}

/* ---------- Metric cards ---------- */
.metric-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 14px; margin-bottom: 14px;
}}
.metric-card {{
    background: #FFFFFF; border: 1px solid {BORDER}; border-radius: 16px;
    padding: 16px 18px; transition: transform .15s ease, box-shadow .15s ease;
}}
.metric-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 22px rgba(15,23,42,0.07); }}
.metric-card.wide {{ grid-column: 1 / -1; }}
.metric-card.highlight {{
    background: linear-gradient(135deg, {PRIMARY}, {PRIMARY_DARK}); border: none; color: white;
}}
.metric-icon {{
    width: 36px; height: 36px; border-radius: 10px; display: flex;
    align-items: center; justify-content: center; margin-bottom: 10px;
    background: {PRIMARY_LIGHT}; color: {PRIMARY};
}}
.metric-card.highlight .metric-icon {{ background: rgba(255,255,255,0.18); color: white; }}
.metric-label {{ font-size: 0.8rem; color: {TEXT_MUTED}; font-weight: 500; }}
.metric-card.highlight .metric-label {{ color: rgba(255,255,255,0.85); }}
.metric-value {{ font-size: 1.45rem; font-weight: 800; color: {TEXT_DARK}; margin-top: 2px; word-break: break-word; }}
.metric-card.highlight .metric-value {{ color: white; }}
.metric-sub {{ font-size: 0.75rem; color: {TEXT_MUTED}; margin-top: 2px; }}
.metric-card.highlight .metric-sub {{ color: rgba(255,255,255,0.8); }}

/* ---------- Notice boxes ---------- */
.notice {{
    display: flex; gap: 10px; align-items: flex-start; border-radius: 12px;
    padding: 12px 14px; font-size: 0.85rem; line-height: 1.5; margin: 4px 0 14px 0;
}}
.notice.warn {{ background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; }}
.notice.info {{ background: {PRIMARY_LIGHT}; border: 1px solid #C6F0DF; color: {PRIMARY_DARK}; }}

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button {{
    border-radius: 10px; font-weight: 600; border: 1px solid {PRIMARY};
    color: {PRIMARY}; background: white;
}}
.stDownloadButton > button {{ background: {PRIMARY}; color: white; }}
.stButton > button:hover {{ background: {PRIMARY_LIGHT}; color: {PRIMARY_DARK}; border-color: {PRIMARY_DARK}; }}
.stDownloadButton > button:hover {{ background: {PRIMARY_DARK}; color: white; border-color: {PRIMARY_DARK}; }}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
.stTabs [data-baseweb="tab"] {{ font-weight: 600; }}

/* ---------- Learn section ---------- */
.learn h4 {{ color: {PRIMARY_DARK}; margin-bottom: 4px; }}
.learn p, .learn li {{ color: #334155; font-size: 0.93rem; line-height: 1.65; }}
.formula {{
    background: #0F172A; color: #A7F3D0; border-radius: 12px; padding: 12px 16px;
    font-family: 'JetBrains Mono', Consolas, monospace; font-size: 0.95rem; margin: 8px 0 12px 0;
}}

/* ---------- Footer ---------- */
.footer {{
    margin-top: 36px; padding: 22px 0 8px 0; border-top: 1px solid {BORDER};
    text-align: center; color: {TEXT_MUTED}; font-size: 0.82rem; line-height: 1.7;
}}
.footer b {{ color: {PRIMARY_DARK}; }}

/* ---------- Mobile tweaks ---------- */
@media (max-width: 640px) {{
    .page-title {{ font-size: 1.45rem; }}
    .metric-value {{ font-size: 1.2rem; }}
    .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
}}
</style>
"""


# ---------------------------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def format_inr(amount, decimals=0):
    """
    Format a number in the Indian numbering system with the Rupee sign.
    Indian grouping keeps the last 3 digits together and then groups by 2:
        1234567   -> ₹12,34,567
        100000000 -> ₹10,00,00,000
    """
    amount = round(float(amount), decimals)
    if amount == 0:
        amount = 0.0  # avoids showing "-0"
    sign = "-" if amount < 0 else ""
    text = f"{abs(amount):.{decimals}f}"
    whole, _, fraction = text.partition(".")

    if len(whole) > 3:
        last_three = whole[-3:]
        rest = whole[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        whole = ",".join(groups) + "," + last_three

    result = f"{sign}₹{whole}"
    if fraction:
        result += "." + fraction
    return result


def format_inr_short(amount):
    """Short form used on chart axes: ₹1.25 Cr, ₹12.5 L, ₹45K."""
    amount = float(amount)
    if abs(amount) >= 1e7:
        return f"₹{amount / 1e7:.2f} Cr".replace(".00 ", " ")
    if abs(amount) >= 1e5:
        return f"₹{amount / 1e5:.2f} L".replace(".00 ", " ")
    if abs(amount) >= 1e3:
        return f"₹{amount / 1e3:.1f}K".replace(".0K", "K")
    return f"₹{amount:.0f}"


def build_csv_report(title, summary, table):
    """
    Build a CSV report: a title, a summary block (label, value) and then the
    full data table. Returns bytes ready for st.download_button.
    Numbers are written as plain numbers so they can be used in Excel.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([title])
    writer.writerow(["Generated on", date.today().strftime("%d %b %Y")])
    writer.writerow([])
    writer.writerow(["SUMMARY"])
    for label, value in summary.items():
        writer.writerow([label, value])
    writer.writerow([])
    writer.writerow(["DETAILED TABLE"])
    table.round(2).to_csv(buffer, index=False)
    writer = csv.writer(buffer)
    writer.writerow([])
    writer.writerow(["Disclaimer", "For educational use only. Not financial advice."])
    # utf-8-sig adds a BOM so Excel opens the file with the right encoding
    return buffer.getvalue().encode("utf-8-sig")


# ---------------------------------------------------------------------------
# 3. CALCULATION LOGIC
# ---------------------------------------------------------------------------

def calculate_emi(principal, annual_rate, years):
    """
    Calculate the monthly EMI for a reducing-balance loan.

        EMI = P × r × (1 + r)^n / ((1 + r)^n − 1)

        P = loan amount, r = monthly interest rate (annual % / 12 / 100),
        n = number of monthly instalments (years × 12)

    Edge case: when the interest rate is 0, the formula divides by zero,
    so the EMI is simply the principal split equally: P / n.
    """
    months = int(years * 12)
    if principal <= 0 or months <= 0:
        raise ValueError("Loan amount and tenure must be greater than zero.")
    if annual_rate < 0:
        raise ValueError("Interest rate cannot be negative.")

    monthly_rate = annual_rate / 12 / 100

    if monthly_rate == 0:
        emi = principal / months
    else:
        growth = (1 + monthly_rate) ** months
        emi = principal * monthly_rate * growth / (growth - 1)

    total_payment = emi * months
    total_interest = total_payment - principal

    return {
        "emi": emi,
        "months": months,
        "principal": principal,
        "total_interest": total_interest,
        "total_payment": total_payment,
    }


def build_amortization_schedule(principal, annual_rate, years):
    """
    Month-by-month repayment schedule.
    Each month: interest = opening balance × monthly rate,
                principal part = EMI − interest,
                closing balance = opening balance − principal part.
    """
    result = calculate_emi(principal, annual_rate, years)
    emi, months = result["emi"], result["months"]
    monthly_rate = annual_rate / 12 / 100

    # Payment months start from the month after today
    today = date.today()
    first_month = date(today.year + (today.month // 12), today.month % 12 + 1, 1)
    payment_dates = pd.date_range(start=first_month, periods=months, freq="MS")

    rows = []
    balance = float(principal)
    for month in range(1, months + 1):
        opening = balance
        interest = opening * monthly_rate
        principal_part = emi - interest
        payment = emi

        # Last instalment: clear any tiny rounding left-over
        if month == months:
            principal_part = opening
            payment = principal_part + interest

        balance = max(opening - principal_part, 0.0)
        rows.append({
            "EMI No.": month,
            "Month": payment_dates[month - 1].strftime("%b %Y"),
            "Loan Year": (month - 1) // 12 + 1,
            "Opening Balance": opening,
            "EMI": payment,
            "Principal Paid": principal_part,
            "Interest Paid": interest,
            "Closing Balance": balance,
        })

    return pd.DataFrame(rows)


def yearly_loan_summary(schedule):
    """Group the monthly schedule into one row per loan year."""
    yearly = schedule.groupby("Loan Year").agg(
        {"Principal Paid": "sum", "Interest Paid": "sum", "EMI": "sum", "Closing Balance": "last"}
    ).reset_index()
    yearly = yearly.rename(columns={"EMI": "Total Paid"})
    return yearly


def calculate_sip(monthly_investment, annual_return, years):
    """
    Future value of a monthly SIP (investment made at the start of each month).

        M = P × [((1 + i)^n − 1) / i] × (1 + i)

        P = monthly investment, i = monthly return (annual % / 12 / 100),
        n = number of monthly instalments (years × 12)

    Edge case: at 0% return the money does not grow, so M = P × n.
    """
    months = int(years * 12)
    if monthly_investment <= 0 or months <= 0:
        raise ValueError("Investment amount and duration must be greater than zero.")
    if annual_return < 0:
        raise ValueError("Expected return cannot be negative.")

    monthly_rate = annual_return / 12 / 100
    invested = monthly_investment * months

    if monthly_rate == 0:
        maturity = invested
    else:
        maturity = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)

    return {
        "invested": invested,
        "returns": maturity - invested,
        "maturity": maturity,
        "months": months,
    }


def sip_yearly_growth(monthly_investment, annual_return, years):
    """
    Year-wise SIP value using NumPy to evaluate the SIP formula for every
    year in one vectorised step (no Python loop needed).
    """
    year_numbers = np.arange(1, int(years) + 1)
    months = year_numbers * 12
    monthly_rate = annual_return / 12 / 100

    invested = monthly_investment * months
    if monthly_rate == 0:
        value = invested.astype(float)
    else:
        value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)

    return pd.DataFrame({
        "Year": year_numbers,
        "Amount Invested": invested,
        "Estimated Returns": value - invested,
        "Estimated Value": value,
    })


# ---------------------------------------------------------------------------
# 4. CHART BUILDERS (Plotly)
# ---------------------------------------------------------------------------

def _base_layout(fig, height=340):
    """Shared clean styling for every chart."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(family="Inter, Segoe UI, sans-serif", color=TEXT_DARK, size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hoverlabel=dict(bgcolor="white", font_size=13),
    )
    return fig


def _inr_y_axis(fig, max_value):
    """Plotly cannot group digits the Indian way, so we write our own tick labels."""
    if max_value <= 0:
        max_value = 1
    ticks = np.linspace(0, max_value, 6)
    fig.update_yaxes(
        tickvals=ticks,
        ticktext=[format_inr_short(t) for t in ticks],
        gridcolor="#EEF2F1",
        zeroline=False,
    )
    fig.update_xaxes(showgrid=False)
    return fig


def donut_chart(labels, values, center_title, center_value):
    """Donut (pie) chart with the total written in the middle."""
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.68,
        sort=False,
        marker=dict(colors=[PRIMARY, SECONDARY], line=dict(color="white", width=3)),
        textinfo="percent",
        textfont=dict(size=13, color=[ "white", PRIMARY_DARK]),
        customdata=[format_inr(v) for v in values],
        hovertemplate="<b>%{label}</b><br>%{customdata}<br>%{percent}<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<span style='font-size:12px;color:{TEXT_MUTED}'>{center_title}</span><br>"
             f"<b style='font-size:17px'>{center_value}</b>",
        showarrow=False, x=0.5, y=0.5,
    )
    _base_layout(fig, height=320)
    fig.update_layout(legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center", yanchor="top"))
    return fig


def loan_balance_chart(schedule):
    """Area chart of the outstanding loan balance after every EMI."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=schedule["EMI No."],
        y=schedule["Closing Balance"],
        mode="lines",
        name="Outstanding balance",
        line=dict(color=PRIMARY, width=3),
        fill="tozeroy",
        fillcolor="rgba(14,159,110,0.12)",
        customdata=np.stack([schedule["Month"], schedule["Closing Balance"].map(format_inr)], axis=-1),
        hovertemplate="EMI %{x} (%{customdata[0]})<br>Balance: <b>%{customdata[1]}</b><extra></extra>",
    ))
    cumulative_interest = schedule["Interest Paid"].cumsum()
    fig.add_trace(go.Scatter(
        x=schedule["EMI No."],
        y=cumulative_interest,
        mode="lines",
        name="Interest paid so far",
        line=dict(color="#F59E0B", width=2, dash="dot"),
        customdata=cumulative_interest.map(format_inr),
        hovertemplate="EMI %{x}<br>Interest paid: <b>%{customdata}</b><extra></extra>",
    ))
    _base_layout(fig, height=360)
    _inr_y_axis(fig, schedule["Opening Balance"].max())
    fig.update_xaxes(title_text="EMI number (month)")
    return fig


def loan_yearly_bar_chart(yearly):
    """Stacked bars: principal vs interest paid in each loan year."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=yearly["Loan Year"], y=yearly["Principal Paid"], name="Principal",
        marker_color=PRIMARY,
        customdata=yearly["Principal Paid"].map(format_inr),
        hovertemplate="Year %{x}<br>Principal: <b>%{customdata}</b><extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=yearly["Loan Year"], y=yearly["Interest Paid"], name="Interest",
        marker_color=SECONDARY,
        customdata=yearly["Interest Paid"].map(format_inr),
        hovertemplate="Year %{x}<br>Interest: <b>%{customdata}</b><extra></extra>",
    ))
    fig.update_layout(barmode="stack", bargap=0.35)
    _base_layout(fig, height=340)
    _inr_y_axis(fig, (yearly["Principal Paid"] + yearly["Interest Paid"]).max())
    fig.update_xaxes(title_text="Loan year", dtick=1 if len(yearly) <= 15 else None)
    return fig


def sip_growth_chart(growth):
    """Line chart: amount invested vs estimated value, year by year."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=growth["Year"], y=growth["Estimated Value"], name="Estimated value",
        mode="lines+markers", line=dict(color=PRIMARY, width=3), marker=dict(size=7),
        fill="tozeroy", fillcolor="rgba(14,159,110,0.10)",
        customdata=growth["Estimated Value"].map(format_inr),
        hovertemplate="Year %{x}<br>Value: <b>%{customdata}</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=growth["Year"], y=growth["Amount Invested"], name="Amount invested",
        mode="lines+markers", line=dict(color="#475569", width=2, dash="dash"), marker=dict(size=6),
        customdata=growth["Amount Invested"].map(format_inr),
        hovertemplate="Year %{x}<br>Invested: <b>%{customdata}</b><extra></extra>",
    ))
    _base_layout(fig, height=380)
    _inr_y_axis(fig, growth["Estimated Value"].max())
    fig.update_xaxes(title_text="Year", dtick=1 if len(growth) <= 15 else None)
    return fig


# ---------------------------------------------------------------------------
# 5. UI COMPONENTS
# ---------------------------------------------------------------------------

def _ensure_state(key, default):
    """
    Each input has one 'master' value (st.session_state[key]) and two widgets
    (a number box and a slider). Streamlit deletes widget state when a page is
    not shown, so we re-create the widget values from the master value.
    """
    if key not in st.session_state:
        st.session_state[key] = default
    for suffix in ("num", "sld"):
        widget_key = f"{key}_{suffix}"
        if widget_key not in st.session_state:
            st.session_state[widget_key] = st.session_state[key]


def _sync(key, source):
    """Keep the number box and the slider showing the same value."""
    value = st.session_state[f"{key}_{source}"]
    other = "sld" if source == "num" else "num"
    st.session_state[key] = value
    st.session_state[f"{key}_{other}"] = value


def reset_inputs(defaults):
    """Callback for the Reset button: restore every input to its default."""
    for key, value in defaults.items():
        st.session_state[key] = value
        st.session_state[f"{key}_num"] = value
        st.session_state[f"{key}_sld"] = value


def input_with_slider(label, key, default, min_value, max_value, step, number_format, hint_fn):
    """
    One input row: label + exact number box on top, slider underneath.
    Both widgets are linked, so changing either updates the other.
    """
    _ensure_state(key, default)
    left, right = st.columns([1.35, 1])
    with left:
        hint = hint_fn(st.session_state[key])
        st.markdown(
            f'<div class="input-label">{label}</div><div class="input-hint">{hint}</div>',
            unsafe_allow_html=True,
        )
    with right:
        st.number_input(
            label, min_value=min_value, max_value=max_value, step=step,
            format=number_format, key=f"{key}_num",
            on_change=_sync, args=(key, "num"), label_visibility="collapsed",
        )
    st.slider(
        label, min_value=min_value, max_value=max_value, step=step,
        key=f"{key}_sld", on_change=_sync, args=(key, "sld"),
        label_visibility="collapsed", format=number_format,
    )
    return st.session_state[key]


def metric_cards(cards, wide_first=False):
    """
    Render a responsive grid of metric cards.
    cards = list of (icon_key, label, value, sub_text, highlight)
    wide_first=True makes the first card span the whole row (used when
    there is an odd number of cards, so the grid has no empty gap).
    HTML is joined without indentation because Markdown would treat
    indented lines as a code block.
    """
    parts = ['<div class="metric-grid">']
    for index, (icon, label, value, sub, highlight) in enumerate(cards):
        css_class = "metric-card highlight" if highlight else "metric-card"
        if wide_first and index == 0:
            css_class += " wide"
        parts.append(
            f'<div class="{css_class}">'
            f'<div class="metric-icon">{ICONS[icon]}</div>'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div>'
            f'<div class="metric-sub">{sub}</div>'
            f'</div>'
        )
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def notice(text, kind="info"):
    st.markdown(
        f'<div class="notice {kind}"><div>{ICONS["info"]}</div><div>{text}</div></div>',
        unsafe_allow_html=True,
    )


def page_header(pill, title, subtitle):
    st.markdown(
        f'<span class="pill">{pill}</span>'
        f'<h1 class="page-title">{title}</h1>'
        f'<p class="page-sub">{subtitle}</p>',
        unsafe_allow_html=True,
    )


def tenure_text(years):
    return f"{years} year{'s' if years != 1 else ''} · {years * 12} months"


# ---------------------------------------------------------------------------
# 6. PAGES
# ---------------------------------------------------------------------------

def emi_page():
    page_header(
        "LOAN PLANNING",
        "Loan EMI Calculator",
        "Find your monthly instalment, total interest and full repayment schedule for a home, car or personal loan.",
    )

    input_col, result_col = st.columns([5, 7], gap="large")

    # ---------------- Inputs ----------------
    with input_col:
        with st.container(border=True):
            st.markdown('<div class="card-title">Loan details</div>', unsafe_allow_html=True)
            principal = input_with_slider(
                "Loan amount (₹)", "loan_amount", EMI_DEFAULTS["loan_amount"],
                10_000, 100_000_000, 10_000, "%d",
                lambda v: f"{format_inr(v)} · {format_inr_short(v)}",
            )
            rate = input_with_slider(
                "Interest rate (% p.a.)", "loan_rate", EMI_DEFAULTS["loan_rate"],
                0.0, 30.0, 0.1, "%.1f",
                lambda v: f"{v:.2f}% per year · {v / 12:.3f}% per month",
            )
            years = input_with_slider(
                "Loan tenure (years)", "loan_years", EMI_DEFAULTS["loan_years"],
                1, 30, 1, "%d", tenure_text,
            )
            st.button(
                "↺  Reset calculator", on_click=reset_inputs, args=(EMI_DEFAULTS,),
                width="stretch", key="reset_emi",
            )

    # ---------------- Validation ----------------
    errors = []
    if principal <= 0:
        errors.append("Loan amount must be greater than zero.")
    if rate < 0:
        errors.append("Interest rate cannot be negative.")
    if years <= 0:
        errors.append("Loan tenure must be at least 1 year.")
    if errors:
        with result_col:
            for message in errors:
                st.error(message)
        return

    # ---------------- Calculations ----------------
    result = calculate_emi(principal, rate, years)
    schedule = build_amortization_schedule(principal, rate, years)
    yearly = yearly_loan_summary(schedule)

    # ---------------- Results ----------------
    with result_col:
        if rate == 0:
            notice("At <b>0% interest</b> there is no interest cost: the EMI is simply the loan amount divided by the number of months.")
        elif rate > 20:
            notice(f"An interest rate of <b>{rate:.1f}%</b> is unusually high. Please double-check the rate offered by your lender.", "warn")

        metric_cards([
            ("emi", "Monthly EMI", format_inr(result["emi"]), f"for {result['months']} months", True),
            ("principal", "Principal amount", format_inr(principal), format_inr_short(principal), False),
            ("interest", "Total interest", format_inr(result["total_interest"]),
             f"{result['total_interest'] / principal * 100:.1f}% of principal", False),
            ("total", "Total repayment", format_inr(result["total_payment"]), "principal + interest", False),
        ])

        with st.container(border=True):
            st.markdown('<div class="card-title">Principal vs interest</div>', unsafe_allow_html=True)
            st.plotly_chart(
                donut_chart(["Principal amount", "Total interest"],
                            [principal, result["total_interest"]],
                            "Total payable", format_inr_short(result["total_payment"])),
                width="stretch", config={"displayModeBar": False},
            )

    # ---------------- Detailed tabs ----------------
    st.write("")
    tab_balance, tab_yearly, tab_schedule, tab_learn = st.tabs(
        ["📉  Loan balance", "📊  Year-wise breakdown", "📋  Repayment schedule", "📘  Learn about EMI"]
    )

    with tab_balance:
        with st.container(border=True):
            st.markdown('<div class="card-title">Outstanding loan balance over time</div>', unsafe_allow_html=True)
            st.plotly_chart(loan_balance_chart(schedule), width="stretch", config={"displayModeBar": False})
            half_point = schedule[schedule["Closing Balance"] <= principal / 2]
            if not half_point.empty:
                row = half_point.iloc[0]
                st.caption(f"You will have repaid half of the loan by EMI no. {int(row['EMI No.'])} ({row['Month']}).")

    with tab_yearly:
        with st.container(border=True):
            st.markdown('<div class="card-title">Principal and interest paid each year</div>', unsafe_allow_html=True)
            st.plotly_chart(loan_yearly_bar_chart(yearly), width="stretch", config={"displayModeBar": False})
            yearly_display = yearly.copy()
            for column in ["Principal Paid", "Interest Paid", "Total Paid", "Closing Balance"]:
                yearly_display[column] = yearly_display[column].map(format_inr)
            st.dataframe(yearly_display, hide_index=True, width="stretch")

    with tab_schedule:
        with st.container(border=True):
            st.markdown('<div class="card-title">Monthly repayment schedule</div>', unsafe_allow_html=True)
            st.caption("Each EMI first pays the interest for that month; the rest reduces your loan balance.")
            schedule_display = schedule.copy()
            for column in ["Opening Balance", "EMI", "Principal Paid", "Interest Paid", "Closing Balance"]:
                schedule_display[column] = schedule_display[column].map(format_inr)
            st.dataframe(schedule_display, hide_index=True, width="stretch", height=420)

            summary = {
                "Loan amount (INR)": round(principal, 2),
                "Annual interest rate (%)": rate,
                "Tenure (years)": years,
                "Number of EMIs": result["months"],
                "Monthly EMI (INR)": round(result["emi"], 2),
                "Total interest (INR)": round(result["total_interest"], 2),
                "Total repayment (INR)": round(result["total_payment"], 2),
            }
            st.download_button(
                "⬇  Download report (CSV)",
                data=build_csv_report("FinWise – Loan EMI Report", summary, schedule),
                file_name=f"finwise_emi_report_{date.today():%Y%m%d}.csv",
                mime="text/csv",
                width="stretch",
                key="download_emi",
            )

    with tab_learn:
        st.markdown(
            f"""<div class="learn">
<h4>What is an EMI?</h4>
<p>An <b>Equated Monthly Instalment (EMI)</b> is the fixed amount you pay your lender every month until the loan is fully repaid. Each EMI has two parts: <b>interest</b> on the balance still outstanding, and <b>principal</b>, which reduces that balance.</p>
<h4>The formula</h4>
<div class="formula">EMI = P × r × (1 + r)<sup>n</sup> ÷ [(1 + r)<sup>n</sup> − 1]</div>
<p><b>P</b> = loan amount &nbsp;·&nbsp; <b>r</b> = monthly interest rate (annual rate ÷ 12 ÷ 100) &nbsp;·&nbsp; <b>n</b> = number of months. When the rate is 0%, EMI = P ÷ n.</p>
<h4>Useful tips</h4>
<ul>
<li><b>Interest is front-loaded.</b> In the early years most of the EMI goes to interest, so prepayments made early save the most money.</li>
<li><b>Longer tenure = lower EMI but more interest.</b> Compare the total interest, not only the monthly EMI.</li>
<li><b>Keep EMIs affordable.</b> A common rule of thumb is to keep all EMIs together below about 40% of your monthly take-home income.</li>
<li><b>Small rate differences matter.</b> On a long home loan, even 0.5% lower interest can save lakhs of rupees.</li>
</ul>
</div>""",
            unsafe_allow_html=True,
        )


def sip_page():
    page_header(
        "WEALTH BUILDING",
        "SIP Calculator",
        "Estimate how a fixed monthly investment could grow over time through the power of compounding.",
    )

    notice(
        "<b>Returns are estimates, not guarantees.</b> This calculator assumes a constant annual return. "
        "Real mutual fund returns change with the market and can be negative. "
        "Mutual fund investments are subject to market risks; read all scheme documents carefully.",
        "warn",
    )

    input_col, result_col = st.columns([5, 7], gap="large")

    # ---------------- Inputs ----------------
    with input_col:
        with st.container(border=True):
            st.markdown('<div class="card-title">Investment details</div>', unsafe_allow_html=True)
            monthly = input_with_slider(
                "Monthly investment (₹)", "sip_amount", SIP_DEFAULTS["sip_amount"],
                100, 1_000_000, 100, "%d",
                lambda v: f"{format_inr(v)} every month",
            )
            rate = input_with_slider(
                "Expected return (% p.a.)", "sip_rate", SIP_DEFAULTS["sip_rate"],
                0.0, 30.0, 0.1, "%.1f",
                lambda v: f"{v:.2f}% per year (assumed)",
            )
            years = input_with_slider(
                "Time period (years)", "sip_years", SIP_DEFAULTS["sip_years"],
                1, 40, 1, "%d", tenure_text,
            )
            st.button(
                "↺  Reset calculator", on_click=reset_inputs, args=(SIP_DEFAULTS,),
                width="stretch", key="reset_sip",
            )

    # ---------------- Validation ----------------
    errors = []
    if monthly <= 0:
        errors.append("Monthly investment must be greater than zero.")
    if rate < 0:
        errors.append("Expected return cannot be negative.")
    if years <= 0:
        errors.append("Time period must be at least 1 year.")
    if errors:
        with result_col:
            for message in errors:
                st.error(message)
        return

    # ---------------- Calculations ----------------
    result = calculate_sip(monthly, rate, years)
    growth = sip_yearly_growth(monthly, rate, years)
    multiple = result["maturity"] / result["invested"]

    # ---------------- Results ----------------
    with result_col:
        if rate == 0:
            notice("At <b>0% return</b> your money does not grow: the maturity value equals the amount invested.")
        elif rate > 15:
            notice(f"<b>{rate:.1f}%</b> a year is an optimistic assumption for long periods. Try a lower rate as well to see a cautious scenario.", "warn")

        metric_cards([
            ("growth", "Estimated maturity value", format_inr(result["maturity"]), f"{multiple:.2f}× your investment", True),
            ("invest", "Total invested", format_inr(result["invested"]), f"{result['months']} monthly instalments", False),
            ("interest", "Estimated returns", format_inr(result["returns"]), "wealth gained (estimated)", False),
        ], wide_first=True)

        with st.container(border=True):
            st.markdown('<div class="card-title">Invested amount vs estimated returns</div>', unsafe_allow_html=True)
            st.plotly_chart(
                donut_chart(["Invested amount", "Estimated returns"],
                            [result["invested"], result["returns"]],
                            "Maturity value", format_inr_short(result["maturity"])),
                width="stretch", config={"displayModeBar": False},
            )

    # ---------------- Detailed tabs ----------------
    st.write("")
    tab_growth, tab_table, tab_learn = st.tabs(
        ["📈  Wealth growth", "📋  Year-wise table", "📘  Learn about SIP"]
    )

    with tab_growth:
        with st.container(border=True):
            st.markdown('<div class="card-title">Year-wise wealth growth</div>', unsafe_allow_html=True)
            st.plotly_chart(sip_growth_chart(growth), width="stretch", config={"displayModeBar": False})
            st.caption("The gap between the two lines is the estimated return earned through compounding. It widens in later years.")

    with tab_table:
        with st.container(border=True):
            st.markdown('<div class="card-title">Year-wise investment summary</div>', unsafe_allow_html=True)
            growth_display = growth.copy()
            for column in ["Amount Invested", "Estimated Returns", "Estimated Value"]:
                growth_display[column] = growth_display[column].map(format_inr)
            st.dataframe(growth_display, hide_index=True, width="stretch")

            summary = {
                "Monthly investment (INR)": monthly,
                "Expected annual return (%)": rate,
                "Duration (years)": years,
                "Total invested (INR)": round(result["invested"], 2),
                "Estimated returns (INR)": round(result["returns"], 2),
                "Estimated maturity value (INR)": round(result["maturity"], 2),
                "Note": "Estimated values only - returns are not guaranteed",
            }
            st.download_button(
                "⬇  Download report (CSV)",
                data=build_csv_report("FinWise – SIP Report", summary, growth),
                file_name=f"finwise_sip_report_{date.today():%Y%m%d}.csv",
                mime="text/csv",
                width="stretch",
                key="download_sip",
            )

    with tab_learn:
        st.markdown(
            """<div class="learn">
<h4>What is a SIP?</h4>
<p>A <b>Systematic Investment Plan (SIP)</b> lets you invest a fixed amount in a mutual fund at regular intervals, usually every month. It builds a saving habit and removes the need to time the market.</p>
<h4>The formula</h4>
<div class="formula">M = P × [((1 + i)<sup>n</sup> − 1) ÷ i] × (1 + i)</div>
<p><b>M</b> = maturity value &nbsp;·&nbsp; <b>P</b> = monthly investment &nbsp;·&nbsp; <b>i</b> = monthly return (annual % ÷ 12 ÷ 100) &nbsp;·&nbsp; <b>n</b> = number of months. The last factor (1 + i) is there because each instalment is invested at the <i>start</i> of the month. At 0% return, M = P × n.</p>
<h4>Why SIPs work</h4>
<ul>
<li><b>Compounding.</b> Returns earn further returns, so growth speeds up the longer you stay invested.</li>
<li><b>Rupee cost averaging.</b> A fixed amount buys more units when prices are low and fewer when prices are high.</li>
<li><b>Discipline.</b> Automatic monthly investing makes it easier to stay consistent.</li>
<li><b>Start early.</b> Time in the market usually matters more than the amount: compare 10 years with 20 years on the chart above.</li>
</ul>
<p><b>Remember:</b> the figures shown are estimates based on a constant return. Actual returns are not guaranteed.</p>
</div>""",
            unsafe_allow_html=True,
        )


def about_page():
    page_header(
        "ABOUT",
        "About FinWise",
        "A smart, simple and transparent way to plan loans and investments.",
    )
    col1, col2 = st.columns(2, gap="large")
    with col1:
        with st.container(border=True):
            st.markdown('<div class="card-title">What you can do</div>', unsafe_allow_html=True)
            st.markdown(
                "- **Loan EMI Calculator** – monthly EMI, total interest, repayment schedule, balance chart\n"
                "- **SIP Calculator** – total invested, estimated returns, maturity value, growth chart\n"
                "- **Real-time results** – every change updates instantly\n"
                "- **CSV reports** – download your calculations for Excel\n"
                "- **Indian formatting** – amounts shown as ₹12,34,567"
            )
    with col2:
        with st.container(border=True):
            st.markdown('<div class="card-title">Built with</div>', unsafe_allow_html=True)
            st.markdown(
                "- **Python** – calculation logic\n"
                "- **Streamlit** – web interface\n"
                "- **Plotly** – interactive charts\n"
                "- **NumPy & pandas** – vectorised maths and tables"
            )
    notice(
        "FinWise is an educational project. Results are for illustration only and are not financial advice. "
        "Actual loan EMIs depend on your lender's terms, and investment returns are never guaranteed.",
        "info",
    )


# ---------------------------------------------------------------------------
# 7. MAIN: SIDEBAR NAVIGATION AND FOOTER
# ---------------------------------------------------------------------------

def sidebar():
    with st.sidebar:
        st.markdown(
            f'<div class="brand"><div class="brand-logo">{ICONS["logo"]}</div>'
            f'<div><div class="brand-name">FinWise</div>'
            f'<div class="brand-tag">Smart Financial Calculator</div></div></div>',
            unsafe_allow_html=True,
        )
        page = st.radio(
            "Navigation",
            ["🏦  Loan EMI Calculator", "📈  SIP Calculator", "ℹ️  About FinWise"],
            key="page",
        )
        st.markdown("---")
        st.markdown(
            '<div class="side-note"><b>Quick tip</b><br>'
            "Type an exact value in the box or drag the slider. Results update instantly.</div>",
            unsafe_allow_html=True,
        )
    return page


def footer():
    st.markdown(
        f'<div class="footer"><b>FinWise</b> – Smart Financial Calculator · Built with Python, Streamlit & Plotly<br>'
        f"For educational purposes only. Not financial advice. SIP returns are estimates and are not guaranteed.<br>"
        f"© {date.today().year} FinWise. All rights reserved.</div>",
        unsafe_allow_html=True,
    )


def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    page = sidebar()

    if "EMI" in page:
        emi_page()
    elif "SIP" in page:
        sip_page()
    else:
        about_page()

    footer()


if __name__ == "__main__":
    main()
