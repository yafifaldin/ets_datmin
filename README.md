# CareerMatch — IT Job Recommendation System

**ETS Data Mining — Sistem Rekomendasi Karir IT berbasis Content-Based Filtering**

## Authors
Yafi Muhammad Faldin - 5052241026 

Athaya Salsabila Alhen - 5052241004

Nabila Chesaria Octavia P. - 5052241006

CareerMatch adalah sistem rekomendasi yang membantu user menemukan posisi IT yang sesuai dengan skill dan preferensi mereka, lengkap dengan gap analysis terhadap target role dan personalized learning roadmap.

---

## 📋 Project Overview

| Komponen | Detail |
|---|---|
| **Domain** | IT job recommendation (Data Science, Software Engineering, Cloud, DevOps, dll) |
| **Method** | Content-Based Filtering dengan Cosine Similarity |
| **Tambahan** | K-Means Clustering, TF-IDF, Gap Analysis |
| **Evaluasi** | Precision@K, Recall@K, NDCG |
| **Framework** | Streamlit |
| **Visual theme** | LinkedIn-inspired |

### Mengapa Content-Based Filtering, bukan Hybrid?

Dataset LinkedIn yang tersedia berisi job postings + skill requirements, tapi **tidak mengandung user_id dengan riwayat aplikasi**. Karena Collaborative Filtering memerlukan data interaksi user-item, kami memilih CBF murni — pilihan metodologi yang **fit** terhadap karakteristik data, bukan memaksakan hybrid yang tidak punya basis data yang cukup.

---

## 🗂 Project Structure

```
ets_datmin/
├── app.py                          # Streamlit entry point
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml                 # LinkedIn theme config
├── assets/
│   ├── style.css                   # Custom LinkedIn-style CSS
│   ├── skill_taxonomy.json         # Skill list by category
│   └── roadmap_courses.json        # Skill → course mapping
├── data/
│   ├── raw/                        # Kaggle datasets (download manual)
│   └── processed/                  # Cleaned data output
├── src/
│   ├── __init__.py
│   ├── preprocessing.py            # Load & clean dataset
│   ├── feature_engineering.py      # Skill vocab, matrix, TF-IDF
│   ├── recommender.py              # CBF cosine similarity engine
│   ├── gap_analysis.py             # Skill match & gap detection
│   ├── clustering.py               # K-Means job segmentation
│   ├── evaluation.py               # Precision@K, Recall@K, NDCG
│   ├── roadmap.py                  # Learning path builder
│   ├── market_insights.py          # Descriptive analytics
│   ├── data_loader.py              # Cached data loading
│   └── ui_components.py            # Reusable Streamlit components
├── pages_logic/
│   ├── step_1_basics.py            # Form: experience, education
│   ├── step_2_skills.py            # Form: tech & soft skills
│   ├── step_3_preferences.py       # Form: work type, salary, etc.
│   ├── step_4_target.py            # Form: target job selection
│   ├── step_5_loading.py           # Loading animation
│   └── step_6_results.py           # Output dashboard
└── notebooks/
    ├── 01_data_preprocessing.ipynb
    ├── 02_feature_engineering.ipynb
    ├── 03_cbf_cosine_similarity.ipynb
    ├── 04_kmeans_clustering.ipynb
    └── 05_evaluation.ipynb
```

---

## 🚀 Quickstart

### 1. Install Dependencies

```bash
cd D:\ets_datmin
pip install -r requirements.txt
```

### 2. (Optional) Download Real Dataset

Kalau ingin pakai data LinkedIn asli (bukan synthetic demo):

Download dari Kaggle:
- https://www.kaggle.com/datasets/arshkon/linkedin-job-postings

Letakkan file-file ini di `data/raw/`:
- `postings.csv`
- `job_skills.csv`
- `job_industries.csv`
- `companies.csv`

Lalu jalankan preprocessing:
```bash
python -m src.preprocessing
```

**Tanpa download dataset**, app akan otomatis pakai 2000 synthetic IT jobs untuk demo. Output dashboard tetap fully functional.

### 3. Run Streamlit App

```bash
streamlit run app.py
```

Buka browser di http://localhost:8501

### 4. Run Analysis Notebooks

```bash
cd notebooks
jupyter notebook
```

Jalankan notebook 01 → 05 sesuai urutan.

---

## 🎯 User Flow (Google Form-style Wizard)

1. **Step 1 — Basic Profile**: experience, education, major, certifications
2. **Step 2 — Skills**: pilih technical skills (per kategori) + 3 soft skills
3. **Step 3 — Preferences**: work type, company size, industry, salary range
4. **Step 4 — Target Job**: pilih role yang ingin diraih (untuk gap analysis)
5. **Step 5 — Loading**: animasi sambil sistem menjalankan analisis
6. **Step 6 — Results**: 4 section output:
   - Top 10 job recommendations dengan match score
   - Gap analysis: skill yang sudah dimiliki vs yang perlu dipelajari
   - Market insights: salary distribution, top skills, hiring companies
   - Learning roadmap: kursus rekomendasi step-by-step

---

## 📊 Method Pipeline

```
1. Preprocessing
   └─ Load → Filter IT → Clean skills → Handle missing → Save
        ↓
2. Feature Engineering
   └─ Skill vocabulary → Binary job-skill matrix → TF-IDF on descriptions
        ↓
3. Content-Based Filtering
   └─ User vector → Cosine similarity → Apply preference filter → Top-N ranking
        ↓
4. Gap Analysis
   └─ Aggregate skill demand from target jobs → Compute overlap → Prioritize gaps
        ↓
5. K-Means Clustering (supplementary)
   └─ Segment jobs by skill profile → Auto-label clusters
        ↓
6. Evaluation
   └─ Leave-one-skill-out → Precision@K, Recall@K, NDCG
        ↓
7. Roadmap Generation
   └─ Map skill gaps to course recommendations from static directory
```

---

## 🧪 Evaluation Methodology

Leave-one-skill-out cross-validation:
1. Sample 200 job dari dataset
2. Untuk tiap sample, sembunyikan 1 random skill
3. Gunakan skill yang tersisa sebagai "user profile"
4. Lihat apakah job-job lain dengan skill yang disembunyikan muncul di top-K rekomendasi

Metrics yang dilaporkan: Precision@5/10/20, Recall@5/10/20, NDCG@5/10/20.

---

## 📚 Datasets

Project ini dirancang untuk bekerja dengan 2 dataset Kaggle:

1. **arshkon/linkedin-job-postings** (primary)
   - 124,000+ LinkedIn job postings (2023-2024)
   - Kolom: title, description, skills, salary, company info, dst

2. **asaniczka/data-science-job-postings-and-skills** (supplementary)
   - Focus pada data science roles

Tanpa kedua dataset tersebut, app jalan dalam **demo mode** dengan 2000 synthetic IT job postings yang realistic.

---

## 🛠 Tech Stack

- **Backend**: Python 3.10+
- **ML/Data**: scikit-learn, pandas, numpy, scipy
- **Visualisasi**: Altair, matplotlib, seaborn
- **UI**: Streamlit + custom CSS (LinkedIn theme)
- **Notebooks**: Jupyter

---

## 📝 License

Project akademis — ETS Mata Kuliah Data Mining.

---
