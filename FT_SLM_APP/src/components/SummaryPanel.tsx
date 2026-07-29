import type { SummarizeResponse } from '../api/api';

interface SummaryPanelProps {
  selectedCount: number;
  onSummarize: () => void;
  onClear: () => void;
  isSummarizing: boolean;
  result: SummarizeResponse | null;
  error: string | null;
}

export default function SummaryPanel({
  selectedCount,
  onSummarize,
  onClear,
  isSummarizing,
  result,
  error,
}: SummaryPanelProps) {
  return (
    <aside className="summary-panel">
      <div className="summary-panel__status">
        <span className="summary-panel__count">{selectedCount}</span>
        <span>cell{selectedCount === 1 ? '' : 's'} marked</span>
      </div>

      <div className="summary-panel__actions">
        <button
          type="button"
          className="summary-panel__primary"
          onClick={onSummarize}
          disabled={selectedCount === 0 || isSummarizing}
        >
          {isSummarizing ? 'Reading cells…' : 'Generate summary'}
        </button>
        <button
          type="button"
          className="summary-panel__secondary"
          onClick={onClear}
          disabled={selectedCount === 0 || isSummarizing}
        >
          Clear marks
        </button>
      </div>

      {error && <p className="summary-panel__error">{error}</p>}

      {result && (
        <div className="summary-card">
          <span className="summary-card__pin" aria-hidden="true" />
          <p>{result.summary}</p>
        </div>
      )}

      {!result && !error && (
        <p className="summary-panel__hint">
          Click cells in the table to mark them, then generate a one-sentence summary of what's highlighted.
        </p>
      )}
    </aside>
  );
}