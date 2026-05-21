"""
Theory page.
Dasar teori lengkap dengan rumus LaTeX:
  1. Content-Based Filtering
  2. Skill Vector Representation
  3. Asymmetric Coverage Score
  4. Cosine Similarity
  5. Preference Filter
  6. K-Means Clustering
  7. TF-IDF
  8. Evaluation Metrics (Precision@K, Recall@K, NDCG)
"""

import streamlit as st
from src.ui_components import render as _r


def _section(num, title, subtitle=None):
    sub = f'<div class="theory-sub">{subtitle}</div>' if subtitle else ""
    _r(f"""
        <div class="theory-section-header fade-in">
        <span class="theory-num">{num}</span>
        <div>
        <div class="theory-title">{title}</div>
        {sub}
        </div>
        </div>
    """)


def _prose(text):
    _r(f'<div class="theory-prose fade-in">{text}</div>')


def _formula_block(label, formula_lines, note=None):
    """Render a named formula block using Streamlit LaTeX."""
    _r(f'<div class="formula-block fade-in"><div class="formula-label">{label}</div>')
    for line in formula_lines:
        st.latex(line)
    if note:
        _r(f'<div class="formula-note">{note}</div>')
    _r('</div>')


def _definition(term, definition):
    _r(f"""
        <div class="def-row fade-in">
        <span class="def-term">{term}</span>
        <span class="def-def">{definition}</span>
        </div>
    """)


