import type { Shape } from "../../api/types";
import type { CSSProperties } from "react";

interface Props {
  shape: Shape;
  style: CSSProperties;
}

export default function PictureRenderer({ shape, style }: Props) {
  if (!shape.media_url) return <div style={style} />;

  const hasCrop =
    shape.crop &&
    (shape.crop.left || shape.crop.top || shape.crop.right || shape.crop.bottom);

  if (hasCrop) {
    // Crop via overflow:hidden container
    return (
      <div style={{ ...style, overflow: "hidden" }}>
        <img
          src={shape.media_url}
          alt={shape.name ?? ""}
          style={{
            display: "block",
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      </div>
    );
  }

  return (
    <div style={style}>
      <img
        src={shape.media_url}
        alt={shape.name ?? ""}
        style={{ width: "100%", height: "100%", objectFit: "fill", display: "block" }}
      />
    </div>
  );
}
