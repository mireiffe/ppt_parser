import type { Shape } from "../../api/types";
import { emuToPx } from "../../utils/emu";
import ParagraphRenderer from "../text/ParagraphRenderer";
import type { CSSProperties } from "react";

interface Props {
  shape: Shape;
  style: CSSProperties;
}

export default function TextBoxRenderer({ shape, style }: Props) {
  const tf = shape.text_frame;
  if (!tf) return <div style={style} />;

  const innerStyle: CSSProperties = {
    width: "100%",
    height: "100%",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
    boxSizing: "border-box",
  };

  // Text frame margins
  if (tf.margin_left) innerStyle.paddingLeft = `${emuToPx(tf.margin_left)}px`;
  if (tf.margin_right) innerStyle.paddingRight = `${emuToPx(tf.margin_right)}px`;
  if (tf.margin_top) innerStyle.paddingTop = `${emuToPx(tf.margin_top)}px`;
  if (tf.margin_bottom) innerStyle.paddingBottom = `${emuToPx(tf.margin_bottom)}px`;

  // Vertical anchor
  if (tf.vertical_anchor === "MIDDLE") {
    innerStyle.justifyContent = "center";
  } else if (tf.vertical_anchor === "BOTTOM") {
    innerStyle.justifyContent = "flex-end";
  }

  // Text direction
  if (tf.text_direction === "VERTICAL" || tf.text_direction === "VERTICAL_270") {
    innerStyle.writingMode = "vertical-rl";
  }

  if (!tf.word_wrap) {
    innerStyle.whiteSpace = "nowrap";
  }

  return (
    <div style={style}>
      <div style={innerStyle}>
        {tf.paragraphs.map((p, i) => (
          <ParagraphRenderer key={i} paragraph={p} />
        ))}
      </div>
    </div>
  );
}
