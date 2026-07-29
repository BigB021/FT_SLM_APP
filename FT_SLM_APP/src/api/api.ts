// Author: Youssef Aitbouddroub
const API_BASE = "http://localhost:5000/api";

export interface UploadResponse {
  upload_id: string;
  filename: string;
  columns: string[];
  total_rows: number;
}

export interface RowData {
  index: number; // absolute row index into the stored DataFrame
  values: string[];
}

export interface RowsResponse {
  rows: RowData[];
  total_filtered: number;
  total_rows: number;
}

export type HighlightedCell = [row: number, col: number];

export interface SummarizeRequest {
  uploadId: string;
  highlightedCells: HighlightedCell[];
  pageTitle?: string;
  sectionTitle?: string;
  sectionText?: string;
}

export interface SummarizeResponse {
  summary: string;
  prompt: string;
}

interface FetchRowsParams {
  uploadId: string;
  start?: number;
  limit?: number;
  filterCol?: string;
  filterVal?: string;
}

interface ApiErrorBody {
  error?: string;
}

async function handleResponse<T>(res: Response): Promise<T> {
  const data = (await res.json()) as T & ApiErrorBody;
  if (!res.ok) {
    throw new Error(data.error || `Request failed (${res.status})`);
  }
  return data;
}

export async function uploadCsv(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<UploadResponse>(res);
}

export async function fetchRows({
  uploadId,
  start = 0,
  limit = 25,
  filterCol,
  filterVal,
}: FetchRowsParams): Promise<RowsResponse> {
  const params = new URLSearchParams({
    upload_id: uploadId,
    start: String(start),
    limit: String(limit),
  });
  if (filterCol && filterVal) {
    params.set("filter_col", filterCol);
    params.set("filter_val", filterVal);
  }

  const res = await fetch(`${API_BASE}/rows?${params.toString()}`);
  return handleResponse<RowsResponse>(res);
}

export async function summarize({
  uploadId,
  highlightedCells,
  pageTitle,
  sectionTitle,
  sectionText,
}: SummarizeRequest): Promise<SummarizeResponse> {
  const res = await fetch(`${API_BASE}/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      upload_id: uploadId,
      highlighted_cells: highlightedCells,
      page_title: pageTitle ?? "",
      section_title: sectionTitle ?? "",
      section_text: sectionText ?? "",
    }),
  });
  return handleResponse<SummarizeResponse>(res);
}