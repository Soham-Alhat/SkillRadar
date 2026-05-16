import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
from supabase import create_client

st.set_page_config(page_title="SkillRadar", page_icon="📡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background: #0E1117; }
.metric-card {
  background: linear-gradient(135deg, #1A1F2E 0%, #16213E 100%);
  border: 1px solid #2A3040; border-radius: 16px;
  padding: 24px 28px; margin: 8px 0;
  transition: transform 0.2s ease, border-color 0.2s ease; }
.metric-card:hover { transform: translateY(-4px); border-color: #00D4AA; }
.metric-label { font-size: 11px; font-weight: 600; color: #8B9AB1;
  text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
.metric-value { font-size: 34px; font-weight: 700; color: #00D4AA; line-height: 1; }
.metric-sub { font-size: 11px; color: #556070; margin-top: 6px; }
.section-title { font-size: 18px; font-weight: 600; color: #FAFAFA;
  margin: 32px 0 16px 0; padding-bottom: 10px; border-bottom: 1px solid #2A3040; }
.insight-box {
  background: linear-gradient(135deg, rgba(0,212,170,0.05), rgba(108,99,255,0.05));
  border: 1px solid rgba(0,212,170,0.2); border-radius: 12px;
  padding: 20px 24px; margin: 12px 0; }
.insight-text { font-size: 14px; color: #C0CBDA; line-height: 1.7; }
.gap-item {
  background: #1A1F2E; border-left: 3px solid #FF6B6B;
  padding: 12px 16px; border-radius: 0 8px 8px 0;
  margin: 5px 0; font-size: 13px; color: #FAFAFA;
  transition: border-color 0.2s; }
.gap-item:hover { border-color: #00D4AA; }
.have-item {
  background: #1A1F2E; border-left: 3px solid #00D4AA;
  padding: 12px 16px; border-radius: 0 8px 8px 0;
  margin: 5px 0; font-size: 13px; color: #FAFAFA; }
.logo-text { font-size: 28px; font-weight: 700;
  background: linear-gradient(135deg, #00D4AA, #6C63FF);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.logo-sub { font-size: 13px; color: #556070; margin-bottom: 20px; }
div[data-testid="stSidebar"] { background: #12151E; border-right: 1px solid #2A3040; }
.stButton > button {
  background: linear-gradient(135deg, #00D4AA, #6C63FF);
  color: white; border: none; border-radius: 10px;
  padding: 10px 24px; font-weight: 600; width: 100%;
  transition: opacity 0.2s, transform 0.2s; }
.stButton > button:hover { opacity: 0.9; transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

PAPER  = "rgba(0,0,0,0)"
GRID   = "#2A3040"
FONT   = {"color": "#8B9AB1", "family": "Inter"}
TEAL   = "#00D4AA"
PURPLE = "#6C63FF"
COLORS = ["#00D4AA","#6C63FF","#00B894","#A29BFE","#0984E3","#74B9FF","#E17055","#FAB1A0"]

def base_layout(title="", height=420, extra=None):
    layout = dict(
        paper_bgcolor=PAPER, plot_bgcolor=PAPER, font=FONT,
        title=dict(text=title, font=dict(color="#FAFAFA", size=15)),
        height=height, margin=dict(l=10, r=20, t=44, b=10),
        hoverlabel=dict(bgcolor="#1A1F2E", bordercolor="#2A3040",
                        font=dict(color="#FAFAFA", size=13))
    )
    if extra:
        layout.update(extra)
    return layout

@st.cache_resource
def get_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

@st.cache_data(ttl=300)
def load_data():
    supa = get_client()
    skills_resp = supa.table("skills").select("*").order("count", desc=True).execute()
    jobs_resp   = supa.table("jobs").select("id,title,company,role,location,extracted_skills").execute()
    skills = pd.DataFrame(skills_resp.data)
    jobs   = pd.DataFrame(jobs_resp.data)
    return skills, jobs

with st.spinner("Loading market data..."):
    skills_df, jobs_df = load_data()

all_roles  = sorted(jobs_df["role"].dropna().unique().tolist()) if "role" in jobs_df.columns else []
all_skills = sorted(skills_df["skill"].str.title().tolist()) if len(skills_df) else []

# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-text">📡 SkillRadar</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">Live Indian job market intelligence</div>', unsafe_allow_html=True)
    st.markdown("### 🎯 Filter")
    selected_role = st.selectbox("Job Role", ["All Roles"] + all_roles)
    st.markdown("### 🧠 Your Skills")
    user_skills = st.multiselect("Select your current skills", options=all_skills,
                                  placeholder="e.g. Python, SQL...")
    st.markdown("### 🔍 Skill Search")
    skill_search = st.text_input("Search a skill", placeholder="e.g. pandas")
    st.markdown('<div style="font-size:11px;color:#556070;margin-top:4px">Shows how many scraped jobs require this skill</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📥 Export")
    export_btn = st.button("Download PDF Report")
    st.markdown("---")
    st.markdown('<div style="font-size:11px;color:#556070">Source: Adzuna API · Indian market<br>Refreshes every 5 min</div>', unsafe_allow_html=True)

# ── FILTER ─────────────────────────────────────────────────────────────────
filtered_jobs = jobs_df if selected_role == "All Roles" else jobs_df[jobs_df["role"] == selected_role]

if selected_role != "All Roles" and "extracted_skills" in filtered_jobs.columns:
    from collections import Counter
    all_extracted = []
    for s in filtered_jobs["extracted_skills"].dropna():
        if isinstance(s, list):
            all_extracted.extend(s)
    if all_extracted:
        counts = Counter(all_extracted)
        total  = len(filtered_jobs)
        role_skills_df = pd.DataFrame([
            {"skill": k, "count": v, "percentage": round(v/total*100, 1)}
            for k, v in counts.most_common()
        ])
    else:
        role_skills_df = skills_df
else:
    role_skills_df = skills_df

# ── HEADER ─────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="logo-text" style="font-size:30px">📡 SkillRadar</div>'
    f'<div class="logo-sub" style="font-size:13px;margin-bottom:20px">'
    f'Showing: <b style="color:#00D4AA">{selected_role}</b> · {len(filtered_jobs)} jobs analysed</div>',
    unsafe_allow_html=True)

# ── METRICS ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
top_skill = role_skills_df.iloc[0]["skill"].title() if len(role_skills_df) else "—"
top_pct   = role_skills_df.iloc[0]["percentage"]    if len(role_skills_df) else 0
cities    = filtered_jobs["location"].dropna().nunique() if "location" in filtered_jobs.columns else 0

for col, label, value, sub in [
    (c1, "Jobs Scraped",  len(filtered_jobs),  f"across {len(all_roles)} roles"),
    (c2, "Unique Skills", len(role_skills_df), "detected in descriptions"),
    (c3, "Top Skill",     top_skill,            f"in {top_pct}% of jobs"),
    (c4, "Cities Hiring", cities,               "unique locations"),
]:
    with col:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value" style="font-size:{'34px' if isinstance(value,int) else '22px'}">{value}</div>
          <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

# ── SKILL SEARCH ───────────────────────────────────────────────────────────
if skill_search:
    match = role_skills_df[role_skills_df["skill"].str.contains(skill_search.lower(), na=False)]
    if not match.empty:
        r     = match.iloc[0]
        level = ("🔥 High demand." if r["percentage"] > 20
                 else "📈 Moderate demand." if r["percentage"] > 10
                 else "💡 Niche — lower competition.")
        st.markdown(f"""
        <div class="insight-box">
          <div class="metric-label">Skill Search</div>
          <div class="insight-text">
            <b style="color:#00D4AA">{r['skill'].title()}</b> appears in
            <b style="color:#FAFAFA">{r['count']} jobs</b> —
            <b style="color:#FAFAFA">{r['percentage']}%</b> of listings. {level}
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.warning(f"'{skill_search}' not found in current data.")

# ── CHARTS ROW 1 ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Skill Demand Analysis</div>', unsafe_allow_html=True)
col_a, col_b = st.columns([3, 2])

with col_a:
    top15 = role_skills_df.head(15).copy()
    top15["skill"] = top15["skill"].str.title()
    fig1  = go.Figure(go.Bar(
        x=top15["count"], y=top15["skill"], orientation="h",
        marker=dict(color=top15["count"],
                    colorscale=[[0,"#1A3040"],[0.5,"#00897B"],[1,"#00D4AA"]],
                    showscale=False),
        hovertemplate="<b>%{y}</b><br>%{x} jobs require this skill<extra></extra>",
        text=top15["percentage"].apply(lambda x: f"{x}%"),
        textposition="outside",
        textfont=dict(color="#8B9AB1", size=11)
    ))
    fig1.update_layout(**base_layout("Top 15 In-Demand Skills", height=480, extra=dict(
        bargap=0.35,
        xaxis=dict(gridcolor=GRID, showgrid=True),
        yaxis=dict(gridcolor=GRID, showgrid=False, categoryorder="total ascending")
    )))
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    top8 = role_skills_df.head(8).copy()
    top8["skill"] = top8["skill"].str.title()
    fig2  = go.Figure(go.Pie(
        labels=top8["skill"], values=top8["percentage"], hole=0.55,
        marker=dict(colors=COLORS, line=dict(color="#0E1117", width=2)),
        hovertemplate="<b>%{label}</b><br>%{value}% of jobs<extra></extra>",
        textinfo="label+percent", textfont=dict(size=11, color="#C0CBDA"),
        pull=[0.05 if i == 0 else 0 for i in range(len(top8))]
    ))
    fig2.update_layout(**base_layout("Skill Share", height=480, extra=dict(
        showlegend=False,
        annotations=[dict(text="Top 8", x=0.5, y=0.5,
                     font=dict(size=13, color="#8B9AB1"), showarrow=False)]
    )))
    st.plotly_chart(fig2, use_container_width=True)

# ── CHARTS ROW 2 ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🏢 Role & Location Intelligence</div>', unsafe_allow_html=True)
col_c, col_d = st.columns(2)

with col_c:
    rc = jobs_df["role"].value_counts().reset_index()
    rc.columns = ["role", "count"]
    rc["role"] = rc["role"].str.title()
    fig3 = go.Figure(go.Bar(
        x=rc["role"], y=rc["count"],
        marker=dict(color=rc["count"],
                    colorscale=[[0,"#1A3040"],[1,PURPLE]], showscale=False),
        hovertemplate="<b>%{x}</b><br>%{y} openings<extra></extra>",
    ))
    fig3.update_layout(**base_layout("Jobs by Role", height=360, extra=dict(
        bargap=0.4,
        xaxis=dict(tickangle=-15, gridcolor=GRID),
        yaxis=dict(gridcolor=GRID)
    )))
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    if "location" in filtered_jobs.columns:
        loc = (filtered_jobs["location"].dropna()
               .str.split(",").str[0].str.strip()
               .value_counts().head(10).reset_index())
        loc.columns = ["city", "count"]
        fig4 = go.Figure(go.Bar(
            x=loc["count"], y=loc["city"], orientation="h",
            marker=dict(color=PURPLE, opacity=0.85),
            hovertemplate="<b>%{y}</b><br>%{x} openings<extra></extra>",
        ))
        fig4.update_layout(**base_layout("Top Hiring Cities", height=360, extra=dict(
            bargap=0.35,
            xaxis=dict(gridcolor=GRID),
            yaxis=dict(gridcolor=GRID, categoryorder="total ascending")
        )))
        st.plotly_chart(fig4, use_container_width=True)

# ── SKILL GAP ANALYZER ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">🎯 Skill Gap Analyzer</div>', unsafe_allow_html=True)

if not user_skills:
    st.markdown("""
    <div class="insight-box">
      <div class="insight-text" style="color:#556070">
        ← Select your current skills from the sidebar to see your gap analysis.
      </div>
    </div>""", unsafe_allow_html=True)
else:
    top20_skills = set(role_skills_df.head(20)["skill"].str.lower().tolist())
    user_set     = set([s.lower() for s in user_skills])
    have         = top20_skills & user_set
    missing      = top20_skills - user_set

    missing_data = (role_skills_df[role_skills_df["skill"].str.lower().isin(missing)]
                    .sort_values("count", ascending=False).head(8))
    have_data    = (role_skills_df[role_skills_df["skill"].str.lower().isin(have)]
                    .sort_values("count", ascending=False))

    coverage = round(len(have) / max(len(top20_skills), 1) * 100)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=coverage,
        number={"suffix": "%", "font": {"color": TEAL, "size": 40}},
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#556070",
                      tickfont=dict(color="#556070")),
            bar=dict(color=TEAL, thickness=0.25),
            bgcolor="#1A1F2E",
            steps=[
                dict(range=[0,  30],  color="#1A1F2E"),
                dict(range=[30, 60],  color="#162030"),
                dict(range=[60, 100], color="#162535"),
            ],
            threshold=dict(line=dict(color=TEAL, width=3), value=coverage)
        ),
        title={"text": "Role Readiness Score",
               "font": {"color": "#8B9AB1", "size": 13}}
    ))
    fig_gauge.update_layout(**base_layout(height=260,
                            extra=dict(margin=dict(l=30, r=30, t=30, b=10))))

    g1, g2, g3 = st.columns([1, 1, 1])
    with g1:
        st.plotly_chart(fig_gauge, use_container_width=True)
    with g2:
        st.markdown("**✅ Skills you have**")
        if have_data.empty:
            st.markdown('<div class="insight-text" style="color:#556070">None match top 20 demanded skills yet.</div>', unsafe_allow_html=True)
        for _, row in have_data.iterrows():
            st.markdown(
                f'<div class="have-item">{row["skill"].title()}'
                f'<span style="color:#00D4AA;float:right;font-weight:600">{row["percentage"]}%</span></div>',
                unsafe_allow_html=True)
    with g3:
        st.markdown("**❌ High-demand skills missing**")
        for _, row in missing_data.iterrows():
            st.markdown(
                f'<div class="gap-item">{row["skill"].title()}'
                f'<span style="color:#556070;float:right">{row["count"]} jobs</span></div>',
                unsafe_allow_html=True)

    label = ("Strong — go deep on what you have." if coverage >= 60
             else "Good start — prioritise the missing skills." if coverage >= 30
             else "Early stage — pick 2-3 from the gap list and master them.")
    st.markdown(f"""
    <div class="insight-box" style="margin-top:12px">
      <div class="insight-text">
        You match <b style="color:#00D4AA">{coverage}%</b> of top 20 skills
        for <b style="color:#FAFAFA">{selected_role}</b>. {label}
      </div>
    </div>""", unsafe_allow_html=True)

# ── AI Q&A ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">💬 Ask About This Data</div>', unsafe_allow_html=True)
question = st.text_input("", placeholder="e.g. Why is machine learning more demanded than SQL?")

if question and len(question) > 5:
    context = (
        f"You are a job market analyst. Answer only based on this data. "
        f"Role: {selected_role}. Total jobs: {len(filtered_jobs)}. "
        f"Top 10 skills: {role_skills_df.head(10)[['skill','percentage']].to_dict('records')}. "
        f"Answer in 3-5 sentences. Be direct and data-specific. No generic advice. "
        f"Question: {question}"
    )
    with st.spinner("Analysing..."):
        try:
            import requests
            res    = requests.post("http://localhost:11434/api/generate",
                                   json={"model":"llama3","prompt":context,"stream":False},
                                   timeout=30)
            answer = res.json().get("response", "")
            st.markdown(f'<div class="insight-box"><div class="insight-text">{answer}</div></div>',
                        unsafe_allow_html=True)
        except Exception:
            st.markdown("""
            <div class="insight-box">
              <div class="insight-text">
                <b style="color:#00D4AA">AI answers need Ollama running locally.</b><br>
                Open a new terminal and run:
                <code style="background:#2A3040;padding:2px 8px;border-radius:4px">ollama run llama3</code>
                then ask again.
              </div>
            </div>""", unsafe_allow_html=True)

# ── PDF EXPORT ─────────────────────────────────────────────────────────────
if export_btn:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import mm
        from datetime import datetime

        buf  = io.BytesIO()
        doc  = SimpleDocTemplate(buf, pagesize=A4,
                                 leftMargin=18*mm, rightMargin=18*mm,
                                 topMargin=18*mm, bottomMargin=18*mm)
        styl = getSampleStyleSheet()
        t_s  = ParagraphStyle("t", fontSize=22, fontName="Helvetica-Bold",
                               textColor=colors.HexColor("#00D4AA"), spaceAfter=4)
        s_s  = ParagraphStyle("s", fontSize=10, textColor=colors.HexColor("#8B9AB1"),
                               spaceAfter=16)
        h2_s = ParagraphStyle("h2", fontSize=13, fontName="Helvetica-Bold",
                               textColor=colors.HexColor("#1E1E2E"), spaceBefore=14, spaceAfter=6)
        b_s  = ParagraphStyle("b", fontSize=9, textColor=colors.HexColor("#4B5563"),
                               leading=14, spaceAfter=4)
        story = []
        story.append(Paragraph("📡 SkillRadar Report", t_s))
        story.append(Paragraph(
            f"Role: {selected_role} · {len(filtered_jobs)} jobs · "
            f"Generated {datetime.now().strftime('%d %b %Y %H:%M')}", s_s))
        story.append(Spacer(1, 8))
        story.append(Paragraph("Top 20 In-Demand Skills", h2_s))

        tdata = [["Rank", "Skill", "Jobs", "% Demand"]]
        for i, (_, row) in enumerate(role_skills_df.head(20).iterrows(), 1):
            tdata.append([str(i), row["skill"].title(), str(row["count"]), f"{row['percentage']}%"])

        t = Table(tdata, colWidths=[15*mm, 80*mm, 30*mm, 30*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#1E1E2E")),
            ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
            ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 8.5),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, colors.HexColor("#F9FAFB")]),
            ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#E5E7EB")),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("TEXTCOLOR",     (0,1), (-1,-1), colors.HexColor("#374151")),
        ]))
        story.append(t)

        if user_skills:
            story.append(Spacer(1, 12))
            story.append(Paragraph("Skill Gap Analysis", h2_s))
            story.append(Paragraph(
                f"Role readiness: {coverage}% of top 20 demanded skills matched.", b_s))
            for _, row in missing_data.iterrows():
                story.append(Paragraph(
                    f"• {row['skill'].title()} — {row['count']} jobs ({row['percentage']}%)", b_s))

        doc.build(story)
        buf.seek(0)
        st.download_button(
            label="📥 Download PDF",
            data=buf,
            file_name=f"SkillRadar_{selected_role.replace(' ','_')}.pdf",
            mime="application/pdf"
        )
        st.success("PDF ready — click Download PDF above.")
    except ImportError:
        st.error("Run: pip install reportlab")

# ── RAW TABLE ──────────────────────────────────────────────────────────────
with st.expander("📋 Full Skills Table"):
    st.dataframe(
        role_skills_df.style.background_gradient(subset=["count"], cmap="YlGn"),
        use_container_width=True, height=300
    )