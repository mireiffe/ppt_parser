import { useState, useEffect } from "react";
import { api } from "../api/client";
import type { PresentationSummary } from "../api/types";

interface Props {
  onSelect: (id: number) => void;
}

export default function PresentationList({ onSelect }: Props) {
  const [presentations, setPresentations] = useState<PresentationSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listPresentations().then((data) => {
      setPresentations(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <div style={{ padding: "40px", textAlign: "center" }}>Loading...</div>;

  return (
    <div style={{ maxWidth: "600px", margin: "40px auto", padding: "0 20px" }}>
      <h1 style={{ fontSize: "24px", marginBottom: "24px" }}>PPTX Viewer</h1>
      {presentations.length === 0 ? (
        <p style={{ color: "#888" }}>
          No presentations found. Parse a PPTX first:<br />
          <code>python -m parser.cli your_file.pptx -o output.db</code>
        </p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          {presentations.map((p) => (
            <div
              key={p.db_no}
              onClick={() => onSelect(p.db_no)}
              style={{
                padding: "16px",
                border: "1px solid #ddd",
                borderRadius: "8px",
                cursor: "pointer",
                transition: "background 0.1s",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "#f0f0ff")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "")}
            >
              <strong>{p.filename}</strong>
              <span style={{ color: "#888", marginLeft: "12px" }}>
                {p.slide_count} slides
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
