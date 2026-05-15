import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import certifi

st.set_page_config(page_title="SkillRadar", page_icon="📡", layout="wide")

@st.cache_data(ttl=300)
def load_skills():
    client = MongoClient(
    st.secrets["MONGO_URI"],
    tls=True,
    tlsCAFile=certifi.where()
    )
    db = client["skillradar"]
    skills = list(db["skills"].find({}, {"_id": 0}))
    jobs   = list(db["jobs"].find({}, {"_id": 0, "title": 1, "company": 1, "role": 1, "location": 1}))
    return pd.DataFrame(skills), pd.DataFrame(jobs)

skills_df, jobs_df = load_skills()

st.title("📡 SkillRadar")
st.caption("Live job market skill intelligence — Indian tech roles")

st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("Jobs Scraped",     len(jobs_df))
col2.metric("Unique Skills",    len(skills_df))
col3.metric("Top Skill",        skills_df.iloc[0]["skill"].title() if len(skills_df) else "—")

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Top 15 In-Demand Skills")
    top15 = skills_df.head(15)
    fig = px.bar(
        top15, x="count", y="skill",
        orientation="h",
        color="percentage",
        color_continuous_scale="teal",
        labels={"count": "Jobs requiring this skill", "skill": ""}
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=450)
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Skill Demand %")
    top10 = skills_df.head(10)
    fig2 = px.pie(
        top10, values="percentage", names="skill",
        color_discrete_sequence=px.colors.sequential.Teal
    )
    fig2.update_layout(height=450)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("Demand by Role")
if "role" in jobs_df.columns:
    role_counts = jobs_df["role"].value_counts().reset_index()
    role_counts.columns = ["role", "count"]
    fig3 = px.bar(role_counts, x="role", y="count",
                  color="count", color_continuous_scale="teal")
    st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.subheader("Raw Skills Table")
st.dataframe(skills_df, use_container_width=True)