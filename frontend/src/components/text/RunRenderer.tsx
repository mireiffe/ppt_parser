import type { Run } from "../../api/types";
import { centiPtToPt } from "../../utils/emu";
import type { CSSProperties } from "react";

interface Props {
  run: Run;
}

export default function RunRenderer({ run }: Props) {
  if (run.is_line_break) return <br />;

  const style: CSSProperties = {};

  if (run.font_name) style.fontFamily = `"${run.font_name}", sans-serif`;
  if (run.font_size) style.fontSize = `${centiPtToPt(run.font_size)}pt`;
  if (run.font_bold) style.fontWeight = "bold";
  if (run.font_italic) style.fontStyle = "italic";
  if (run.font_color) style.color = run.font_color;

  if (run.font_underline && run.font_underline !== "NONE") {
    style.textDecoration = "underline";
  }

  const content = run.text || "";

  if (run.hyperlink_url) {
    return (
      <a href={run.hyperlink_url} target="_blank" rel="noopener noreferrer" style={style}>
        {content}
      </a>
    );
  }

  return <span style={style}>{content}</span>;
}
