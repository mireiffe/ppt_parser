import React from "react";
import type { Shape, Line } from "../../api/types";
import { emuToPx, lineWidthToPx } from "../../utils/emu";
import type { CSSProperties } from "react";

interface Props {
  shape: Shape;
  style: CSSProperties;
}

function dashArray(dashStyle: string | null | undefined, lineWidth: number): string | undefined {
  const w = Math.max(lineWidth, 1);
  switch (dashStyle) {
    case "DASH": return `${w * 4},${w * 3}`;
    case "DOT": return `${w},${w * 2}`;
    case "DASH_DOT": return `${w * 4},${w * 2},${w},${w * 2}`;
    case "LONG_DASH": return `${w * 8},${w * 3}`;
    case "LONG_DASH_DOT": return `${w * 8},${w * 3},${w},${w * 3}`;
    case "LONG_DASH_DOT_DOT": return `${w * 8},${w * 3},${w},${w * 2},${w},${w * 3}`;
    case "ROUND_DOT": return `0.1,${w * 2}`;
    case "SQUARE_DOT": return `${w},${w * 2}`;
    default: return undefined;
  }
}

/** Get arrow marker size multiplier */
function sizeMul(size: string | null | undefined): number {
  switch (size) {
    case "sm": return 0.5;
    case "lg": return 1.5;
    default: return 1.0;
  }
}

/** Compute marker dimensions in user-space pixels */
function markerSize(lineWidth: number, wSize: string | null | undefined, lenSize: string | null | undefined) {
  const wM = sizeMul(wSize);
  const lM = sizeMul(lenSize);
  // Arrow width and length proportional to line width, with min/max bounds
  const arrowW = Math.max(lineWidth * 2.5 * wM, 3);
  const arrowL = Math.max(lineWidth * 3 * lM, 4);
  return { arrowW, arrowL };
}

/** Generate SVG marker defs for arrow heads/tails */
function ArrowMarkers({ line, lineColor, lineWidth, id }: {
  line: Line | null;
  lineColor: string;
  lineWidth: number;
  id: string;
}) {
  if (!line) return null;
  const markers: React.ReactElement[] = [];

  const makeMarker = (type: string, wSize: string | null | undefined, lenSize: string | null | undefined, isHead: boolean) => {
    const { arrowW, arrowL } = markerSize(lineWidth, wSize, lenSize);
    const markerId = isHead ? `${id}-head` : `${id}-tail`;
    const mW = arrowL;
    const mH = arrowW * 2;
    const halfH = mH / 2;

    let el: React.ReactElement;
    let refX: number;

    switch (type) {
      case "triangle":
        refX = isHead ? 0 : mW;
        el = isHead
          ? <path d={`M${mW},${halfH} L0,0 L0,${mH} Z`} fill={lineColor} />
          : <path d={`M0,${halfH} L${mW},0 L${mW},${mH} Z`} fill={lineColor} />;
        break;
      case "stealth":
        refX = isHead ? 0 : mW;
        el = isHead
          ? <path d={`M${mW},${halfH} L0,0 L${mW * 0.3},${halfH} L0,${mH} Z`} fill={lineColor} />
          : <path d={`M0,${halfH} L${mW},0 L${mW * 0.7},${halfH} L${mW},${mH} Z`} fill={lineColor} />;
        break;
      case "arrow":
        refX = isHead ? 0 : mW;
        el = isHead
          ? <path d={`M0,0 L${mW},${halfH} L0,${mH}`} fill="none" stroke={lineColor} strokeWidth={Math.max(lineWidth * 0.6, 1)} strokeLinejoin="round" />
          : <path d={`M${mW},0 L0,${halfH} L${mW},${mH}`} fill="none" stroke={lineColor} strokeWidth={Math.max(lineWidth * 0.6, 1)} strokeLinejoin="round" />;
        break;
      case "diamond": {
        const cx = mW / 2;
        refX = cx;
        el = <path d={`M0,${halfH} L${cx},0 L${mW},${halfH} L${cx},${mH} Z`} fill={lineColor} />;
        break;
      }
      case "oval": {
        const rx = mW / 2;
        const ry = halfH;
        refX = rx;
        el = <ellipse cx={rx} cy={halfH} rx={rx} ry={ry} fill={lineColor} />;
        break;
      }
      default:
        return null;
    }

    return (
      <marker
        key={markerId}
        id={markerId}
        markerWidth={mW}
        markerHeight={mH}
        refX={refX}
        refY={halfH}
        orient="auto"
        markerUnits="userSpaceOnUse"
      >
        {el}
      </marker>
    );
  };

  if (line.head_type) {
    const m = makeMarker(line.head_type, line.head_w, line.head_len, true);
    if (m) markers.push(m);
  }
  if (line.tail_type) {
    const m = makeMarker(line.tail_type, line.tail_w, line.tail_len, false);
    if (m) markers.push(m);
  }

  if (markers.length === 0) return null;
  return <defs>{markers}</defs>;
}

