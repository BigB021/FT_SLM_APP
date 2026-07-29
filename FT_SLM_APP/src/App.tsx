import { useState } from 'react';
import { PiBrainBold } from "react-icons/pi";
import FileUpload from './components/FileUpload';
import DataTable from './components/Datatable';
import SummaryPanel from './components/Summarypanel';
import { summarize } from './api/api';
import type { UploadResponse, HighlightedCell, SummarizeResponse } from './api/api';


export default function App() {
  const [upload, setUpload] = useState<UploadResponse | null>(null);
  const [highlighted, setHighlighted] = useState<Set<string>>(new Set());
  const [summaryResult, setSummaryResult] = useState<SummarizeResponse | null>(null);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [summarizeError, setSummarizeError] = useState<string | null>(null);

  function handleUploaded(result: UploadResponse) {
    setUpload(result);
    setHighlighted(new Set());
    setSummaryResult(null);
    setSummarizeError(null);
  }

  function toggleCell(row: number, col: number) {
    const key = `${row}-${col}`;
    setHighlighted((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
    setSummaryResult(null);
  }

  function clearHighlights() {
    setHighlighted(new Set());
    setSummaryResult(null);
    setSummarizeError(null);
  }

  async function handleSummarize() {
    if (!upload || highlighted.size === 0) return;

    setIsSummarizing(true);
    setSummarizeError(null);
    try {
      const cells: HighlightedCell[] = Array.from(highlighted).map((key) => {
        const [row, col] = key.split('-').map(Number);
        return [row, col];
      });

      const result = await summarize({
        uploadId: upload.upload_id,
        highlightedCells: cells,
      });
      setSummaryResult(result);
    } catch (err) {
      setSummarizeError(err instanceof Error ? err.message : 'Summarize failed.');
    } finally {
      setIsSummarizing(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header__title">
          {/* <span className="app-header__mark" aria-hidden="true"></span> */}
          <PiBrainBold size={30}/>
          <div>
            <h1>Fine Tuned Flan T5 Model</h1>
            <p>LoRA fine tuned model to summarize csv tables.</p>
          </div>
        </div>
        <FileUpload onUploaded={handleUploaded} />
      </header>

      {upload && (
        <main className="workspace">
          <section className="workspace__table">
            <div className="workspace__table-meta">
              <span>{upload.filename}</span>
              <span className="dot">·</span>
              <span>{upload.total_rows} rows</span>
              <span className="dot">·</span>
              <span>{upload.columns.length} columns</span>
            </div>
            <DataTable upload={upload} highlighted={highlighted} onToggleCell={toggleCell} />
          </section>

          <SummaryPanel
            selectedCount={highlighted.size}
            onSummarize={handleSummarize}
            onClear={clearHighlights}
            isSummarizing={isSummarizing}
            result={summaryResult}
            error={summarizeError}
          />
        </main>
      )}

      {!upload && (
        <div className="empty-state">
          <p>No file yet. Choose a CSV above to start marking cells.</p>
        </div>
      )}
    </div>
  );
}