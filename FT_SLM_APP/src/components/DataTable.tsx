import { useEffect, useState } from 'react';
import { fetchRows } from '../api/api';
import type { UploadResponse, RowData } from '../api/api';

const PAGE_SIZE = 25;

interface DataTableProps {
  upload: UploadResponse;
  highlighted: Set<string>;
  onToggleCell: (row: number, col: number) => void;
}

export default function DataTable({ upload, highlighted, onToggleCell }: DataTableProps) {
  const [rows, setRows] = useState<RowData[]>([]);
  const [start, setStart] = useState(0);
  const [totalFiltered, setTotalFiltered] = useState(upload.total_rows);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset to the first page whenever a new file is uploaded.
  useEffect(() => {
    setStart(0);
  }, [upload.upload_id]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const result = await fetchRows({ uploadId: upload.upload_id, start, limit: PAGE_SIZE });
        if (!cancelled) {
          setRows(result.rows);
          setTotalFiltered(result.total_filtered);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load rows.');
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [upload.upload_id, start]);

  const pageEnd = Math.min(start + PAGE_SIZE, totalFiltered);
  const canPrev = start > 0;
  const canNext = pageEnd < totalFiltered;

  return (
    <div className="data-table">
      <div className="data-table__scroll">
        <table>
          <thead>
            <tr>
              <th className="data-table__index-col">#</th>
              {upload.columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.index}>
                <td className="data-table__index-col">{row.index}</td>
                {row.values.map((value, colIdx) => {
                  const key = `${row.index}-${colIdx}`;
                  const isHighlighted = highlighted.has(key);
                  return (
                    <td
                      key={colIdx}
                      className={isHighlighted ? 'cell cell--highlighted' : 'cell'}
                      onClick={() => onToggleCell(row.index, colIdx)}
                    >
                      <span className={isHighlighted ? 'cell__mark' : undefined}>{value}</span>
                    </td>
                  );
                })}
              </tr>
            ))}
            {!isLoading && rows.length === 0 && (
              <tr>
                <td className="data-table__empty" colSpan={upload.columns.length + 1}>
                  No rows on this page.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {error && <p className="data-table__error">{error}</p>}

      <div className="data-table__footer">
        <button
          type="button"
          onClick={() => setStart(Math.max(0, start - PAGE_SIZE))}
          disabled={!canPrev || isLoading}
        >
          ← Prev
        </button>
        <span>
          {isLoading ? 'Loading…' : `Rows ${totalFiltered === 0 ? 0 : start + 1}–${pageEnd} of ${totalFiltered}`}
        </span>
        <button type="button" onClick={() => setStart(start + PAGE_SIZE)} disabled={!canNext || isLoading}>
          Next →
        </button>
      </div>
    </div>
  );
}