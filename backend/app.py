# Author : Youssef Aitbouddroub

import io
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

import model 
from utils import dataframe_to_tab_string

app = Flask(__name__)
CORS(app)

UPLOADS = {}
PAGE_SIZE_DEFAULT = 25

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/api/upload",methods=["POST"])
def upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Expected a 'file' field."}),400

    file = request.files["file"]

    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only .csv files are supported."}),400

    try:
        df = pd.read_csv(io.BytesIO(file.read()))
    except Exception as e:
        return jsonify({"error": f"Could not parse CSV: {e}"}), 400

    if df.empty or len(df.columns) == 0:
        return jsonify({"error": "The uploaded CSV appears to be empty."}), 400
    
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all").reset_index(drop=True)

    upload_id = str(uuid.uuid4())
    UPLOADS[upload_id] = df
 
    return jsonify({
        "upload_id": upload_id,
        "filename": file.filename,
        "columns": list(df.columns),
        "total_rows": len(df),
    })


@app.route("/api/rows", methods=["GET"])
def get_rows():
    upload_id = request.args.get("upload_id")
    start = int(request.args.get("start", 0))
    limit = int(request.args.get("limit", PAGE_SIZE_DEFAULT))
    filter_col = request.args.get("filter_col")
    filter_val = request.args.get("filter_val")
 
    if upload_id not in UPLOADS:
        return jsonify({"error": "Unknown upload_id. Please re-upload the CSV."}), 404
 
    df = UPLOADS[upload_id]
 
    if filter_col and filter_val is not None:
        if filter_col not in df.columns:
            return jsonify({"error": f"Unknown column '{filter_col}'."}), 400
        mask = df[filter_col].astype(str).str.contains(filter_val, case=False, na=False)
        filtered_df = df[mask]
    else:
        filtered_df = df
 
    page = filtered_df.iloc[start:start + limit].fillna("")
    rows = [
        {"index": int(idx), "values": [str(v) for v in row_values]}
        for idx, row_values in zip(page.index, page.itertuples(index=False, name=None))
    ]
 
    return jsonify({
        "rows": rows,
        "total_filtered": len(filtered_df),
        "total_rows": len(df),
    })

@app.route("/api/summarize",methods=["POST"])
def summarize():
    data = request.get_json(force=True)

    upload_id = data.get("upload_id")
    highlighted_cells = data.get("highlighted_cells", [])
    page_title = data.get("page_title", "")
    section_title = data.get("section_title", "")
    section_text = data.get("section_text", "")

    if upload_id not in UPLOADS:
        return jsonify({"error": "Unknown upload_id. Please re-upload the CSV."}), 404
    if not highlighted_cells:
        return jsonify({"error": "Select at least one cell to highlight."}), 400
    df = UPLOADS[upload_id]
    n_data_rows, n_cols = len(df), len(df.columns)
    
    resolved_cells = []
    for r, c in highlighted_cells:
        if not (0 <= r < n_data_rows) or not (0 <= c < n_cols):
            return jsonify({
                "error": f"Highlighted cell (row {r}, col {c}) is out of range "
                         f"for a table with {n_data_rows} data rows and {n_cols} columns."
            }), 400
        resolved_cells.append([r + 1, c])
    table_str = dataframe_to_tab_string(df)
    sample = {
        "table": table_str,
        "table_page_title": page_title,
        "table_section_title": section_title,
        "table_section_text": section_text,
        "highlighted_cells": resolved_cells,
    }

    prompt = model.build_prompt(sample)
    ft_model, tokenizer = model.load_fine_tuned_model()
    summary = model.generate_summary(ft_model, tokenizer, prompt)
    return jsonify({"summary": summary, "prompt": prompt})

if __name__ == "__main__":
    print("Loading model at startup...")
    model.load_fine_tuned_model()
    app.run(host="0.0.0.0", port=5000, debug=False)

