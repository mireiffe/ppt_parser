import { useState, useEffect, useCallback } from "react";
import { api } from "../api/client";
import type { PresentationDetail, SlideData } from "../api/types";
import SlideCanvas from "./SlideCanvas";
import SlideNavigator from "./SlideNavigator";

interface Props {
  presentation: PresentationDetail;
  onBack: () => void;
}

export default function SlideViewer({ presentation, onBack }: Props) {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [slideData, setSlideData] = useState<SlideData | null>(null);
  const [loading, setLoading] = useState(false);

  const slideList = presentation.slides;
  const currentSlide = slideList[currentIdx];

  useEffect(() => {
    if (!currentSlide) return;
    setLoading(true);
    api.getSlide(currentSlide.id).then((data) => {
      setSlideData(data);
      setLoading(false);
    });
  }, [currentSlide]);

  const goPrev = useCallback(() => setCurrentIdx((i) => Math.max(0, i - 1)), []);
  const goNext = useCallback(() => setCurrentIdx((i) => Math.min(slideList.length - 1, i + 1)), [slideList.length]);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "ArrowLeft") goPrev();
      if (e.key === "ArrowRight") goNext();
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [goPrev, goNext]);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* Header */}
      <div style={{
        padding: "8px 16px",
        borderBottom: "1px solid #ddd",
        display: "flex",
        alignItems: "center",
        gap: "16px",
        background: "#fafafa",
      }}>
        <button onClick={onBack} style={{ cursor: "pointer" }}>&larr; Back</button>
        <strong>{presentation.filename}</strong>
        <span style={{ color: "#888" }}>
          Slide {currentIdx + 1} / {slideList.length}
        </span>
        <div style={{ marginLeft: "auto", display: "flex", gap: "8px" }}>
          <button onClick={goPrev} disabled={currentIdx === 0}>&larr; Prev</button>
          <button onClick={goNext} disabled={currentIdx === slideList.length - 1}>Next &rarr;</button>
        </div>
      </div>

      {/* Body */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <SlideNavigator
          slides={slideList}
          currentSlideIdx={currentIdx}
          onSelect={setCurrentIdx}
        />
        {loading ? (
          <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
            Loading...
          </div>
        ) : slideData ? (
          <SlideCanvas slide={slideData} />
        ) : null}
      </div>
    </div>
  );
}
