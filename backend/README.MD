# AI Table Summarization Backend

**Author:** Youssef Aitbouddroub

A Flask REST API that powers the AI table summarization application.

The backend allows users to:

- Upload CSV datasets
- Browse uploaded tables
- Filter rows
- Select (highlight) table cells
- Convert the table into a structured prompt
- Generate natural-language summaries using a LoRA fine-tuned FLAN-T5 model

The system was developed as part of an industrial internship project on fine-tuning Small Language Models (SLMs) for table-to-text generation.

---

# Project Structure

backend/
│
├── models/
│ ├── flan-t5-base-local/
│ └── flan-t5-base-totto-lora-finetuned/
│
├── app.py   # Flask REST API
├── model.py # Model loading + prompt engineering + inference
├── utils.py # Helper utilities
├── .gitignore
└── README.md

---

# Features

- REST API
- CSV upload
- In-memory dataset management
- Pagination
- Row filtering
- Interactive highlighted-cell summarization
- Prompt engineering
- LoRA fine-tuned FLAN-T5 inference
- GPU acceleration (CUDA)
- CORS enabled

---

# Technologies Used

- Python 3.11+
- Flask
- Flask-CORS
- Pandas
- PyTorch (cuda)
- Transformers
- PEFT (LoRA)
- HuggingFace

---

# Installation

## 1 Clone the repository

```bash
git clone https://github.com/BigB021/FT_SLM_APP.git
cd backend
```

---

## 2 Create a virtual environment

Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3 Install dependencies

```bash
pip install -r requirements.txt
```

Typical packages include

```text
Flask
Flask-Cors
pandas
torch (you might wanna adjust the version depending on if you want to use cpu or gpu for inference)
transformers
peft
accelerate
sentencepiece
```

---

## 4 Download / Place Models

The backend expects two folders inside `models/`

```
models/
│
├── flan-t5-base-local/
└── flan-t5-base-totto-lora-finetuned/
```

These contain

- Base FLAN-T5 model
- LoRA adapter

To download the FLAN T5 Base model locally on your machine run:
```python
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Download the model and tokenizer to your local cache
model_name = "google/flan-t5-base"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Save the model locally on your machine
local_path = "./models"
model.save_pretrained(local_path)
tokenizer.save_pretrained(local_path)
```

---

## 5 Run the server

```bash
python app.py
```

Expected output

```
Loading model at startup...
[+] Model Loaded Successfully

 * Running on http://localhost:5000
```

---

# API Overview

---

## Health Check

GET

```
/api/health
```

Response

```json
{
    "status":"ok"
}
```

---

## Upload CSV

POST

```
/api/upload
```

Form Data

```
file=<csv file>
```

Response

```json
{
  "upload_id":"...",
  "filename":"sales.csv",
  "columns":[
      "Product",
      "Price"
  ],
  "total_rows":250
}
```

---

## Retrieve Table Rows

GET

```
/api/rows
```

Parameters

| Parameter | Description |
|------------|-------------|
| upload_id | Upload identifier |
| start | Starting row |
| limit | Page size |
| filter_col | Column name |
| filter_val | Search value |

Example

```
GET /api/rows?upload_id=xxx&start=0&limit=25
```

Response

```json
{
    "rows":[
        {
            "index":0,
            "values":[...]
        }
    ],
    "total_filtered":250,
    "total_rows":250
}
```

---

## Generate Summary

POST

```
/api/summarize
```

Body

```json
{
  "upload_id":"...",
  "highlighted_cells":[
      [2,3],
      [2,5]
  ],
  "page_title":"Sales Report",
  "section_title":"Quarter 1",
  "section_text":"Regional Sales"
}
```

Response

```json
{
    "summary":"David sold $4631.23 worth of Food products.",
    "prompt":"..."
}
```

---

# Backend Workflow

```
CSV Upload
      │
      ▼
Pandas DataFrame
      │
      ▼
Stored in Memory
      │
      ▼
Frontend displays table
      │
      ▼
User highlights cells
      │
      ▼
Prompt Builder
      │
      ▼
Fine-tuned FLAN-T5
      │
      ▼
Generated Summary
```

---

# Memory Management

Uploaded datasets are stored in

```python
UPLOADS = {}
```

Each upload receives a UUID.

Example

```
UPLOADS

{
   "a29d....":
      DataFrame(...)
}
```

No files are permanently stored.

Restarting the server clears all uploaded datasets.

---

# Prompt Generation

The backend converts the selected table into a structured prompt.

The prompt contains

- Page title
- Section title
- Additional context
- Highlighted cells
- Windowed table

Example

```
Task:
Generate a factual sentence...

Page Title:
Sales Report

Section:
Quarter 1

Highlighted Cells:
(5,2)
(5,4)

Table:
...
```

This prompt is passed directly to the LoRA fine-tuned FLAN-T5 model.

---

# Model

Base model

```
google/flan-t5-base
```

Fine-tuning

```
LoRA
```

Task

```
Table-to-Text Generation
```

Dataset

```
ToTTo
```

Inference

- Beam Search
- No Sampling
- Maximum 64 generated tokens

---

# GPU Support

The backend automatically checks

- CUDA version
- GPU availability
- GPU memory

Example

```
torch version: 2.x

CUDA available: True

GPU:
RTX 3060

VRAM:
12 GB
```

---

# Error Handling

The API validates

- Missing uploads
- Invalid upload IDs
- Empty CSV files
- Invalid highlighted cells
- Invalid filters
- CSV parsing errors

All errors return JSON responses.

Example

```json
{
    "error":"Unknown upload_id."
}
```


# License

Academic / Research Use

Developed during an industrial internship project.