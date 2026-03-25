import type { Shape } from "../../api/types";
import { emuToPx } from "../../utils/emu";
import AutoShapeRenderer from "./AutoShapeRenderer";
import TextBoxRenderer from "./TextBoxRenderer";
import PictureRenderer from "./PictureRenderer";
import TableRenderer from "./TableRenderer";
import GroupRenderer from "./GroupRenderer";
import ConnectorRenderer from "./ConnectorRenderer";
import ChartRenderer from "./ChartRenderer";
import type { CSSProperties } from "react";

interface Props {
  shape: Shape;
}

export default function ShapeRenderer({ shape }: Props) {
  const style: CSSProperties = {
    position: "absolute",
    left: `${emuToPx(shape.pos_x)}px`,
    top: `${emuToPx(shape.pos_y)}px`,
    width: `${emuToPx(shape.width)}px`,
    height: `${emuToPx(shape.height)}px`,
    zIndex: shape.z_order,
  };

  // Rotation
  const transforms: string[] = [];
  if (shape.rotation) transforms.push(`rotate(${shape.rotation}deg)`);
  if (shape.flip_h) transforms.push("scaleX(-1)");
  if (shape.flip_v) transforms.push("scaleY(-1)");
  if (transforms.length > 0) {
    style.transform = transforms.join(" ");
  }

  switch (shape.shape_type) {
    case "textbox":
      return <TextBoxRenderer shape={shape} style={style} />;
    case "shape":
    case "freeform":
      return <AutoShapeRenderer shape={shape} style={style} />;
    case "picture":
      return <PictureRenderer shape={shape} style={style} />;
    case "chart":
      return <ChartRenderer shape={shape} style={style} />;
    case "table":
      return <TableRenderer shape={shape} style={style} />;
    case "group":
      return <GroupRenderer shape={shape} style={style} />;
    case "connector":
      return <ConnectorRenderer shape={shape} style={style} />;
    default:
      return <div style={style} />;
  }
}
