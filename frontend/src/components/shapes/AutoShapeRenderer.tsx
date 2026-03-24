import type { Shape } from "../../api/types";
import { emuToPx } from "../../utils/emu";
import { getGeometryPath, isEllipse } from "../../utils/geometry";
import ParagraphRenderer from "../text/ParagraphRenderer";
import type { CSSProperties } from "react";

interface Props {
  shape: Shape;
  style: CSSProperties;
}

export default function AutoShapeRenderer({ shape, style }: Props) {
  const w = emuToPx(shape.width);
  const h = emuToPx(shape.height);
  const tf = shape.text_frame;

  const fillColor = shape.fill?.color ?? "transparent";
  const fillOpacity = shape.fill?.opacity ?? 1;
  const lineColor = shape.line?.color ?? "none";
  const lineWidth = shape.line?.width ? emuToPx(shape.line.width) : 0;

  const hasGradient =
    shape.fill?.type === "gradient" &&
    shape.fill.details?.stops &&
    shape.fill.details.stops.length > 0;

  // Ellipse: use CSS border-radius
  if (isEllipse(shape.preset_geometry)) {
    const shapeStyle: CSSProperties = {
      ...style,
      borderRadius: "50%",
      opacity: fillOpacity,
      border: lineWidth > 0 ? `${Math.max(lineWidth, 0.5)}px solid ${lineColor}` : undefined,
    };

    if (hasGradient) {
      const stops = shape.fill!.details!.stops
        .map((s) => `${s.color ?? "#fff"} ${s.position * 100}%`)
        .join(", ");
      shapeStyle.background = `linear-gradient(180deg, ${stops})`;
    } else if (shape.fill?.type === "solid") {
      shapeStyle.backgroundColor = fillColor;
    }

    return (
      <div style={shapeStyle}>
        {tf && (
          <div style={{
            width: "100%", height: "100%",
            display: "flex", flexDirection: "column",
            justifyContent: tf.vertical_anchor === "MIDDLE" ? "center" :
              tf.vertical_anchor === "BOTTOM" ? "flex-end" : "flex-start",
            padding: `${emuToPx(tf.margin_top ?? 0)}px ${emuToPx(tf.margin_right ?? 0)}px ${emuToPx(tf.margin_bottom ?? 0)}px ${emuToPx(tf.margin_left ?? 0)}px`,
            boxSizing: "border-box",
            overflow: "hidden",
          }}>
            {tf.paragraphs.map((p, i) => <ParagraphRenderer key={i} paragraph={p} />)}
          </div>
        )}
      </div>
    );
  }

  // SVG path-based shape
  const path = getGeometryPath(shape.preset_geometry);
  const gradientId = `grad-${shape.id}`;
  const svgFill = hasGradient
    ? `url(#${gradientId})`
    : shape.fill?.type === "solid"
      ? fillColor
      : "transparent";

  return (
    <div style={style}>
      <svg
        viewBox={`0 0 ${w} ${h}`}
        width={w}
        height={h}
        style={{ position: "absolute", top: 0, left: 0 }}
      >
        {hasGradient && (
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              {shape.fill!.details!.stops.map((s, i) => (
                <stop
                  key={i}
                  offset={`${s.position * 100}%`}
                  stopColor={s.color ?? "#fff"}
                />
              ))}
            </linearGradient>
          </defs>
        )}
        {path ? (
          <path
            d={scalePath(path, w, h)}
            fill={svgFill}
            fillOpacity={fillOpacity}
            stroke={lineColor}
            strokeWidth={Math.max(lineWidth, 0)}
          />
        ) : (
          <rect
            x={lineWidth / 2} y={lineWidth / 2}
            width={w - lineWidth} height={h - lineWidth}
            fill={svgFill}
            fillOpacity={fillOpacity}
            stroke={lineColor}
            strokeWidth={lineWidth}
          />
        )}
      </svg>
      {tf && (
        <div style={{
          position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
          display: "flex", flexDirection: "column",
          justifyContent: tf.vertical_anchor === "MIDDLE" ? "center" :
            tf.vertical_anchor === "BOTTOM" ? "flex-end" : "flex-start",
          padding: `${emuToPx(tf.margin_top ?? 0)}px ${emuToPx(tf.margin_right ?? 0)}px ${emuToPx(tf.margin_bottom ?? 0)}px ${emuToPx(tf.margin_left ?? 0)}px`,
          boxSizing: "border-box",
          overflow: "hidden",
        }}>
          {tf.paragraphs.map((p, i) => <ParagraphRenderer key={i} paragraph={p} />)}
        </div>
      )}
    </div>
  );
}

/** Scale a normalized (0-1) SVG path to actual pixel dimensions. */
function scalePath(pathData: string, w: number, h: number): string {
  return pathData.replace(/([0-9]*\.?[0-9]+)/g, (match, _num, offset, str) => {
    const val = parseFloat(match);
    // Determine if this is an X or Y coordinate by counting preceding commas/spaces
    const before = str.substring(0, offset);
    const isY = isYCoordinate(before);
    return String(Math.round((isY ? val * h : val * w) * 100) / 100);
  });
}

function isYCoordinate(before: string): boolean {
  // In SVG path, after a command letter, odd-indexed numbers are Y
  let count = 0;
  for (let i = before.length - 1; i >= 0; i--) {
    const c = before[i];
    if (c === "," || c === " ") count++;
    else if (/[A-Za-z]/.test(c)) break;
  }
  return count % 2 === 1;
}
