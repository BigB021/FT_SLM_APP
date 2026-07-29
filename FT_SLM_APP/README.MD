# AI Table Summarization Frontend

**Author:** Youssef Aitbouddroub

A modern React + TypeScript web application that provides an interactive interface for the AI-powered table summarization system.

The frontend allows users to:

- Upload CSV datasets
- Browse tabular data
- Select (highlight) one or more cells
- Send selected cells to the backend
- Display AI-generated summaries produced by the fine-tuned FLAN-T5 model

The application communicates with a Flask REST API and provides an intuitive interface for interacting with the AI model.

---

# Project Structure

```
FT_SLM_APP/
│
├── public/
├── src/
│   ├── api/
│   │   └── api.ts
│   │
│   ├── assets/
│   │
│   ├── components/
│   │   ├── DataTable.tsx
│   │   ├── FileUpload.tsx
│   │   └── SummaryPanel.tsx
│   │
│   ├── App.tsx
│   ├── main.tsx
│   └── style.css
│
├── package.json
├── package-lock.json
├── tsconfig.json
├── index.html
└── README.md
```

---

# Features

- Responsive React interface
- CSV upload
- Interactive table viewer
- Cell highlighting
- Pagination
- AI summary generation
- REST API integration
- Error handling
- TypeScript type safety

---

# Technologies Used

- React 19
- TypeScript
- Vite
- Fetch API
- React Icons
- CSS3

---

# Installation

## 1 Clone the repository

```bash
git clone https://github.com/BigB021/FT_SLM_APP.git

cd FT_SLM_APP
```

---

## 2 Install dependencies

```bash
npm install
```

---

## 3 Start the development server

```bash
npm run dev
```
or
```bash
npx vite
```
Default address

```
http://localhost:5173
```

---

## 4 Start the backend

The frontend expects the Flask backend to be running on

```
http://localhost:5000
```
API_BASE is set in ./src/api/api.ts
---

# Application Workflow

```
User uploads CSV
        │
        ▼
Frontend sends CSV
        │
        ▼
Flask Backend
        │
        ▼
CSV parsed into DataFrame
        │
        ▼
Rows returned
        │
        ▼
Interactive table displayed
        │
        ▼
User highlights cells
        │
        ▼
Highlighted cells sent to backend
        │
        ▼
Prompt generation
        │
        ▼
Fine-tuned FLAN-T5
        │
        ▼
Summary returned
        │
        ▼
Displayed in Summary Panel
```

---

# Component Overview

## App

Main application component responsible for

- Global application state
- Upload state
- Highlight state
- Summary generation
- Component communication

---

## FileUpload

Handles

- CSV selection
- Upload requests
- Upload errors
- Upload progress

---

## DataTable

Responsible for

- Displaying CSV rows
- Pagination
- Cell highlighting
- User interaction

---

## SummaryPanel

Responsible for

- Displaying selected cell count
- Generate Summary button
- Clear Selection button
- Displaying AI-generated summary

---

## API Module

Centralizes all communication with the backend.

Provides functions for

- uploadCsv()
- fetchRows()
- summarize()

---

# Backend Communication

The frontend communicates with

```
http://localhost:5000/api
```

---

## Upload

```
POST /upload
```

Returns

```json
{
  "upload_id":"...",
  "filename":"sales.csv",
  "columns":[...],
  "total_rows":250
}
```

---

## Fetch Rows

```
GET /rows
```

Returns paginated rows for display.

---

## Summarize

```
POST /summarize
```

Returns

```json
{
    "summary":"David sold Food products worth $4631.",
    "prompt":"..."
}
```

---

# State Management

The application maintains several pieces of state:

| State | Purpose |
|---------|----------|
| upload | Uploaded CSV metadata |
| highlighted | Selected table cells |
| summaryResult | Generated summary |
| isSummarizing | Loading indicator |
| summarizeError | Backend errors |

---

# Cell Selection

Each selected cell is stored as

```
row-column
```

Example

```
12-3
```

representing

```
Row 12
Column 3
```

A JavaScript Set is used to efficiently

- Add cells
- Remove cells
- Check selections

---

# Pagination

The table loads

```
25 rows per page
```

Navigation includes

- Previous page
- Next page
- Current row range
- Total rows

---

# Error Handling

The frontend gracefully handles

- Upload failures
- Invalid CSV files
- Network errors
- Backend errors
- Empty datasets

Errors are displayed directly to the user.

---

# User Interface

The interface consists of

```
Header
 ├── Application Title
 └── CSV Upload

Workspace
 ├── Data Table
 └── Summary Panel

```


# License

Academic / Research Use

Developed during an industrial internship project on fine-tuning Small Language Models (SLMs) for table-to-text generation.