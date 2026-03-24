import type { Shape, TableCell } from "../../api/types";
import { emuToPx, lineWidthToPx } from "../../utils/emu";
import ParagraphRenderer from "../text/ParagraphRenderer";
import type { CSSProperties } from "react";

interface Props {
  shape: Shape;
  style: CSSProperties;
}

export default function TableRenderer({ shape, style }: Props) {
  const table = shape.table;
  if (!table) return <div style={style} />;

  const colWidths = table.col_widths.map(emuToPx);

  // Build a 2D grid of cells
  const grid: (TableCell | null)[][] = Array.from({ length: table.num_rows }, () =>
    Array(table.num_cols).fill(null)
  );
  for (const cell of table.cells) {
    grid[cell.row_idx][cell.col_idx] = cell;
  }

  return (
    <div style={style}>
      <table
        style={{
          borderCollapse: "collapse",
          width: "100%",
          height: "100%",
          tableLayout: "fixed",
        }}
      >
        <colgroup>
          {colWidths.map((w, i) => (
            <col key={i} style={{ width: `${w}px` }} />
          ))}
        </colgroup>
        <tbody>
          {Array.from({ length: table.num_rows }, (_, rowIdx) => (
            <tr key={rowIdx} style={{ height: `${emuToPx(table.row_heights[rowIdx])}px` }}>
              {Array.from({ length: table.num_cols }, (_, colIdx) => {
                const cell = grid[rowIdx][colIdx];
                if (!cell || !cell.is_merge_origin) return null;

                const cellStyle: CSSProperties = {
                  verticalAlign:
                    cell.vertical_anchor === "MIDDLE" ? "middle" :
                    cell.vertical_anchor === "BOTTOM" ? "bottom" : "top",
                  padding: `${emuToPx(cell.margin_top ?? 0)}px ${emuToPx(cell.margin_right ?? 0)}px ${emuToPx(cell.margin_bottom ?? 0)}px ${emuToPx(cell.margin_left ?? 0)}px`,
                  overflow: "hidden",
                };

                if (cell.fill_type === "solid" && cell.fill_color) {
                  cellStyle.backgroundColor = cell.fill_color;
                }

                // Borders
                if (cell.borders.top.width)
                  cellStyle.borderTop = `${lineWidthToPx(cell.borders.top.width)}px solid ${cell.borders.top.color ?? "#000"}`;
                if (cell.borders.bottom.width)
                  cellStyle.borderBottom = `${lineWidthToPx(cell.borders.bottom.width)}px solid ${cell.borders.bottom.color ?? "#000"}`;
                if (cell.borders.left.width)
                  cellStyle.borderLeft = `${lineWidthToPx(cell.borders.left.width)}px solid ${cell.borders.left.color ?? "#000"}`;
                if (cell.borders.right.width)
                  cellStyle.borderRight = `${lineWidthToPx(cell.borders.right.width)}px solid ${cell.borders.right.color ?? "#000"}`;

                return (
                  <td
                    key={colIdx}
                    rowSpan={cell.row_span > 1 ? cell.row_span : undefined}
                    colSpan={cell.col_span > 1 ? cell.col_span : undefined}
                    style={cellStyle}
                  >
                    {cell.text_frame?.paragraphs.map((p, i) => (
                      <ParagraphRenderer key={i} paragraph={p} />
                    ))}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
