<div align="center">

# 📡 SkillRadar

### *Know exactly what skills the market wants. Before everyone else does.*

[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-SkillRadar-00D4AA?style=for-the-badge&logo=streamlit&logoColor=white)](https://your-streamlit-url.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![Scrapy](https://img.shields.io/badge/Scrapy-Spider-60A839?style=for-the-badge&logo=scrapy&logoColor=white)](https://scrapy.org)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/features/actions)

<br/>

> Built this because I was tired of guessing which skills to learn for placements.  
> So I built a system that scrapes real job listings, extracts what companies actually ask for,  
> and shows exactly where my skill gaps are. Live. Automated. No manual work.

<br/>

![SkillRadar Dashboard Preview](https://via.placeholder.com/900x400/0E1117/00D4AA?text=SkillRadar+Dashboard)

</div>

---

## 🤔 What problem does this solve?

Every student preparing for placements faces the same question: **"What should I learn next?"**

Most people guess. Or follow random YouTube roadmaps. Or copy what their friend is doing.

SkillRadar answers that question with actual data — scraped from real Indian job listings, processed with NLP, and shown as clear visual charts. You select your target role, add your current skills, and instantly see a **readiness score** plus exactly which high-demand skills you're missing.

No fluff. Just data.

---

## ✨ What it does

| Feature | Description |
|---|---|
| 🕷️ **Auto-scraping** | Pulls 400+ job listings every week via Adzuna API across 8 roles |
| 🧠 **NLP skill extraction** | Uses spaCy to extract skill keywords from job descriptions |
| 📊 **Live dashboard** | Streamlit app shows skill demand charts, city breakdown, role comparison |
| 🎯 **Skill gap analyzer** | Add your skills → see your readiness score + what you're missing |
| 📥 **PDF export** | Download a personalized market report for any role |
| 🔄 **Fully automated** | GitHub Actions runs the pipeline every Monday. Zero manual work. |

---

## 🏗️ How it's built

```
Adzuna API  ──→  Scrapy Spider  ──→  Supabase (PostgreSQL)
                                          │
                                    spaCy NLP extractor
                                          │
                              Streamlit Dashboard (public URL)
                                          │
                              GitHub Actions (runs weekly)
```

**No local server needed. No MongoDB. No Docker for production.**  
Everything runs on free cloud infrastructure.

---

## 🛠️ Tech stack

| Layer | Technology | Why |
|---|---|---|
| Scraping | Scrapy + Adzuna API | Fast async scraping, structured job data |
| NLP | spaCy `en_core_web_sm` | Keyword extraction from job descriptions |
| Database | Supabase (PostgreSQL) | Free, REST API, no SSL headaches |
| Dashboard | Streamlit + Plotly | Python-native, deploys in one click |
| Scheduler | GitHub Actions (cron) | Free, cloud, zero infrastructure |
| Charts | Plotly Graph Objects | Interactive, hoverable, clean dark theme |

---

## 📂 Project structure

```
SkillRadar/
├── spiders/
│   └── naukri_spider.py        # Scrapy spider — hits Adzuna API, writes to Supabase
├── models/
│   └── skill_extractor.py      # NLP pipeline — reads jobs, writes skill frequencies
├── dashboard/
│   └── app.py                  # Streamlit dashboard — all charts and UI
├── pipelines.py                # Scrapy pipeline — Supabase batch upsert
├── settings.py                 # Scrapy settings
├── .github/workflows/
│   └── scrape.yml              # GitHub Actions — runs every Monday 7:30 AM IST
└── requirements.txt
```

---

## 🚀 Run it locally

**1. Clone the repo**
```bash
git clone https://github.com/Soham-Alhat/SkillRadar.git
cd SkillRadar
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

**3. Set up secrets**

Create `dashboard/.streamlit/secrets.toml`:
```toml
SUPABASE_URL = "your-supabase-project-url"
SUPABASE_KEY = "your-supabase-anon-key"
```

**4. Scrape jobs**
```bash
python -m scrapy runspider spiders/naukri_spider.py -L INFO
```

**5. Extract skills**
```bash
python models/skill_extractor.py
```

**6. Run the dashboard**
```bash
streamlit run dashboard/app.py
```

---

## ⚙️ Automated pipeline (GitHub Actions)

Every Monday at 7:30 AM IST, GitHub's servers automatically:

1. Run the Scrapy spider → fetch fresh job listings
2. Run the skill extractor → update skill frequencies
3. Write everything to Supabase → dashboard shows new data

No laptop required. No cron job to set up locally.

The workflow file is at `.github/workflows/scrape.yml`.  
Secrets are stored in GitHub → Settings → Secrets → Actions.

---

## 📊 Roles tracked

```
Data Analyst          Python Developer      Data Scientist
Machine Learning Eng  Business Analyst      Data Engineer
SQL Developer         Power BI Developer
```

---

## 🔑 Environment variables

| Variable | Where to get it |
|---|---|
| `SUPABASE_URL` | Supabase → Project Settings → API |
| `SUPABASE_KEY` | Supabase → Project Settings → API (anon key) |
| `ADZUNA_APP_ID` | developer.adzuna.com → Create App |
| `ADZUNA_APP_KEY` | developer.adzuna.com → Create App |

---

## 💡 What I learned building this

- Scrapy's async pipeline and how to swap backends (MongoDB → Supabase) mid-project
- Why PostgreSQL's `ON CONFLICT` upsert fails on duplicate keys in the same batch — and how to deduplicate before inserting
- How GitHub Actions works as a free cloud scheduler — basically a cron job that runs Python scripts on their servers
- SSL handshake failures between Python 3.13 + Windows + older pymongo versions (brutal)
- Why Supabase is significantly easier to integrate than Atlas for REST-based pipelines

---

## 🔮 What's next

- [ ] Salary range data per role (Adzuna returns this, not displaying it yet)
- [ ] Weekly trend — did Python demand go up or down this week vs last week?
- [ ] Role comparison view — Data Analyst vs Data Scientist side by side
- [ ] Export as shareable link — `/report?role=data-analyst`

---

<div align="center">

Built by **Soham Alhat** · MCA Student · Placement prep 2025

*If this helped you figure out what to learn next, that's the whole point.*

[![GitHub](https://img.shields.io/badge/GitHub-Soham--Alhat-181717?style=flat-square&logo=github)](https://github.com/Soham-Alhat)

</div>
