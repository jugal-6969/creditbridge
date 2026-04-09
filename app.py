import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import time
import requests

st.set_page_config(page_title="CreditBridge", page_icon="💳",
                   layout="centered", initial_sidebar_state="collapsed")

BG      = "#07090f"
CARD    = "#0d1117"
BORDER  = "#1c2333"
ACCENT  = "#00c9a7"
ACCENT2 = "#6366f1"
TEXT    = "#e2e8f0"
MUTED   = "#64748b"
WARN    = "#f59e0b"
DANGER  = "#ef4444"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif;}}
.main .block-container{{max-width:440px;padding:1rem 1rem 3rem;margin:0 auto;}}
.stApp{{background:{BG};}}
#MainMenu,footer,header,.stDeployButton{{visibility:hidden;display:none;}}
.cb-card{{background:{CARD};border:1px solid {BORDER};border-radius:16px;padding:18px 20px;margin-bottom:14px;}}
.cb-accent{{border-left:3px solid {ACCENT};}}
.brand-title{{font-size:26px;font-weight:700;color:{TEXT};letter-spacing:-0.5px;}}
.brand-title span{{color:{ACCENT};}}
.brand-sub{{font-size:13px;color:{MUTED};margin-top:4px;}}
.sec-head{{font-size:11px;font-weight:600;color:{MUTED};letter-spacing:0.8px;text-transform:uppercase;margin:18px 0 10px;}}
.score-big{{font-size:68px;font-weight:700;line-height:1;text-align:center;}}
.pill{{display:inline-block;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:600;}}
.pill-low{{background:rgba(0,201,167,0.12);color:{ACCENT};}}
.pill-mod{{background:rgba(245,158,11,0.12);color:{WARN};}}
.pill-high{{background:rgba(239,68,68,0.12);color:{DANGER};}}
.pill-info{{background:rgba(99,102,241,0.12);color:{ACCENT2};}}
.row{{display:flex;justify-content:space-between;align-items:center;padding:11px 0;border-bottom:1px solid {BORDER};}}
.row-label{{font-size:13px;color:{MUTED};}}
.row-val{{font-size:13px;font-weight:600;color:{TEXT};}}
.bank-row{{display:flex;align-items:center;gap:12px;padding:13px 16px;border-radius:12px;border:1px solid {BORDER};background:{CARD};margin-bottom:10px;}}
.bank-ok{{border-color:{ACCENT};background:rgba(0,201,167,0.04);}}
.chat-user{{background:{ACCENT};color:#000;padding:10px 14px;border-radius:14px 14px 4px 14px;font-size:14px;margin:6px 0;margin-left:18%;line-height:1.6;}}
.chat-bot{{background:#131924;color:#a8bbd4;padding:10px 14px;border-radius:14px 14px 14px 4px;font-size:14px;margin:6px 0;margin-right:18%;line-height:1.6;}}
.stButton>button{{background:{ACCENT}!important;color:#000!important;border:none!important;border-radius:12px!important;padding:12px 24px!important;font-size:14px!important;font-weight:700!important;width:100%!important;}}
.stButton>button:hover{{opacity:0.88!important;}}
.stTextInput input,.stSelectbox select{{background:#131924!important;border:1px solid {BORDER}!important;border-radius:12px!important;color:{TEXT}!important;font-size:14px!important;}}
div[data-testid="stRadio"] label{{color:{MUTED}!important;font-size:13px;}}
.prog-bg{{height:6px;background:{BORDER};border-radius:3px;overflow:hidden;margin-top:6px;}}
.prog-fill{{height:100%;border-radius:3px;}}
.fi{{display:flex;align-items:center;gap:12px;padding:12px 16px;border-radius:12px;border:1px solid {BORDER};margin-bottom:8px;}}
.fi-done{{border-color:{ACCENT};background:rgba(0,201,167,0.05);}}
</style>
""", unsafe_allow_html=True)

PROFILES = {
    "Arjun Mehta - arrived 8 months ago": dict(
        name="Arjun Mehta", nat="Indian", visa="Employment",
        employer="Keeta Technologies LLC", salary=12500,
        rent=4, sal=4, telco=3, util=4, ejari=0.7,
        telco_mo=8, exp=0.52, wps=True, months_in_uae=8),
    "Mohamed Hassan - arrived 5 months ago": dict(
        name="Mohamed Hassan", nat="Egyptian", visa="Employment",
        employer="ENOC Group", salary=8200,
        rent=3, sal=3, telco=2, util=3, ejari=0.4,
        telco_mo=5, exp=0.68, wps=True, months_in_uae=5),
    "Priya Nair - arrived 14 months ago": dict(
        name="Priya Nair", nat="Indian", visa="Freelance",
        employer="Self-employed", salary=18000,
        rent=4, sal=3, telco=4, util=4, ejari=1.2,
        telco_mo=14, exp=0.41, wps=False, months_in_uae=14),
}

BANKS = [
    dict(name="Emirates NBD", min=650, rate="3.49%", product="Personal Loan", max="AED 500,000"),
    dict(name="ADCB",         min=600, rate="3.75%", product="Personal Loan", max="AED 300,000"),
    dict(name="FAB",          min=700, rate="2.99%", product="Home Mortgage", max="AED 2,000,000"),
    dict(name="Mashreq",      min=580, rate="4.25%", product="Personal Loan", max="AED 200,000"),
    dict(name="DIB",          min=620, rate="3.99%", product="Auto Finance",  max="AED 350,000"),
]

LOANS = [
    dict(a=500, t=1, f=3), dict(a=1000, t=2, f=3),
    dict(a=1500, t=3, f=4), dict(a=2000, t=3, f=4), dict(a=3000, t=6, f=5),
]

COUNTRIES = [
    dict(flag="🇬🇧", name="United Kingdom", bureau="Experian UK",    live=True),
    dict(flag="🇨🇦", name="Canada",         bureau="Equifax Canada", live=True),
    dict(flag="🇦🇺", name="Australia",       bureau="Illion",         live=True),
    dict(flag="🇮🇳", name="India",           bureau="CIBIL",          live=False),
    dict(flag="🇺🇸", name="United States",   bureau="TransUnion",     live=False),
]

SOURCES = [
    ("UAE Pass",                 "Identity verified"),
    ("WPS / Ministry of Labour", "Salary and employment"),
    ("DEWA",                     "Utility payment history"),
    ("Ejari / RERA",             "Rental records"),
    ("e& (Etisalat)",            "Telecom behaviour"),
    ("AECB",                     "Thin-file check"),
]

WALLET_TXN = [
    dict(desc="Salary Credit",  merchant="Keeta Technologies LLC",       amount=+12500, date="Apr 1, 2026", cat="Income"),
    dict(desc="DEWA Bill",       merchant="Dubai Electricity & Water",     amount=-320,   date="Apr 3, 2026", cat="Utilities"),
    dict(desc="Carrefour",       merchant="Carrefour Mall of Emirates",    amount=-287,   date="Apr 5, 2026", cat="Food"),
    dict(desc="Ejari Rent",      merchant="Real Estate Regulatory Agency", amount=-3800,  date="Apr 7, 2026", cat="Housing"),
    dict(desc="Noon Delivery",   merchant="Noon.com",                      amount=-145,   date="Apr 8, 2026", cat="Shopping"),
    dict(desc="Uber",            merchant="Uber Technologies",             amount=-34,    date="Apr 8, 2026", cat="Transport"),
    dict(desc="du Telecom",      merchant="du Postpaid Plan",              amount=-199,   date="Apr 9, 2026", cat="Utilities"),
]

SPENDING_DATA = [
    dict(name="Housing",   value=3800, color="#00c9a7"),
    dict(name="Food",      value=287,  color="#6366f1"),
    dict(name="Utilities", value=519,  color="#a855f7"),
    dict(name="Shopping",  value=145,  color="#f59e0b"),
    dict(name="Transport", value=34,   color="#f43f5e"),
]

@st.cache_resource
def train_model():
    np.random.seed(42)
    n = 1000
    df = pd.DataFrame({
        "rent":  np.random.choice([1,2,3,4], n, p=[0.05,0.15,0.35,0.45]),
        "sal":   np.random.choice([1,2,3,4], n, p=[0.08,0.17,0.30,0.45]),
        "ejari": np.random.choice([1,2,3,4], n, p=[0.20,0.30,0.30,0.20]),
        "ir":    np.random.choice([1,2,3,4], n, p=[0.10,0.30,0.40,0.20]),
        "telco": np.random.choice([1,2,3,4], n, p=[0.10,0.20,0.35,0.35]),
        "tt":    np.random.choice([1,2,3,4], n, p=[0.15,0.25,0.35,0.25]),
        "util":  np.random.choice([1,2,3,4], n, p=[0.08,0.17,0.35,0.40]),
    })
    raw = (df.rent*0.28 + df.sal*0.22 + df.ejari*0.12 +
           df.ir*0.15 + df.telco*0.10 + df.tt*0.07 + df.util*0.06)
    df["default"] = (np.random.rand(n) < (1-(raw-1)/3)*0.25).astype(int)
    X, y = df.drop("default", axis=1), df["default"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    m = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1,
                      scale_pos_weight=3, random_state=42, eval_metric="logloss")
    m.fit(Xtr, ytr)
    auc = round(roc_auc_score(yte, m.predict_proba(Xte)[:,1]), 3)
    return m, auc

def calc_score(p, ov={}):
    d = {**p, **ov}
    ir = 4 if d["exp"]<=0.4 else 3 if d["exp"]<=0.6 else 2 if d["exp"]<=0.8 else 1
    te = 4 if d["ejari"]>=3 else 3 if d["ejari"]>=1 else 2 if d["ejari"]>=0.5 else 1
    tt = 4 if d["telco_mo"]>=36 else 3 if d["telco_mo"]>=12 else 2 if d["telco_mo"]>=6 else 1
    raw = (d["rent"]*0.28 + d["sal"]*0.22 + te*0.12 +
           ir*0.15 + d["telco"]*0.10 + tt*0.07 + d["util"]*0.06)
    return int(round(300 + ((raw-1)/3)*550))

def tier(s):
    if s >= 700: return "Low Risk",      "pill-low",  ACCENT
    if s >= 550: return "Moderate Risk", "pill-mod",  WARN
    return              "High Risk",     "pill-high", DANGER

def smart_reply(q, p, sc):
    q = q.lower()
    lbl, _, _ = tier(sc)
    eligible = [b["name"] for b in BANKS if sc >= b["min"]]
    if any(x in q for x in ["improv","increas","boost","higher","better"]):
        tips = []
        if p["telco"] < 4: tips.append("switch to a postpaid phone contract")
        if p["exp"] > 0.5: tips.append("bring monthly expenses below 50% of income")
        if p["ejari"] < 1: tips.append("register your tenancy on Ejari")
        if not tips: tips.append("take a micro loan and repay on time")
        return f"Your score is {sc}/850. Fastest wins: " + "; ".join(tips) + "."
    if any(x in q for x in ["bank","apply","loan","eligible","qualify"]):
        if eligible:
            return f"With {sc} points you qualify at: {', '.join(eligible)}. Start with Mashreq — lowest threshold and fastest for new expats."
        return f"At {sc} you are below all bank thresholds. Take a micro loan, repay for 3 months, and you will unlock Mashreq at 580."
    if any(x in q for x in ["mortgage","home","house","property"]):
        gap = max(0, 700-sc)
        return f"FAB requires 700 for home mortgages. You are {gap} points away. Better rent consistency and lower expenses can close that in 6-9 months."
    if any(x in q for x in ["micro","borrow","credit builder"]):
        return f"A micro loan is your best move. Borrow AED {min(1000, 300+(sc-300)//2):,}, repay monthly, and each payment gets reported to AECB."
    if any(x in q for x in ["passport","leave","move","uk","canada","australia"]):
        return "Your Credit Passport is valid for 12 months and accepted in the UK, Canada, and Australia. Show it alongside your UAE employment letter to open a secured credit card abroad."
    if any(x in q for x in ["wallet","digital","balance","pay"]):
        return "Every bill you pay through the CreditBridge Wallet is reported as a positive signal in your score. It is the fastest way to build payment history without a bank account."
    return f"Your CreditBridge score is {sc}/850 ({lbl}). You have been in UAE for {p.get('months_in_uae','a few')} months with no bank history yet, but your rent, salary, and utility behaviour tell a strong story. What would you like to explore?"

model, auc_score = train_model()

defaults = dict(screen="login", profile=None, score=None,
                loan_applied=False, selected_loan=None,
                passport_done=False, chat=[],
                apple_pay=True, google_pay=False)
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# =========================================================
# LOGIN
# =========================================================
if st.session_state.screen == "login":
    st.markdown(f"""
    <div style="text-align:center;padding:28px 0 20px;">
        <div style="width:56px;height:56px;background:#131924;border:1px solid {BORDER};
                    border-radius:16px;display:flex;align-items:center;justify-content:center;
                    margin:0 auto 14px;font-size:24px;">💳</div>
        <div class="brand-title">Credit<span>Bridge</span></div>
        <div class="brand-sub">No UAE credit history? We build it from scratch.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#0d1421;border:1px solid {BORDER};border-radius:14px;
                padding:16px 18px;margin-bottom:20px;">
        <div style="font-size:12px;color:{ACCENT};font-weight:600;margin-bottom:10px;">
            Who is CreditBridge for?
        </div>
        <div style="font-size:13px;color:{MUTED};line-height:1.8;">
            You just arrived in UAE. You have a job, you pay rent on time, your DEWA bill
            is settled every month — but UAE banks have
            <strong style="color:{TEXT};">zero record of you.</strong><br><br>
            CreditBridge reads your real financial behaviour from government
            systems and gives you a score banks can act on.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="cb-card"><div class="sec-head">Sign in with UAE Pass</div>', unsafe_allow_html=True)
    eid = st.selectbox("Select profile (demo)", list(PROFILES.keys()), label_visibility="collapsed")
    pin = st.text_input("UAE Pass PIN", value="123456", type="password", placeholder="Enter 6-digit PIN")
    login_btn = st.button("Continue with UAE Pass")
    st.markdown(f'<p style="text-align:center;font-size:11px;color:{BORDER};margin-top:8px;">Demo PIN: 123456</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if login_btn:
        if pin != "123456":
            st.error("Incorrect PIN. Use 123456 for the demo.")
        else:
            st.session_state.profile = PROFILES[eid]
            st.session_state.screen  = "fetch"
            st.rerun()

    st.markdown(f'<div class="sec-head" style="margin-top:24px;">How we score you without bank history</div>', unsafe_allow_html=True)
    for src, sub in SOURCES:
        st.markdown(f'<div class="row"><span class="row-label">✅ {src}</span><span style="font-size:11px;color:{MUTED};">{sub}</span></div>', unsafe_allow_html=True)


# =========================================================
# FETCHING
# =========================================================
elif st.session_state.screen == "fetch":
    p = st.session_state.profile
    st.markdown(f"""
    <div style="text-align:center;padding:28px 0 20px;">
        <div style="font-size:20px;font-weight:600;color:{TEXT};">Building your profile</div>
        <div style="font-size:13px;color:{MUTED};margin-top:6px;">
            Pulling data from UAE government systems for {p['name']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    prog  = st.progress(0)
    slots = [st.empty() for _ in SOURCES]
    for i, (src, sub) in enumerate(SOURCES):
        for j in range(i):
            slots[j].markdown(f'<div class="fi fi-done"><span style="font-size:16px;">✅</span><div><div style="font-size:13px;font-weight:500;color:{TEXT};">{SOURCES[j][0]}</div><div style="font-size:11px;color:{ACCENT};">{SOURCES[j][1]}</div></div></div>', unsafe_allow_html=True)
        slots[i].markdown(f'<div class="fi"><span style="font-size:16px;">⏳</span><div><div style="font-size:13px;font-weight:500;color:{TEXT};">{src}</div><div style="font-size:11px;color:{MUTED};">{sub}</div></div></div>', unsafe_allow_html=True)
        prog.progress((i+1)/len(SOURCES))
        time.sleep(0.65)
    for j in range(len(SOURCES)):
        slots[j].markdown(f'<div class="fi fi-done"><span style="font-size:16px;">✅</span><div><div style="font-size:13px;font-weight:500;color:{TEXT};">{SOURCES[j][0]}</div><div style="font-size:11px;color:{ACCENT};">{SOURCES[j][1]}</div></div></div>', unsafe_allow_html=True)
    time.sleep(0.4)
    st.session_state.score  = calc_score(p)
    st.session_state.screen = "app"
    st.rerun()


# =========================================================
# MAIN APP
# =========================================================
elif st.session_state.screen == "app":
    p   = st.session_state.profile
    sc  = st.session_state.score
    lbl, css, col = tier(sc)
    pct = int(((sc-300)/550)*100)
    initials = "".join(w[0] for w in p["name"].split())

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                padding:12px 4px 14px;border-bottom:1px solid {BORDER};margin-bottom:14px;">
        <div class="brand-title" style="font-size:18px;">Credit<span>Bridge</span></div>
        <div style="display:flex;gap:10px;align-items:center;">
            <div style="font-size:12px;color:{MUTED};">{p['name']}</div>
            <div style="width:32px;height:32px;border-radius:50%;background:#131924;
                        border:1px solid {BORDER};display:flex;align-items:center;
                        justify-content:center;font-size:11px;font-weight:700;color:{ACCENT};">
                {initials}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["Score","Banks","Loan","Wallet","Passport","Simulator","AI Advisor"])


    # -------------------------
    # TAB 1: SCORE
    # -------------------------
    with tabs[0]:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=sc,
            number=dict(font=dict(size=54, color=col, family="Inter")),
            gauge=dict(
                axis=dict(range=[300,850], tickcolor=MUTED, tickfont=dict(color=MUTED, size=10), nticks=7),
                bar=dict(color=col, thickness=0.22),
                bgcolor=CARD, bordercolor=BORDER, borderwidth=1,
                steps=[
                    dict(range=[300,550], color="rgba(239,68,68,0.06)"),
                    dict(range=[550,700], color="rgba(245,158,11,0.06)"),
                    dict(range=[700,850], color="rgba(0,201,167,0.06)"),
                ],
                threshold=dict(line=dict(color=col,width=3), thickness=0.75, value=sc)
            )
        ))
        fig_g.update_layout(height=210, margin=dict(l=20,r=20,t=10,b=0),
                            paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_g, use_container_width=True)

        st.markdown(f'<div style="text-align:center;margin-bottom:6px;"><span class="pill {css}">{lbl}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;font-size:12px;color:{MUTED};margin-bottom:16px;">out of 850 · AECB-calibrated · {p.get("months_in_uae","?")} months in UAE</div>', unsafe_allow_html=True)

        if sc >= 650:
            blurb = f"Strong profile for someone who arrived {p.get('months_in_uae','?')} months ago. Your rent and salary signals are doing the heavy lifting."
        elif sc >= 550:
            blurb = f"Solid start for {p.get('months_in_uae','?')} months in UAE. Improving telecom tenure and expense ratio will push you into low-risk within months."
        else:
            blurb = f"At {p.get('months_in_uae','?')} months in UAE, your footprint is still building. A CreditBridge micro loan repaid on time is the fastest path forward."
        st.markdown(f'<div style="font-size:13px;color:{MUTED};line-height:1.8;margin-bottom:18px;padding:14px 16px;background:#0d1421;border-radius:12px;border:1px solid {BORDER};">{blurb}</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-head">Your Profile</div>', unsafe_allow_html=True)
        for l, v in [("Monthly income", f"AED {p['salary']:,}"), ("Employer", p['employer']),
                     ("Visa type", p['visa']), ("UAE tenure", f"{p.get('months_in_uae','?')} months"),
                     ("WPS registered", "Yes" if p['wps'] else "No"), ("Expense ratio", f"{int(p['exp']*100)}%")]:
            st.markdown(f'<div class="row"><span class="row-label">{l}</span><span class="row-val">{v}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-head" style="margin-top:20px;">What is driving your score</div>', unsafe_allow_html=True)
        feats = ["Rent consistency","Salary regularity","Telecom","Utility payments"]
        vals  = [p["rent"], p["sal"], p["telco"], p["util"]]
        clrs  = [col if v>=3 else WARN if v==2 else DANGER for v in vals]
        fig_b = go.Figure(go.Bar(
            x=[v/4*100 for v in vals], y=feats, orientation="h",
            marker_color=clrs, marker_line_width=0,
            text=[f"{v/4*100:.0f}%" for v in vals],
            textposition="outside", textfont=dict(color=MUTED, size=11),
        ))
        fig_b.update_layout(
            height=175,
            xaxis=dict(range=[0,130], showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(tickfont=dict(color=MUTED, size=12)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=50,t=0,b=0), showlegend=False
        )
        st.plotly_chart(fig_b, use_container_width=True)
        st.markdown(f'<p style="text-align:center;font-size:11px;color:{BORDER};">XGBoost · AUC {auc_score} · 1,000 synthetic UAE profiles</p>', unsafe_allow_html=True)


    # -------------------------
    # TAB 2: BANKS
    # -------------------------
    with tabs[1]:
        eligible   = [b for b in BANKS if sc >= b["min"]]
        ineligible = [b for b in BANKS if sc <  b["min"]]

        st.markdown(f'<div class="cb-card"><div style="font-size:11px;color:{MUTED};margin-bottom:4px;">Your score</div><div style="font-size:40px;font-weight:700;color:{col};">{sc}</div><div style="font-size:13px;color:{MUTED};margin-top:2px;">{lbl} · {len(eligible)} of {len(BANKS)} banks eligible</div></div>', unsafe_allow_html=True)

        fig_d = go.Figure(go.Pie(
            labels=["Eligible","Not yet"],
            values=[max(len(eligible), 0.01), len(ineligible)],
            hole=0.72, textinfo="none",
            marker=dict(colors=[ACCENT,"#131924"], line=dict(color=BG, width=3)),
            hovertemplate="%{label}: %{value} banks<extra></extra>",
        ))
        fig_d.add_annotation(
            text=f"{len(eligible)}/{len(BANKS)}",
            font=dict(size=22, color=ACCENT, family="Inter"),
            showarrow=False, x=0.5, y=0.5
        )
        fig_d.update_layout(
            height=180, showlegend=True,
            legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.05,
                        font=dict(color=MUTED, size=12), bgcolor="rgba(0,0,0,0)"),
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=10,b=40)
        )
        st.plotly_chart(fig_d, use_container_width=True)

        st.markdown('<div class="sec-head">Bank by bank</div>', unsafe_allow_html=True)
        for b in BANKS:
            ok  = sc >= b["min"]
            gap = b["min"] - sc
            badge = f'<span class="pill pill-low">Eligible</span>' if ok else f'<span class="pill pill-mod">+{gap} pts</span>'
            cls   = "bank-row bank-ok" if ok else "bank-row"
            st.markdown(f'<div class="{cls}"><div style="flex:1;"><div style="font-size:13px;font-weight:600;color:{TEXT};">{b["name"]}</div><div style="font-size:11px;color:{MUTED};margin-top:2px;">{b["product"]} · {b["rate"]} · up to {b["max"]}</div></div>{badge}</div>', unsafe_allow_html=True)
            if not ok:
                pp = min(sc/b["min"]*100, 100)
                st.markdown(f'<div class="prog-bg" style="margin:-4px 0 10px;"><div class="prog-fill" style="width:{pp:.0f}%;background:{WARN};"></div></div>', unsafe_allow_html=True)


    # -------------------------
    # TAB 3: LOAN
    # -------------------------
    with tabs[2]:
        max_loan = 3000 if sc>=700 else 2000 if sc>=600 else 1000 if sc>=500 else 500
        st.markdown(f"""
        <div class="cb-card cb-accent">
            <div style="font-size:11px;color:{ACCENT};margin-bottom:8px;">Credit Builder Loan</div>
            <div style="font-size:13px;color:{MUTED};line-height:1.8;">
                No UAE credit history? A micro loan fixes that. Borrow a small amount,
                repay on time, and every repayment gets reported to AECB — building your
                formal credit trail from month one.<br>
                <strong style="color:{TEXT};">Your max eligibility: AED {max_loan:,}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.loan_applied:
            opts   = [l for l in LOANS if l["a"] <= max_loan]
            labels = [f"AED {l['a']:,} · {l['t']} month{'s' if l['t']>1 else ''} · {l['f']}% flat fee" for l in opts]
            choice = st.radio("Select amount", labels, label_visibility="collapsed")
            sel    = opts[labels.index(choice)]
            total  = sel["a"] * (1 + sel["f"]/100)
            mo     = total / sel["t"]
            st.markdown(f'<div class="row"><span class="row-label">Monthly payment</span><span class="row-val">AED {mo:,.0f}</span></div><div class="row"><span class="row-label">Total repayable</span><span class="row-val">AED {total:,.0f}</span></div><div class="row"><span class="row-label">Score impact</span><span class="row-val" style="color:{ACCENT};">+15 to 25 pts per repayment</span></div>', unsafe_allow_html=True)

            months = list(range(1, sel["t"]+1))
            proj   = [min(sc + i*20, 850) for i in months]
            fig_p  = go.Figure()
            fig_p.add_trace(go.Scatter(
                x=months, y=proj, mode="lines+markers",
                line=dict(color=ACCENT, width=2),
                marker=dict(color=ACCENT, size=7),
                fill="tozeroy", fillcolor="rgba(0,201,167,0.07)"
            ))
            fig_p.update_layout(
                height=140, margin=dict(l=40,r=10,t=10,b=40),
                xaxis=dict(title="Month", color=MUTED, tickcolor=MUTED, gridcolor=BORDER),
                yaxis=dict(title="Score", color=MUTED, gridcolor=BORDER),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_p, use_container_width=True)

            if st.button(f"Apply for AED {sel['a']:,}"):
                st.session_state.selected_loan = sel
                st.session_state.loan_applied  = True
                st.rerun()
        else:
            sel   = st.session_state.selected_loan
            total = sel["a"] * (1 + sel["f"]/100)
            mo    = total / sel["t"]
            st.success(f"Approved! AED {sel['a']:,} transferred within 24 hours.")
            st.markdown(f'<div class="row"><span class="row-label">First repayment</span><span class="row-val">AED {mo:,.0f} in 30 days</span></div><div class="row"><span class="row-label">Reporting</span><span class="row-val" style="color:{ACCENT};">Monthly to AECB</span></div>', unsafe_allow_html=True)
            if st.button("Apply for another loan"):
                st.session_state.loan_applied  = False
                st.session_state.selected_loan = None
                st.rerun()


    # -------------------------
    # TAB 4: WALLET
    # -------------------------
    with tabs[3]:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d1f35,#091729,#060f1e);
                    border-radius:20px;padding:24px;margin-bottom:16px;
                    border:1px solid {BORDER};position:relative;overflow:hidden;">
            <div style="position:absolute;top:-40px;right:-40px;width:150px;height:150px;
                        border-radius:50%;background:{ACCENT};opacity:0.06;"></div>
            <div style="font-size:10px;font-weight:700;letter-spacing:0.15em;
                        text-transform:uppercase;color:{ACCENT};margin-bottom:12px;">
                CreditBridge · Digital Wallet
            </div>
            <div style="font-size:12px;color:{MUTED};margin-bottom:6px;">Available balance</div>
            <div style="font-size:36px;font-weight:700;color:{TEXT};margin-bottom:16px;">AED 7,716</div>
            <div style="display:flex;justify-content:space-between;align-items:flex-end;">
                <div>
                    <div style="font-size:11px;color:{MUTED};margin-bottom:2px;">Card holder</div>
                    <div style="font-size:14px;font-weight:600;color:{TEXT};">{p['name']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:12px;color:{MUTED};font-family:monospace;letter-spacing:0.1em;">**** **** **** 4821</div>
                    <div style="font-size:11px;color:{MUTED};margin-top:2px;">Exp 04/29</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.2);
                    border-radius:12px;padding:12px 16px;margin-bottom:16px;font-size:12px;color:{MUTED};">
            <strong style="color:{TEXT};">Zero minimum balance.</strong> No salary transfer required.
            Open instantly with your Emirates ID. Works with Apple Pay and Google Pay.
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        for col_obj, label in [(c1,"Add Money"),(c2,"Send Money"),(c3,"Pay Bills")]:
            with col_obj:
                st.markdown(f'<div style="text-align:center;padding:14px 8px;background:{CARD};border:1px solid {BORDER};border-radius:12px;cursor:pointer;"><div style="font-size:20px;margin-bottom:6px;">{"➕" if label=="Add Money" else "➡️" if label=="Send Money" else "🧾"}</div><div style="font-size:12px;color:{MUTED};">{label}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-head" style="margin-top:16px;">Linked payment services</div>', unsafe_allow_html=True)
        ap_col, gp_col = st.columns(2)
        with ap_col:
            st.session_state.apple_pay  = st.toggle("Apple Pay",  value=st.session_state.apple_pay)
        with gp_col:
            st.session_state.google_pay = st.toggle("Google Pay", value=st.session_state.google_pay)

        st.markdown('<div class="sec-head" style="margin-top:16px;">AI spending recommendations</div>', unsafe_allow_html=True)
        for tip in [
            ("⚡", "Pay your DEWA bill through the wallet every month — it is your highest-impact score signal at 28% weight."),
            ("📱", "Switch to a postpaid du plan. Consistent monthly payments add telecom tenure to your score faster."),
            ("💸", f"Your expense ratio is {int(p['exp']*100)}%. Bring it below 50% to unlock the next score tier."),
        ]:
            st.markdown(f'<div style="display:flex;gap:12px;align-items:flex-start;padding:12px 14px;background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.15);border-radius:12px;margin-bottom:8px;"><span style="font-size:18px;flex-shrink:0;">{tip[0]}</span><span style="font-size:13px;color:{MUTED};line-height:1.7;">{tip[1]}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-head" style="margin-top:16px;">Spending breakdown</div>', unsafe_allow_html=True)
        total_spend = sum(d["value"] for d in SPENDING_DATA)
        fig_w = go.Figure(go.Pie(
            labels=[d["name"] for d in SPENDING_DATA],
            values=[d["value"] for d in SPENDING_DATA],
            hole=0.65, textinfo="none",
            marker=dict(colors=[d["color"] for d in SPENDING_DATA],
                        line=dict(color=BG, width=2)),
            hovertemplate="%{label}: AED %{value:,}<extra></extra>",
        ))
        fig_w.update_layout(
            height=200, showlegend=True,
            legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.08,
                        font=dict(color=MUTED, size=11), bgcolor="rgba(0,0,0,0)"),
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=10,b=50)
        )
        st.plotly_chart(fig_w, use_container_width=True)

        st.markdown('<div class="sec-head">Recent transactions</div>', unsafe_allow_html=True)
        for tx in WALLET_TXN:
            is_credit = tx["amount"] > 0
            amt_color = ACCENT if is_credit else TEXT
            sign      = "+" if is_credit else "-"
            st.markdown(f'<div class="row"><div><div style="font-size:13px;font-weight:500;color:{TEXT};">{tx["desc"]}</div><div style="font-size:11px;color:{MUTED};margin-top:2px;">{tx["merchant"]} · {tx["date"]}</div></div><div style="text-align:right;"><div style="font-size:13px;font-weight:600;color:{amt_color};">{sign}AED {abs(tx["amount"]):,}</div><div style="font-size:10px;color:{MUTED};margin-top:2px;">{tx["cat"]}</div></div></div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:rgba(0,201,167,0.04);border:1px solid rgba(0,201,167,0.18);
                    border-radius:14px;padding:16px 18px;margin-top:18px;">
            <div style="font-size:13px;font-weight:600;color:{TEXT};margin-bottom:8px;">
                How this wallet builds your score
            </div>
            <div style="font-size:13px;color:{MUTED};line-height:1.8;">
                Every on-time bill paid through the CreditBridge Wallet is counted as a positive
                signal in the scoring engine. Consistent wallet activity builds a richer payment
                history — faster than waiting for a bank statement.
            </div>
        </div>
        """, unsafe_allow_html=True)


    # -------------------------
    # TAB 5: PASSPORT
    # -------------------------
    with tabs[4]:
        st.markdown(f'<div class="cb-card cb-accent"><div style="font-size:11px;color:{ACCENT};margin-bottom:8px;">Credit Passport</div><div style="font-size:13px;color:{MUTED};line-height:1.8;">Leaving UAE? Your credit history should not die at the border. CreditBridge issues a portable score report accepted by partner financial institutions worldwide.</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-head">Partner countries</div>', unsafe_allow_html=True)
        for c in COUNTRIES:
            badge = f'<span class="pill pill-low">Live</span>' if c["live"] else f'<span class="pill pill-info">Soon</span>'
            st.markdown(f'<div class="row"><span class="row-label">{c["flag"]} {c["name"]} · {c["bureau"]}</span>{badge}</div>', unsafe_allow_html=True)

        if not st.session_state.passport_done:
            if st.button("Generate my Credit Passport"):
                with st.spinner("Generating..."):
                    time.sleep(1.5)
                st.session_state.passport_done = True
                st.rerun()
        else:
            lbl2, _, col2 = tier(sc)
            pid = f"CB-{abs(sum(ord(c) for c in p['name']))%100000:05d}"
            st.markdown(f"""
            <div style="border-radius:16px;overflow:hidden;border:1px solid {BORDER};margin-top:16px;">
                <div style="background:linear-gradient(135deg,#0d2535,#091d2b);padding:22px 20px;">
                    <div style="font-size:10px;color:{ACCENT};letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;">
                        CreditBridge Credit Passport
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <div style="font-size:21px;font-weight:700;color:{TEXT};">{p['name']}</div>
                            <div style="font-size:13px;color:{MUTED};margin-top:4px;">{p['nat']} · {p['visa']} Visa</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:40px;font-weight:700;color:{col2};">{sc}</div>
                            <div style="font-size:11px;color:{MUTED};">/ 850</div>
                        </div>
                    </div>
                </div>
                <div style="background:{CARD};padding:18px 20px;">
                    <div class="row"><span class="row-label">Rating</span><span class="row-val">{lbl2}</span></div>
                    <div class="row"><span class="row-label">UAE tenure</span><span class="row-val">{p.get('months_in_uae','?')} months</span></div>
                    <div class="row"><span class="row-label">Issued</span><span class="row-val">April 2026</span></div>
                    <div class="row"><span class="row-label">Valid until</span><span class="row-val">April 2027</span></div>
                    <div class="row" style="border:none;"><span class="row-label">Passport ID</span><span class="row-val">{pid}</span></div>
                    <div style="margin-top:12px;font-size:12px;color:{MUTED};">
                        Accepted in: 🇬🇧 UK · 🇨🇦 Canada · 🇦🇺 Australia
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


    # -------------------------
    # TAB 6: SIMULATOR
    # -------------------------
    with tabs[5]:
        st.markdown(f'<p style="font-size:13px;color:{MUTED};line-height:1.8;margin-bottom:16px;">Change your behaviours below and see your score update instantly along with which banks you unlock.</p>', unsafe_allow_html=True)

        o4  = ["Always on time (4)","Usually on time (3)","Sometimes late (2)","Often late (1)"]
        def v(s): return int(s[-2])

        r_s = st.selectbox("Rent payment consistency",  o4, index=4-p["rent"])
        s_s = st.selectbox("Salary regularity",         o4, index=4-p["sal"])
        t_s = st.selectbox("Phone payment behaviour",   o4, index=4-p["telco"])
        u_s = st.selectbox("DEWA payment record",       o4, index=4-p["util"])

        sim  = calc_score(p, {"rent":v(r_s),"sal":v(s_s),"telco":v(t_s),"util":v(u_s)})
        diff = sim - sc
        s_lbl, s_css, s_col = tier(sim)

        fig_c = go.Figure()
        for val, name, clr, dom in [(sc,"Current",col,[0,.46]),(sim,"Simulated",s_col,[.54,1])]:
            fig_c.add_trace(go.Indicator(
                mode="gauge+number", value=val,
                title=dict(text=name, font=dict(color=MUTED, size=12)),
                number=dict(font=dict(size=26, color=clr)),
                gauge=dict(
                    axis=dict(range=[300,850], tickcolor=MUTED,
                              tickfont=dict(color=MUTED, size=8), nticks=5),
                    bar=dict(color=clr, thickness=0.28),
                    bgcolor=CARD, bordercolor=BORDER, borderwidth=1
                ),
                domain=dict(x=dom, y=[0,1])
            ))
        fig_c.update_layout(height=170, paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig_c, use_container_width=True)

        dc = ACCENT if diff>0 else DANGER if diff<0 else MUTED
        st.markdown(f'<div style="text-align:center;font-size:32px;font-weight:700;color:{dc};margin-bottom:6px;">{"+" if diff>0 else ""}{diff} pts</div><div style="text-align:center;margin-bottom:18px;"><span class="pill {s_css}">{s_lbl}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-head">Bank eligibility at simulated score</div>', unsafe_allow_html=True)
        for b in BANKS:
            was_ok = sc >= b["min"]
            now_ok = sim >= b["min"]
            if not was_ok and now_ok:     tag, tc = "Unlocked!", ACCENT
            elif was_ok and not now_ok:   tag, tc = "Lost", DANGER
            elif now_ok:                  tag, tc = "Eligible", ACCENT
            else:                         tag, tc = f"Need +{b['min']-sim}", WARN
            st.markdown(f'<div class="row"><span class="row-label">{b["name"]}</span><span style="font-size:13px;font-weight:600;color:{tc};">{tag}</span></div>', unsafe_allow_html=True)


    # -------------------------
    # TAB 7: AI ADVISOR
    # -------------------------
    with tabs[6]:
        st.markdown(f'<div class="cb-card cb-accent"><div style="font-size:11px;color:{ACCENT};margin-bottom:8px;">AI Financial Advisor</div><div style="font-size:13px;color:{MUTED};line-height:1.8;">Score: <strong style="color:{TEXT};">{sc}/850</strong> · {lbl} · {p.get("months_in_uae","?")} months in UAE. Ask me anything about improving your score, which bank to target, or how the wallet helps.</div></div>', unsafe_allow_html=True)

        if not st.session_state.chat:
            c1, c2 = st.columns(2)
            qs = ["How do I improve my score?", "Which bank should I apply to?",
                  "Should I take a micro loan?", "How does the wallet help my score?"]
            for i, q in enumerate(qs):
                with (c1 if i%2==0 else c2):
                    if st.button(q, key=f"qq{i}"):
                        reply = smart_reply(q, p, sc)
                        st.session_state.chat += [{"role":"user","text":q}, {"role":"bot","text":reply}]
                        st.rerun()

        for msg in st.session_state.chat:
            cls = "chat-user" if msg["role"]=="user" else "chat-bot"
            st.markdown(f'<div class="{cls}">{msg["text"]}</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Ask about your score, loans, banks, or wallet...")
        if user_input:
            reply = smart_reply(user_input, p, sc)
            st.session_state.chat += [{"role":"user","text":user_input}, {"role":"bot","text":reply}]
            st.rerun()

    st.markdown("---")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        if st.button("Sign out"):
            for k, v2 in defaults.items():
                st.session_state[k] = v2
            st.rerun()
    st.markdown(f'<p style="text-align:center;font-size:11px;color:{BORDER};margin-top:6px;">CreditBridge v2.0 · Dubai · Not a regulated credit bureau.</p>', unsafe_allow_html=True)
