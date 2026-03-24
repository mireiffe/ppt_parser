import type { Shape } from "../../api/types";
import { emuToPx, lineWidthToPx } from "../../utils/emu";
import type { CSSProperties } from "react";

interface Props {
  shape: Shape;
  style: CSSProperties;
}

export default function ConnectorRenderer({ shape, style }: Props) {
  const x1 = shape.begin_x != null ? emuToPx(shape.begin_x) : 0;
  const y1 = shape.begin_y != null ? emuToPx(shape.begin_y) : 0;
  const x2 = shape.end_x != null ? emuToPx(shape.end_x) : emuToPx(shape.width);
  const y2 = shape.end_y != null ? emuToPx(shape.end_y) : emuToPx(shape.height);

  const lineColor = shape.line?.color ?? "#000000";
  const lineWidth = shape.line?.width ? lineWidthToPx(shape.line.width) : 1;

  // Calculate SVG viewport from connector endpoints
  const minX = Math.min(x1, x2);
  const minY = Math.min(y1, y2);
  const w = Math.abs(x2 - x1) || 1;
  const h = Math.abs(y2 - y1) || 1;

  const connectorStyle: CSSProperties = {
    ...style,
    // Override position to use connector's actual bounds
    left: `${minX}px`,
    top: `${minY}px`,
    width: `${w + lineWidth}px`,
    height: `${h + lineWidth}px`,
  };

  return (
    <div style={connectorStyle}>
      <svg width="100%" height="100%" style={{ overflow: "visible" }}>
        <line
          x1={x1 - minX + lineWidth / 2}
          y1={y1 - minY + lineWidth / 2}
          x2={x2 - minX + lineWidth / 2}
          y2={y2 - minY + lineWidth / 2}
          stroke={lineColor}
          strokeWidth={lineWidth}
          strokeDasharray={shape.line?.dash_style === "DASH" ? "8,4" :
            shape.line?.dash_style === "DOT" ? "2,4" : undefined}
        />
      </svg>
    </div>
  );
}