export default function ConnectorRenderer({ shape, style }: Props) {
  const hasEndpoints = shape.begin_x != null && shape.begin_y != null
    && shape.end_x != null && shape.end_y != null;

  const lineColor = shape.line?.color ?? "#000000";
  const lineWidth = shape.line?.width ? lineWidthToPx(shape.line.width) : 1;
  const markerId = `conn-${shape.id}`;
  const hasHead = !!shape.line?.head_type;
  const hasTail = !!shape.line?.tail_type;
  const da = dashArray(shape.line?.dash_style, lineWidth);
  const lineCap = shape.line?.dash_style === "ROUND_DOT" ? "round" : "butt";

  if (hasEndpoints) {
    const x1 = emuToPx(shape.begin_x!);
    const y1 = emuToPx(shape.begin_y!);
    const x2 = emuToPx(shape.end_x!);
    const y2 = emuToPx(shape.end_y!);

    const minX = Math.min(x1, x2);
    const minY = Math.min(y1, y2);
    const w = Math.abs(x2 - x1) || 1;
    const h = Math.abs(y2 - y1) || 1;

    const pad = Math.max(lineWidth * 4, 10);
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
          <ArrowMarkers line={shape.line} lineColor={lineColor} lineWidth={lineWidth} id={markerId} />
          <line
            x1={x1 - minX + pad}
            y1={y1 - minY + pad}
            x2={x2 - minX + pad}
            y2={y2 - minY + pad}
            stroke={lineColor}
            strokeWidth={lineWidth}
            strokeLinecap={lineCap}
            strokeDasharray={da}
            markerStart={hasHead ? `url(#${markerId}-head)` : undefined}
            markerEnd={hasTail ? `url(#${markerId}-tail)` : undefined}
          />
        </svg>
      </div>
    );
  }

  // Fallback: use pos_x/pos_y + width/height
  const w = emuToPx(shape.width) || 1;
  const h = emuToPx(shape.height) || 1;

  let lx1 = 0, ly1 = 0, lx2 = w, ly2 = h;
  if (shape.flip_v) { ly1 = h; ly2 = 0; }
  if (shape.flip_h) { lx1 = w; lx2 = 0; }
  if (h <= 1) { ly1 = lineWidth / 2; ly2 = lineWidth / 2; }
  if (w <= 1) { lx1 = lineWidth / 2; lx2 = lineWidth / 2; }

  const pad = Math.max(lineWidth * 4, 10);
  const svgW = w + pad * 2;
  const svgH = (h <= 1 ? lineWidth + pad * 2 : h + pad * 2);

  const connectorStyle: CSSProperties = {
    ...style,
    pointerEvents: "none",
    transform: undefined,
    width: `${svgW}px`,
    height: `${svgH}px`,
    left: `${emuToPx(shape.pos_x) - pad}px`,
    top: `${emuToPx(shape.pos_y) - (h <= 1 ? pad : 0)}px`,
  };

  return (
    <div style={connectorStyle}>
      <svg width={svgW} height={svgH} style={{ overflow: "visible" }}>
        <ArrowMarkers line={shape.line} lineColor={lineColor} lineWidth={lineWidth} id={markerId} />
        <line
          x1={lx1 + pad}
          y1={ly1 + (h <= 1 ? pad : 0)}
          x2={lx2 + pad}
          y2={ly2 + (h <= 1 ? pad : 0)}
          stroke={lineColor}
          strokeWidth={lineWidth}
          strokeLinecap={lineCap}
          strokeDasharray={da}
          markerStart={hasHead ? `url(#${markerId}-head)` : undefined}
          markerEnd={hasTail ? `url(#${markerId}-tail)` : undefined}
        />
      </svg>
    </div>
  );
}
