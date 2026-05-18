<div align="center">

# 📡 SkillRadar

### *Real-time Indian job market intelligence. Automated. No manual work.*

[![Live Dashboard](https://img.shields.io/badge/🚀%20Open%20Live%20Dashboard-Click%20Here-00D4AA?style=for-the-badge)](https://skillradar-eebjrxfsriafgeed5kksge.streamlit.app/)

<br/>

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com)
[![Scrapy](https://img.shields.io/badge/Scrapy-Spider-60A839?style=flat-square)](https://scrapy.org)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Auto%20Weekly-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![spaCy](https://img.shields.io/badge/spaCy-NLP-09A3D5?style=flat-square)](https://spacy.io)

</div>

![SkillRadar Dashboard Preview](https://github.com/user-attachments/assets/f34f7705-108c-4666-b91e-9836992f80d8)

![SkillRadar Analytics Preview](https://github.com/user-attachments/assets/95725901-4b4f-466e-9998-1615a46b99bb)

</div>
---

## 🎯 What is this?

I built SkillRadar because I was tired of guessing which skills to learn before placements.

Most students ask "what should I learn next?" and get random YouTube roadmap answers. SkillRadar answers that question with **actual live data** — scraped from real Indian job listings every week, processed with NLP, and shown as interactive charts.

**The whole system runs automatically. Every Monday morning, GitHub's servers (not my laptop) scrape fresh job data, extract skills, and update the dashboard. I don't touch anything.**

---

## 🔥 What you can actually do with it

<br/>

**🔍 Search any skill and see its real market demand**

Type "pandas" → instantly see how many jobs require it, what percentage of listings mention it, and whether it's high demand or niche.

<br/>

**🎯 Add your skills and get a readiness score**

Select the skills you have from the sidebar. The system compares them against the top 20 demanded skills for your target role and gives you:
- A gauge chart showing your readiness percentage
- Exactly which high-demand skills you're missing (sorted by demand)
- A plain-English verdict on where you stand

<br/>

**📊 Filter the entire dashboard by job role**

Switch between Data Analyst, Python Developer, Data Scientist, ML Engineer, Business Analyst, Data Engineer, SQL Developer, Power BI Developer. Every chart, every metric, every city — all updates to show only that role's data.

<br/>

**🏙️ See which cities are actually hiring**

Not just "Bangalore and Mumbai." The top 10 cities hiring for your specific role, ranked by number of openings.

<br/>

**💬 Ask questions about the data**

Type a question like "Why is machine learning more demanded than SQL here?" and get a data-specific answer (requires Ollama running locally).

<br/>

**📥 Download a PDF market report**

One click. Gets you a formatted report with the top 20 skills, demand percentages, and your personal gap analysis. Named after the role you selected.

---

## ⚙️ How the automation actually works

This is the part that makes it different from a regular dashboard.

```
Every Monday at 7:30 AM IST
         │
         ▼
GitHub Actions wakes up on GitHub's servers
(your laptop doesn't need to be on)
         │
         ▼
Scrapy spider hits Adzuna API
→ fetches 50 jobs × 3 pages × 8 roles = up to 1200 job listings
→ deduplicates by title + company
→ writes to Supabase in batches
         │
         ▼
spaCy NLP extractor reads every job description
→ matches 50+ skill keywords with word boundary detection
→ calculates frequency and percentage per skill
→ updates the skills table in Supabase
         │
         ▼
Streamlit dashboard reads fresh data from Supabase
→ anyone opening the dashboard sees this week's data
         │
         ▼
Done. No human involved.
```

The workflow file is at `.github/workflows/scrape.yml`.
API keys are stored as GitHub Secrets — never in the code.

---

## 🛠️ Tech stack and why each tool was chosen

| Tool | Role | Why this specifically |
|---|---|---|
| **Scrapy** | Web scraping | Async, fast, pipeline architecture — not just `requests` |
| **Adzuna API** | Job data source | Free tier, structured JSON, India-specific search |
| **spaCy** | NLP / skill extraction | Word boundary matching — "r" won't match inside "developer" |
| **Supabase** | Database | PostgreSQL with REST API, free tier, no SSL issues unlike Atlas |
| **GitHub Actions** | Scheduler | Runs on GitHub's servers, free, cron syntax, secrets management |
| **Streamlit** | Dashboard | Python-native, deploys in one click, Plotly integration |
| **Plotly** | Charts | Interactive hover, dark theme, donut + bar + gauge charts |
| **ReportLab** | PDF export | Programmatic PDF generation — tables, styles, layout |

---

## 📂 Project structure

```
SkillRadar/
├── .github/
│   └── workflows/
│       └── scrape.yml              ← GitHub Actions (runs every Monday)
├── spiders/
│   └── naukri_spider.py            ← Scrapy spider, writes to Supabase
├── models/
│   └── skill_extractor.py          ← NLP pipeline, reads + writes Supabase
├── dashboard/
│   └── app.py                      ← Full Streamlit dashboard
├── pipelines.py                    ← Scrapy → Supabase batch pipeline
├── settings.py                     ← Scrapy config
├── requirements.txt
└── .gitignore                      ← secrets.toml is in here, never committed
```

---

## 🚀 Run locally

```bash
# 1. clone
git clone https://github.com/Soham-Alhat/SkillRadar.git
cd SkillRadar

# 2. install
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. create secrets file (never commit this)
mkdir -p dashboard/.streamlit
cat > dashboard/.streamlit/secrets.toml << EOF
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-anon-key"
EOF

# 4. scrape
python -m scrapy runspider spiders/naukri_spider.py -L INFO

# 5. extract skills
python models/skill_extractor.py

# 6. run dashboard
streamlit run dashboard/app.py
```

---

## 🔐 Secrets — where they live

| Secret | Local | Cloud |
|---|---|---|
| `SUPABASE_URL` | `dashboard/.streamlit/secrets.toml` | Streamlit Cloud app secrets |
| `SUPABASE_KEY` | `dashboard/.streamlit/secrets.toml` | Streamlit Cloud app secrets |
| `ADZUNA_APP_ID` | Local env or secrets file | GitHub → Settings → Secrets → Actions |
| `ADZUNA_APP_KEY` | Local env or secrets file | GitHub → Settings → Secrets → Actions |

**No secret ever touches the codebase. `.gitignore` blocks `secrets.toml` from being committed.**

---

## 📊 Roles tracked

```
Data Analyst          │  Python Developer     │  Data Scientist
Machine Learning Eng  │  Business Analyst     │  Data Engineer
SQL Developer         │  Power BI Developer
```

---

## 🧱 Problems I actually ran into and fixed

**Supabase upsert crashing with `ON CONFLICT DO UPDATE command cannot affect row a second time`**
→ Adzuna returns duplicate jobs across pages. Fixed by deduplicating within each batch using a `seen` set before upserting.

**spaCy matching the letter "r" inside every word — 100% false positive rate**
→ Switched from `str.contains()` to `re.search()` with `\b` word boundary anchors.

**Python 3.13 + Windows + MongoDB Atlas SSL handshake failure — completely unsolvable**
→ Ditched Atlas entirely. Switched to Supabase which uses plain HTTPS REST calls. No driver-level SSL issues at all.

**GitHub Actions not finding spaCy model after pip install**
→ Added `python -m spacy download en_core_web_sm` as an explicit separate step in the workflow YAML.

---

## 🔮 Planned next

- [ ] Salary range by role — Adzuna returns this, just not displayed yet
- [ ] Week-on-week skill trend — did Python demand rise or fall vs last week?
- [ ] Role comparison view — two roles side by side
- [ ] Shareable URL per search — `/report?role=data-analyst`

---

<div align="center">

Built by **Soham Alhat** · MCA · Placement prep 2025

*Started because I didn't know what to learn. Ended up building the tool that answers that.*

[![GitHub](https://img.shields.io/badge/GitHub-Soham--Alhat-181717?style=flat-square&logo=github)](https://github.com/Soham-Alhat)

</div>
