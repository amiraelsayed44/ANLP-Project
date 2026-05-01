# Resume Analyzer — NLP Model

CV analysis system built with spaCy and FastAPI. Extracts structured info from resumes using Named Entity Recognition, then gives feedback via rule-based logic + Gemini AI.

## What's inside

```
model/
├── api.py                  # FastAPI endpoints
├── nlp_analyzer.py         # main NLP pipeline
├── requirements.txt
│
├── data/
│   ├── raw/                # original Kaggle dataset (220 resumes, JSONL)
│   └── processed/          # cleaned train/test splits after running notebook 01
│
├── notebooks/              # everything runs from here
│   ├── 01_dataset_preprocessing.ipynb
│   ├── 02_feature_extraction.ipynb
│   ├── 03_model_training.ipynb
│   └── 04_evaluation.ipynb
│
├── schemas/cv_schema.py    # Pydantic models
├── utils/
│   ├── constants.py
│   └── gemini_client.py
└── tests/
```

## Setup

```bash
pip install -r requirements.txt
python -m spacy download xx_ent_wiki_sm
```

## Running the notebooks

Run in order: 01 → 02 → 03 → 04.  
Notebook 01 reads from `data/raw/` and writes the cleaned splits to `data/processed/`.  
Notebook 03 saves the fine-tuned model to `fine_tuning/model_output/` (created automatically).

## API

```bash
uvicorn api:app --reload --port 8000
# docs at http://localhost:8000/docs
```

POST `/analyze` with `{"cv_text": "..."}` returns sections, skills, entities, suggestions.
