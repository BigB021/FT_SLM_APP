import { useState } from 'react';
import type { ChangeEvent } from 'react';
import { uploadCsv } from "../api/api";
import type {UploadResponse} from "../api/api";

interface FileUploadProps {
  onUploaded: (result: UploadResponse) => void;
}

export default function FileUpload({ onUploaded }: FileUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);
    try {
      const result = await uploadCsv(file);
      onUploaded(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setIsUploading(false);
      e.target.value = ""; // allow re-selecting the same file
    }
  }

  return (
    <div className="file-upload">
      <label className="file-upload__label">
        {isUploading ? "Uploading..." : "Choose a CSV file"}
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          disabled={isUploading}
          style={{ display: "none" }}
        />
      </label>
      {error && <p className="file-upload__error">{error}</p>}
    </div>
  );
}