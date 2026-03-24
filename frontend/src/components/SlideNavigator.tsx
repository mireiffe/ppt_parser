import type { SlideSummary } from "../api/types";

interface Props {
  slides: SlideSummary[];
  currentSlideIdx: number;
  onSelect: (idx: number) => void;
}

export default function SlideNavigator({ slides, currentSlideIdx, onSelect }: Props) {
  return (
    <div style={{
      width: "160px",
      borderRight: "1px solid #ddd",
      overflowY: "auto",
      background: "#f5f5f5",
      flexShrink: 0,
    }}>
      {slides.map((s, idx) => (
        <div
          key={s.id}
          onClick={() => onSelect(idx)}
          style={{
            padding: "8px 12px",
            cursor: "pointer",
            borderBottom: "1px solid #e0e0e0",
            backgroundColor: idx === currentSlideIdx ? "#d0d0f0" : undefined,
            fontSize: "13px",
          }}
        >
          <strong>Slide {s.slide_number}</strong>
          {s.name && <div style={{ fontSize: "11px", color: "#666" }}>{s.name}</div>}
        </div>
      ))}
    </div>
  );
}
