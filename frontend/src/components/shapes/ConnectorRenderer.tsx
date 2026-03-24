import type { Shape } from "../../api/types";
import { emuToPx, lineWidthToPx } from "../../utils/emu";
import type { CSSProperties } from "react";

interface Props {
  shape: Shape;
  style: CSSProperties;
}

function dashArray(dashStyle: string | null | undefined): string | undefined {
  switch (dashStyle) {
    case "DASH": return "8,4";
    case "DOT": return "2,4";
    case "DASH_DOT": return "8,4,2,4";
    case "LONG_DASH": return "16,4";
    case "LONG_DASH_DOT": return "16,4,2,4";
    case "LONG_DASH_DOT_DOT": return "16,4,2,4,2,4";
    default: return undefined;
  }
}

export default function ConnectorRenderer({ shape, style }: Props) {
  const hasEndpoints = shape.begin_x != null && shape.begin_y != null
    && shape.end_x != null && shape.end_y != null;

  const lineColor = shape.line?.color ?? "#000000";
  const lineWidth = shape.line?.width ? lineWidthToPx(shape.line.width) : 1;

  if (hasEndpoints) {
    // Use absolute begin/end coordinates
    const x1 = emuToPx(shape.begin_x!);
    const y1 = emuToPx(shape.begin_y!);
    const x2 = emuToPx(shape.end_x!);
    const y2 = emuToPx(shape.end_y!);

    const minX = Math.min(x1, x2);
    const minY = Math.min(y1, y2);
    const w = Math.abs(x2 - x1) || 1;
    const h = Math.abs(y2 - y1) || 1;

    const pad = lineWidth;
    const svgW = w + pad * 2;
    const svgH = h + pad * 2;

    const connectorStyle: CSSProperties = {
      position: "absolute",
      left: `${minX - pad}px`,
      top: `${minY - pad}px`,
      width: `${svgW}px`,
      height: `${svgH}px`,
      zIndex: style.zIndex,
      pointerEvents: "none",
    };

    return (
      <div style={connectorStyle}>
        <svg width={svgW} height={svgH} style={{ overflow: "visible" }}>
          <line
            x1={x1 - minX + pad}
            y1={y1 - minY + pad}
            x2={x2 - minX + pad}
            y2={y2 - minY + pad}
            stroke={lineColor}
            strokeWidth={lineWidth}
            strokeLinecap="round"
            strokeDasharray={dashArray(shape.line?.dash_style)}
          />
        </svg>
      </div>
    );
  }

  // Fallback: use pos_x/pos_y + width/height to draw from one corner to another
  const w = emuToPx(shape.width) || 1;
  const h = emuToPx(shape.height) || 1;

  // Determine line direction based on shape dimensions and flip flags
  let lx1 = 0, ly1 = 0, lx2 = w, ly2 = h;
  if (shape.flip_v) { ly1 = h; ly2 = 0; }
  if (shape.flip_h) { lx1 = w; lx2 = 0; }
  // If height is ~0, it's horizontal; if width is ~0, it's vertical
  if (h <= 1) { ly1 = lineWidth / 2; ly2 = lineWidth / 2; }
  if (w <= 1) { lx1 = lineWidth / 2; lx2 = lineWidth / 2; }

  const connectorStyle: CSSProperties = {
    ...style,
    pointerEvents: "none",
    // Remove transforms - we handle flip via line direction
    transform: undefined,
  };

  return (
    <div style={connectorStyle}>
      <svg width="100%" height="100%" style={{ overflow: "visible" }}>
        <line
          x1={lx1}
          y1={ly1}
          x2={lx2}
          y2={ly2}
          stroke={lineColor}
          strokeWidth={lineWidth}
          strokeLinecap="round"
          strokeDasharray={dashArray(shape.line?.dash_style)}
        />
      </svg>
    </div>
  );
}
