import type { Shape } from "../../api/types";
import { emuToPx } from "../../utils/emu";
import ShapeRenderer from "./ShapeRenderer";
import type { CSSProperties } from "react";

interface Props {
  shape: Shape;
  style: CSSProperties;
}

export default function GroupRenderer({ shape, style }: Props) {
  if (!shape.children) return <div style={style} />;

  const gt = shape.group_transform;
  const innerStyle: CSSProperties = {
    position: "relative",
    width: "100%",
    height: "100%",
  };

  // If group has child coordinate transform, apply scaling
  if (gt?.ch_ext_cx && gt?.ch_ext_cy && shape.width && shape.height) {
    const scaleX = emuToPx(shape.width) / emuToPx(gt.ch_ext_cx);
    const scaleY = emuToPx(shape.height) / emuToPx(gt.ch_ext_cy);
    if (scaleX !== 1 || scaleY !== 1) {
      innerStyle.transform = `scale(${scaleX}, ${scaleY})`;
      innerStyle.transformOrigin = "0 0";
    }
  }

  return (
    <div style={style}>
      <div style={innerStyle}>
        {shape.children.map((child) => {
          // Offset child position by group's chOff
          const offsetX = gt?.ch_off_x ?? 0;
          const offsetY = gt?.ch_off_y ?? 0;
          const adjustedChild = {
            ...child,
            pos_x: child.pos_x - offsetX,
            pos_y: child.pos_y - offsetY,
          };
          return <ShapeRenderer key={child.id} shape={adjustedChild} />;
        })}
      </div>
    </div>
  );
}
