import { useRef, useEffect, useState } from "react";
import type { SlideData } from "../api/types";
import { emuToPx } from "../utils/emu";
import ShapeRenderer from "./shapes/ShapeRenderer";

interface Props {
  slide: SlideData;
}

export default function SlideCanvas({ slide }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);

  const slideW = emuToPx(slide.slide_width);
  const slideH = emuToPx(slide.slide_height);

  useEffect(() => {
    function updateScale() {
      if (!containerRef.current) return;
      const cw = containerRef.current.clientWidth;
      const ch = containerRef.current.clientHeight;
      const s = Math.min(cw / slideW, ch / slideH);
      setScale(s);
    }
    updateScale();
    window.addEventListener("resize", updateScale);
    return () => window.removeEventListener("resize", updateScale);
  }, [slideW, slideH]);

  // Background
  const bgStyle: React.CSSProperties = {
    width: `${slideW}px`,
    height: `${slideH}px`,
    transform: `scale(${scale})`,
    transformOrigin: "0 0",
    position: "relative",
    overflow: "hidden",
    boxShadow: "0 2px 12px rgba(0,0,0,0.15)",
  };

  if (slide.background.fill_type === "solid" && slide.background.fill_color) {
    bgStyle.backgroundColor = slide.background.fill_color;
  } else if (slide.background.fill_type === "gradient" && slide.background.fill_json?.stops) {
    const stops = slide.background.fill_json.stops
      .map((s) => `${s.color ?? "#fff"} ${s.position * 100}%`)
      .join(", ");
    bgStyle.background = `linear-gradient(180deg, ${stops})`;
  } else {
    bgStyle.backgroundColor = "#FFFFFF";
  }

  return (
    <div
      ref={containerRef}
      style={{
        flex: 1,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
        background: "#e8e8e8",
        padding: "20px",
      }}
    >
      <div style={{ width: `${slideW * scale}px`, height: `${slideH * scale}px` }}>
        <div style={bgStyle}>
          {slide.shapes.map((shape) => (
            <ShapeRenderer key={shape.id} shape={shape} />
          ))}
        </div>
      </div>
    </div>
  );
}
