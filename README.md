<!--
GitHub profile README.
To publish: create a public repo named Maria-James13/Maria-James13.
Put this file in it as README.md, and copy assets/github-banner.gif
(plus github-banner-still.png if you want the static version).
-->

<p align="center">
  <img src="assets/github-banner.gif" alt="Maria James — Applied AI and Machine Learning. Data to signal to intelligence." width="100%">
</p>

**AI/ML Engineer** building models that survive a real evaluation, not just a training-set score.

I work end to end: leakage-safe features, honest holdouts, baselines before boosting, and APIs that serve the frozen model. Recruiters looking at this page should start with the three featured projects — they are the ones that show how I think about production ML.

[GitHub](https://github.com/Maria-James13) · [LinkedIn](https://www.linkedin.com/in/maria-james-36b063340/) · [Email](mailto:mariajameskolamkuzhy@gmail.com) · [Resume](https://drive.google.com/file/d/10SPtBxaV3IDBjUDJdA04dtIL5LGBsfz3/view?usp=drive_link)

---

## Professional introduction

I am an AI/ML engineer focused on **tabular prediction, NLP/LLM systems, and model serving**.

The pattern I care about is the same across domains: define the target so the model can learn, keep time and IDs out of the features, beat a strong baseline, then ship inference behind a typed API. On freight rates that meant predicting rate-per-mile instead of raw dollars, scoring on a future month, and freezing the model before hidden validation. On NBA games that meant a chronological season split, Brier score next to accuracy, and FastAPI with tests. On clinical text that meant a RAG pipeline over FDA labels, not a prompt with no retrieval.

I would rather report a slightly worse MAE from a conservative config than publish a lucky hyperparameter search.

---

## Core technical skills

| Area | What I actually do |
|---|---|
| **Supervised ML** | Gradient boosting (CatBoost, XGBoost, GBM), logistic regression, stacking / meta-learners |
| **Evaluation** | Temporal holdouts, leakage audits, MAE / RMSE / MAPE / MedAE, Brier / log loss, segment error (equipment, distance, class) |
| **Feature engineering** | Target transforms (RPM, log), rolling windows with strict lookback, missingness flags, calendar encodings, imputers fit on train only |
| **NLP / LLMs** | RAG (ChromaDB, TF-IDF, sentence-transformers), Gemini / Groq / Llama, VADER sentiment, cognitive-distortion classification |
| **Serving** | FastAPI, Pydantic schemas, artifact load-at-startup, API-key auth, Docker / ECS-style packaging |
| **Data pipelines** | Train-only cleaners, FDA / HuggingFace ingestion, NewsAPI fetch, persistent vector stores |
| **Engineering** | Python, pandas, numpy, pytest / unittest, scikit-learn, Streamlit / Gradio |

---

## Featured projects

These three are the hiring packet. Everything else is supporting evidence.

### 1. Freight rate prediction — leakage-safe tabular ML

**[Freight_Rate](https://github.com/Maria-James13/Freight_Rate)** · Python · CatBoost · temporal validation

Predict truckload `posted_rate` (USD) from 48k labeled loads. Frozen candidate: **CatBoost on RPM** (`posted_rate / distance`), then `predicted_rate = predicted_rpm × distance`.

Why a recruiter should open this first:

- **Target transform that changed error structure**, not just the headline. Direct-rate CatBoost MAE $115.08; RPM $111.12. Short-haul MAPE fell from 19.8% to ~5% and stayed flat across distance buckets.
- **Baselines before trees.** Lane-median RPM was the strongest simple model ($190 MAE) and still **mispriced reefers at $298.52**. RPM CatBoost brought reefers to **$123.59** (58.6% reduction).
- **Leakage discipline.** `load_id` and `posted_rate` never enter features. Imputers fit on labeled train only. October holdout is time-forward; hidden validation is not used for model selection.
- **Honest error analysis.** Median AE $33, MAPE 5.12% — RMSE stays ~$646 because ~31 extreme loads dominate squared error. That is reported, not hidden.

`Python` `CatBoost` `pandas` `temporal split` `MAE/RMSE/MAPE`

### 2. NBA home-win service — evaluated model behind an API

**[NBA_Predictor](https://github.com/Maria-James13/NBA_Predictor)** · FastAPI · XGBoost · VADER

Home-win probability from pre-tip-off stats and optional per-team news. Five prediction cases (base rate → logistic → XGBoost → sentiment-adjusted → conservative bound). **59 pytest tests.** Models load from `artifacts/` at startup.

Why it is featured:

- **Production shape.** `POST /predict`, Pydantic schemas, optional API-key auth, NewsAPI auto-fetch, health endpoint.
- **Features with strict lookback.** Rolling win %, rest days, back-to-backs, H2H — all `GAME_DATE < current`. No future leak.
- **Metrics that match the problem.** Always-home is 55% accurate for free. Logistic regression **64.14% accuracy, Brier 0.2205** vs naive 0.2475. Chronological split: train 2019–2022, test 2023.

`FastAPI` `XGBoost` `scikit-learn` `VADER` `pytest` `HuggingFace datasets`

### 3. Drug interaction checker — RAG + LLM over a live knowledge base

**[EY_Test- / drug-interaction-checker](https://github.com/Maria-James13/EY_Test-/tree/main/drug-interaction-checker)** · FastAPI · ChromaDB · Gemini

User submits drugs → embed query → retrieve FDA label chunks → Gemini writes a grounded interaction analysis.

Pipeline: openFDA ingestion → local MiniLM embeddings → persistent ChromaDB → top-6 retrieval → Gemini generation. Frontend is a thin HTML/JS client; the model work is in the backend.

Why it is featured: this is the **NLP/LLM production pattern** — retrieval before generation, a rebuildable knowledge base, and an API (`/check-interactions`, `/rebuild-knowledge-base`), not a notebook that calls an LLM once.

`FastAPI` `ChromaDB` `sentence-transformers` `Gemini` `RAG`

---

## Other projects grouped by domain

### NLP & LLM systems

| Project | What it shows |
|---|---|
| **[PathFinderAI](https://github.com/Maria-James13/PathFinderAI)** | Career / learning-path assistant: TF-IDF retrieval over learning resources, Groq Llama-3.1 agent, Streamlit, Qdrant / sentence-transformers in the stack. |
| **[SelfTalk-AI](https://github.com/Maria-James13/SelfTalk-AI)** | Mood and cognitive-distortion analyzer: MiniLM embeddings, classification + regression metrics (MSE / MAE / RMSE, confusion matrix), Gradio UI. |
| **[NLP-tasks](https://github.com/Maria-James13/NLP-tasks)** | Course NLP labs (NLTK tokenization through later sequence / modeling notebooks). Foundation, not production. |

### Applied ML & sensing

| Project | What it shows |
|---|---|
| **[TrafficAnalysis](https://github.com/Maria-James13/TrafficAnalysis)** | Bangalore traffic dataset — exploratory modeling on congestion / urban mobility. |
| **[CIA3_ADA](https://github.com/Maria-James13/CIA3_ADA)** | Image and video analysis, including counterfeit-product inspection notebooks. |
| **[SPR-lab--2448529](https://github.com/Maria-James13/SPR-lab--2448529)** | Speech / pattern-recognition lab sequence (features, classification, reporting). |

### Applied systems

| Project | What it shows |
|---|---|
| **[Smart-Agriculture-System](https://github.com/Maria-James13/Smart-Agriculture-System)** | IoT dashboard (ESP8266 telemetry, charts, device views). Product/UI layer around sensor data, not the ML core. |

### Production sports APIs *(repo placeholder)*

| Project | What it shows |
|---|---|
| **Multi-league prediction service** · *[add GitHub URL]* | FastAPI app serving NBA / NCAA / MLB engines on one port, Docker image, ECS-style task definition, stacked GBM + logistic meta-learner, model registry, walk-forward training scripts. Stronger “shipped ML” story than the public NBA repo; not published yet. |

---

## Key technologies

**Languages:** Python (primary) · SQL · JavaScript (light frontends)

**ML:** CatBoost · XGBoost · scikit-learn · GradientBoosting · logistic regression · stacking

**NLP / LLMs:** sentence-transformers · ChromaDB · Qdrant · Gemini · Groq (Llama 3.1) · VADER · NLTK · RAG

**Serving & data:** FastAPI · Pydantic · pandas · numpy · HuggingFace datasets · openFDA · NewsAPI · Docker · AWS ECS *(production sports stack)*

**Quality:** pytest · unittest · leakage audits · chronological splits · baseline-first experiments

---

## Repository index

| Repo | Role on this page |
|---|---|
| [Freight_Rate](https://github.com/Maria-James13/Freight_Rate) | Featured — tabular ML, evaluation, features |
| [NBA_Predictor](https://github.com/Maria-James13/NBA_Predictor) | Featured — deployment + probabilistic eval |
| [EY_Test-](https://github.com/Maria-James13/EY_Test-) | Featured — RAG / LLM API |
| [PathFinderAI](https://github.com/Maria-James13/PathFinderAI) | NLP — agents + retrieval |
| [SelfTalk-AI](https://github.com/Maria-James13/SelfTalk-AI) | NLP — embeddings + eval UI |
| [NLP-tasks](https://github.com/Maria-James13/NLP-tasks) | NLP — coursework |
| [TrafficAnalysis](https://github.com/Maria-James13/TrafficAnalysis) | Applied ML |
| [CIA3_ADA](https://github.com/Maria-James13/CIA3_ADA) | Computer vision coursework |
| [SPR-lab--2448529](https://github.com/Maria-James13/SPR-lab--2448529) | Speech / SPR coursework |
| [Smart-Agriculture-System](https://github.com/Maria-James13/Smart-Agriculture-System) | IoT / dashboard |
| *[Sports prediction platform]* | Placeholder — production multi-league API |

`Java1` is an empty starter repo and is omitted on purpose.

---

If you want the short version: **I freeze a model only after a baseline, a leakage check, and a time-aware score — then I put it behind an API.**