def render():
    # ── Page header ───────────────────────────────────────────
    _r("""
        <div class="page-hero-sm fade-in">
        <div class="page-hero-sm-tag">Theory</div>
        <h1 class="page-hero-sm-title">Mathematical Foundations</h1>
        <p class="page-hero-sm-sub">
        Complete derivation of every algorithm used in CareerMatch —
        from raw skill vectors to ranking metrics.
        </p>
        </div>
    """)

    # ── Table of contents ─────────────────────────────────────
    _r("""
        <div class="toc fade-in">
        <div class="toc-title">Contents</div>
        <ol class="toc-list">
        <li>Problem Formulation</li>
        <li>Skill Vector Representation</li>
        <li>Content-Based Filtering</li>
        <li>Cosine Similarity</li>
        <li>Asymmetric Coverage Score</li>
        <li>Preference Filter (Soft Penalty)</li>
        <li>K-Means Clustering</li>
        <li>TF-IDF Feature Extraction</li>
        <li>Evaluation Metrics</li>
        </ol>
        </div>
    """)

    # ══════════════════════════════════════════════════════════
    # 1. Problem Formulation
    # ══════════════════════════════════════════════════════════
    _section("1", "Problem Formulation",
             "Formalizing job recommendation as an information retrieval task")

    _prose("""
        Let <strong>U</strong> be the set of user profiles and <strong>J</strong>
        the set of job postings. The recommendation task is to learn a scoring
        function:
    """)

    _formula_block("Scoring function",
        [r"f: U \times J \;\rightarrow\; [0,\,1]"],
        "that assigns a relevance score for each (user, job) pair.")

    _prose("""
        We operate in the <strong>Content-Based Filtering</strong> paradigm:
        relevance is derived exclusively from the intrinsic attributes of items
        (skill requirements) and the user's explicit profile — no interaction
        history (clicks, applications) is needed.
    """)

    _r('<div class="theory-divider"></div>')

    # ══════════════════════════════════════════════════════════
    # 2. Skill Vector Representation
    # ══════════════════════════════════════════════════════════
    _section("2", "Skill Vector Representation",
             "Binary encoding of job requirements and user profiles")

    _prose("""
        Let <strong>V</strong> = {s₁, s₂, …, s<sub>n</sub>} be the global skill
        vocabulary of size <em>n</em>, built from all skills appearing at least
        <em>min_freq</em> times across the dataset.
    """)

    _formula_block("Job skill vector",
        [r"\mathbf{j} \in \{0,1\}^n, \quad j_k = \begin{cases} 1 & \text{if job requires skill } s_k \\ 0 & \text{otherwise} \end{cases}"],
        "Each job is a binary vector of length n.")

    _formula_block("User profile vector",
        [r"\mathbf{u} \in \{0,1\}^n, \quad u_k = \begin{cases} 1 & \text{if user possesses skill } s_k \\ 0 & \text{otherwise} \end{cases}"],
        "User profile encoded in the same space as job vectors.")

    _formula_block("Job-skill matrix",
        [r"\mathbf{M} \in \{0,1\}^{m \times n}"],
        "Row i = skill vector for job i. Shape: (m jobs) × (n skills).")

    _r('<div class="theory-divider"></div>')

    # ══════════════════════════════════════════════════════════
    # 3. Content-Based Filtering
    # ══════════════════════════════════════════════════════════
    _section("3", "Content-Based Filtering (CBF)",
             "Why CBF — not Collaborative Filtering or Hybrid")

    _prose("""
        <strong>Collaborative Filtering (CF)</strong> requires a user–item interaction
        matrix R ∈ ℝ<sup>|U|×|J|</sup> where R<sub>ui</sub> records whether user u
        applied to / viewed job j. The LinkedIn dataset used here contains only
        <em>job postings and their skill requirements</em> — no user interaction log.
        CF is therefore mathematically infeasible.
    """)

    _r("""
        <div class="theory-table fade-in">
        <table>
        <thead><tr><th>Method</th><th>Requires</th><th>Available?</th><th>Decision</th></tr></thead>
        <tbody>
        <tr><td>Content-Based Filtering</td><td>Item features (skill lists)</td><td>✅ Yes</td><td>✅ Used</td></tr>
        <tr><td>Collaborative Filtering</td><td>User–item interaction history</td><td>❌ No</td><td>❌ Excluded</td></tr>
        <tr><td>Hybrid</td><td>Both above</td><td>❌ Partial</td><td>❌ Excluded</td></tr>
        </tbody>
        </table>
        </div>
    """)

    _r('<div class="theory-divider"></div>')

    # ══════════════════════════════════════════════════════════
    # 4. Cosine Similarity
    # ══════════════════════════════════════════════════════════
    _section("4", "Cosine Similarity",
             "Symmetric angular similarity between two vectors")

    _formula_block("Cosine similarity",
        [r"\text{cos}(\mathbf{u},\,\mathbf{j}) \;=\; \frac{\mathbf{u} \cdot \mathbf{j}}{\|\mathbf{u}\|\;\|\mathbf{j}\|} \;=\; \frac{\sum_{k=1}^{n} u_k j_k}{\sqrt{\sum_k u_k^2}\;\sqrt{\sum_k j_k^2}}"])

    _prose("For binary vectors this simplifies to:")

    _formula_block("Binary cosine",
        [r"\text{cos}(\mathbf{u},\,\mathbf{j}) \;=\; \frac{|S_u \cap S_j|}{\sqrt{|S_u|}\;\sqrt{|S_j|}}"],
        "where S_u and S_j are the sets of skills the user has and the job requires.")

    _prose("""
        <strong>Limitation of pure cosine on skill vectors:</strong> the denominator
        normalises by both ‖u‖ and ‖j‖. A user with only 2 skills matching
        2 of 5 required skills yields cos = 2/(√2·√5) ≈ 0.632, which overstates
        actual coverage (40%). This motivates the asymmetric score below.
    """)

    _r('<div class="theory-divider"></div>')

    # ══════════════════════════════════════════════════════════
    # 5. Asymmetric Coverage Score
    # ══════════════════════════════════════════════════════════
    _section("5", "Asymmetric Coverage Score",
             "The primary ranking metric used in CareerMatch")

    _prose("""
        CareerMatch replaces pure cosine with a <em>coverage-weighted</em> score
        that measures how much of the <em>job's</em> requirements the user satisfies,
        making it directionally asymmetric (user → job, not symmetric).
    """)

    _formula_block("Coverage (recall from job's perspective)",
        [r"\text{cov}(\mathbf{u},\,\mathbf{j}) \;=\; \frac{\mathbf{u} \cdot \mathbf{j}}{\|\mathbf{j}\|_1} \;=\; \frac{|S_u \cap S_j|}{|S_j|}"],
        "Fraction of the job's required skills the user already possesses.")

    _formula_block("Final match score",
        [r"\text{score}(\mathbf{u},\,\mathbf{j}) \;=\; \alpha \cdot \text{cov}(\mathbf{u},\,\mathbf{j}) \;+\; (1-\alpha) \cdot \text{cos}(\mathbf{u},\,\mathbf{j})"],
        "α = 0.7 in CareerMatch. Coverage dominates; cosine acts as a tie-breaker.")

    _prose("Vectorised form over all m jobs:")

    _formula_block("Batch score vector",
        [r"\mathbf{s} \;=\; \alpha\;\frac{\mathbf{M}\mathbf{u}}{\mathbf{M}\mathbf{1}} \;+\; (1-\alpha)\;\frac{\mathbf{M}\mathbf{u}}{\|\mathbf{u}\|\;\|\mathbf{M}\|_{\text{row}}}"],
        "M ∈ {0,1}^{m×n}. Division is element-wise per job. Shape of s: (m,).")

    _prose("""
        <strong>Why α = 0.7?</strong> Empirical — higher α puts more weight on literal
        coverage (intuitive, prevents score inflation), while the cosine component
        (1−α = 0.3) ensures jobs sharing <em>most</em> skills still rank higher
        than jobs with only one or two exact matches.
    """)

    _r('<div class="theory-divider"></div>')

    # ══════════════════════════════════════════════════════════
    # 6. Preference Filter
    # ══════════════════════════════════════════════════════════
    _section("6", "Preference Filter — Soft Penalty",
             "Post-ranking adjustment for work type, salary, and industry")

    _prose("""
        After computing the raw score vector <strong>s</strong>, a multiplicative
        soft-penalty is applied. Jobs that do not match user preferences are
        <em>demoted</em> in rank — not removed — preserving diversity and
        allowing the user to still see near-misses.
    """)

    _formula_block("Penalised score",
        [r"s'_i \;=\; s_i \;\prod_{c \in C} p_c(i)"],
        "C = set of preference criteria. Each p_c(i) ∈ (0,1] for mismatch, 1 for match.")

    _r("""
        <div class="theory-table fade-in">
        <table>
        <thead><tr><th>Criterion</th><th>Penalty p_c</th><th>Condition</th></tr></thead>
        <tbody>
        <tr><td>Experience level</td><td>0.70</td><td>job level ≠ user level</td></tr>
        <tr><td>Work type (On-site)</td><td>0.70</td><td>remote_allowed = 1 but user wants On-site</td></tr>
        <tr><td>Work type (Remote)</td><td>0.70</td><td>remote_allowed = 0 but user wants Remote</td></tr>
        <tr><td>Industry</td><td>0.80</td><td>job industry ≠ preferred industry</td></tr>
        <tr><td>Company size</td><td>0.85</td><td>job company_size ∉ preferred bucket</td></tr>
        <tr><td>Salary below range</td><td>0.60</td><td>job salary &lt; 0.8 × min_salary</td></tr>
        <tr><td>Salary above range</td><td>0.85</td><td>job salary &gt; 1.3 × max_salary</td></tr>
        </tbody>
        </table>
        </div>
    """)

    _r('<div class="theory-divider"></div>')

    # ══════════════════════════════════════════════════════════
    # 7. K-Means Clustering
    # ══════════════════════════════════════════════════════════
    _section("7", "K-Means Clustering",
             "Unsupervised segmentation of the job market")

    _prose("""
        K-Means partitions the <em>m</em> job vectors into <em>K</em> cohesive clusters
        based on shared skill signatures, enabling market-segment analysis.
    """)

    _formula_block("K-Means objective",
        [r"\min_{\{\mu_k\}} \sum_{k=1}^{K} \sum_{i \in C_k} \|\mathbf{j}_i - \boldsymbol{\mu}_k\|^2"],
        "Minimise within-cluster sum of squared distances (inertia).")

    _formula_block("Centroid update",
        [r"\boldsymbol{\mu}_k \;=\; \frac{1}{|C_k|} \sum_{i \in C_k} \mathbf{j}_i"])

    _prose("<strong>Optimal K selection</strong> uses two criteria combined:")

    _formula_block("Elbow method — second derivative of inertia",
        [r"\Delta^2 W(K) \;=\; W(K-1) - 2W(K) + W(K+1)"],
        "K is chosen at the 'elbow' — where the marginal gain in tightness drops sharply.")

    _formula_block("Silhouette score",
        [r"s(i) \;=\; \frac{b(i) - a(i)}{\max\{a(i),\,b(i)\}}",
         r"\bar{s} \;=\; \frac{1}{m}\sum_{i=1}^{m} s(i)"],
        "a(i) = avg intra-cluster distance; b(i) = avg nearest-cluster distance. Range: [−1, 1].")

    _prose("The final K maximises the Silhouette score (verified visually against the Elbow curve).")

    _r('<div class="theory-divider"></div>')

    # ══════════════════════════════════════════════════════════
    # 8. TF-IDF
    # ══════════════════════════════════════════════════════════
    _section("8", "TF-IDF Feature Extraction",
             "Supplementary text representation from job descriptions")

    _prose("""
        In addition to binary skill vectors, job <em>descriptions</em> are encoded
        with TF-IDF to capture latent context (e.g. domain, seniority cues) not
        expressed in structured skill lists.
    """)

    _formula_block("Term Frequency",
        [r"\text{TF}(t, d) \;=\; \frac{f_{t,d}}{\sum_{t' \in d} f_{t',d}}"],
        "f_{t,d} = raw count of term t in document d.")

    _formula_block("Inverse Document Frequency",
        [r"\text{IDF}(t) \;=\; \log\!\left(\frac{1 + N}{1 + \text{df}(t)}\right) + 1"],
        "N = corpus size; df(t) = # documents containing t. +1 prevents zero IDF (smooth IDF).")

    _formula_block("TF-IDF weight",
        [r"\text{TFIDF}(t,d) \;=\; \text{TF}(t,d) \;\times\; \text{IDF}(t)"])

    _prose("""
        The combined feature vector for job <em>i</em> is:
    """)

    _formula_block("Combined feature vector",
        [r"\mathbf{x}_i \;=\; \left[\,\alpha_s \cdot \mathbf{j}_i \;\Big|\; \alpha_t \cdot \tilde{\mathbf{t}}_i\,\right]"],
        "α_s = 0.7, α_t = 0.3. j_i = binary skill vector; t̃_i = L2-normalised TF-IDF vector.")

    _r('<div class="theory-divider"></div>')

    # ══════════════════════════════════════════════════════════
    # 9. Evaluation Metrics
    # ══════════════════════════════════════════════════════════
    _section("9", "Evaluation Metrics",
             "Quantitative assessment of recommendation quality")

    _prose("""
        All metrics are computed using <strong>leave-one-skill-out</strong> validation:
        for each sampled job <em>i</em>, one skill s* is hidden from its profile;
        the remaining skills form the query; the system must retrieve other jobs
        requiring s* in its top-K results.
    """)

    _formula_block("Precision@K",
        [r"\text{P@K} \;=\; \frac{|\{j \in \text{top-K}\} \cap \text{Rel}|}{K}"],
        "Rel = set of all relevant jobs (those requiring the hidden skill s*).")

    _formula_block("Recall@K",
        [r"\text{R@K} \;=\; \frac{|\{j \in \text{top-K}\} \cap \text{Rel}|}{|\text{Rel}|}"])

    _formula_block("DCG@K",
        [r"\text{DCG@K} \;=\; \sum_{i=1}^{K} \frac{\text{rel}_i}{\log_2(i+1)}"],
        "rel_i = 1 if rank-i job is relevant, 0 otherwise.")

    _formula_block("Ideal DCG (IDCG@K)",
        [r"\text{IDCG@K} \;=\; \sum_{i=1}^{\min(|\text{Rel}|,K)} \frac{1}{\log_2(i+1)}"])

    _formula_block("NDCG@K",
        [r"\text{NDCG@K} \;=\; \frac{\text{DCG@K}}{\text{IDCG@K}}"],
        "Normalised DCG ∈ [0,1]. Penalises relevant items appearing lower in the ranking.")

    _prose("""
        <strong>Why these three?</strong> Precision@K measures <em>quality</em> of the top list.
        Recall@K measures <em>coverage</em>. NDCG combines both while being sensitive to
        <em>rank position</em> — a relevant result at rank 1 is worth more than at rank 10.
        Together they provide a complete picture of retrieval performance.
    """)

    _r('<div class="theory-divider"></div>')

    # ── Summary table ──────────────────────────────────────────
    _r("""
        <div class="theory-summary fade-in">
        <div class="theory-summary-title">Algorithm Summary</div>
        <table>
        <thead><tr><th>Component</th><th>Algorithm</th><th>Key Formula</th></tr></thead>
        <tbody>
        <tr><td>Representation</td><td>Binary skill vector</td><td>j ∈ {0,1}ⁿ</td></tr>
        <tr><td>Primary score</td><td>Asymmetric coverage</td><td>0.7·cov + 0.3·cos</td></tr>
        <tr><td>Post-filter</td><td>Soft multiplicative penalty</td><td>s' = s · ∏p_c</td></tr>
        <tr><td>Segmentation</td><td>K-Means (K=6)</td><td>min Σ‖j−μ‖²</td></tr>
        <tr><td>Text features</td><td>TF-IDF (d=300)</td><td>TF·IDF with smooth</td></tr>
        <tr><td>Evaluation</td><td>Leave-one-skill-out</td><td>P@K, R@K, NDCG@K</td></tr>
        </tbody>
        </table>
        </div>
    """)

    _r('<div class="page-footer">CareerMatch · ETS Data Mining · Statistika ITS 2026</div>')
