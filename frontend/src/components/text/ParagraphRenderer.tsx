import type { Paragraph } from "../../api/types";
import { emuToPx } from "../../utils/emu";
import RunRenderer from "./RunRenderer";
import type { CSSProperties } from "react";

interface Props {
  paragraph: Paragraph;
}

export default function ParagraphRenderer({ paragraph }: Props) {
  const style: CSSProperties = {};

  if (paragraph.alignment) {
    const alignMap: Record<string, string> = {
      LEFT: "left",
      CENTER: "center",
      RIGHT: "right",
      JUSTIFY: "justify",
    };
    style.textAlign = (alignMap[paragraph.alignment] ?? "left") as CSSProperties["textAlign"];
  }

  if (paragraph.space_before)
    style.marginTop = `${emuToPx(paragraph.space_before)}px`;
  if (paragraph.space_after)
    style.marginBottom = `${emuToPx(paragraph.space_after)}px`;

  if (paragraph.line_spacing && paragraph.line_spacing_rule === "MULTIPLE") {
    style.lineHeight = paragraph.line_spacing;
  }

  if (paragraph.margin_left) {
    style.paddingLeft = `${emuToPx(paragraph.margin_left)}px`;
  }

  // Bullet
  let bullet: React.ReactNode = null;
  if (paragraph.bullet_type === "CHAR" && paragraph.bullet_char) {
    const bulletStyle: CSSProperties = {
      marginRight: "0.3em",
      color: paragraph.bullet_color ?? undefined,
    };
    bullet = <span style={bulletStyle}>{paragraph.bullet_char}</span>;
  } else if (paragraph.bullet_type === "AUTO_NUMBER") {
    bullet = <span style={{ marginRight: "0.3em" }}>{"\u2022"}</span>;
  }

  return (
    <div style={style}>
      {bullet}
      {paragraph.runs.map((run, i) => (
        <RunRenderer key={i} run={run} />
      ))}
    </div>
  );
}
