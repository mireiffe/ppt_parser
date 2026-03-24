import type { Shape } from "../../api/types";
import type { CSSProperties } from "react";
import { API_BASE } from "../../api/client";

interface Props {
  shape: Shape;
  style: CSSProperties;
}

/** Prepend API_BASE to relative paths (no Vite proxy configured). */
function resolveMediaSrc(mediaUrl: string): string {
  if (mediaUrl.startsWith("http://") || mediaUrl.startsWith("https://")) {
    return mediaUrl;
  }
  return `${API_BASE}${mediaUrl}`;
}

export default function PictureRenderer({ shape, style }: Props) {
  if (!shape.media_url) return <div style={style} />;

  const src = resolveMediaSrc(shape.media_url);

  const hasCrop =
    shape.crop &&
    (shape.crop.left || shape.crop.top || shape.crop.right || shape.crop.bottom);

  if (hasCrop) {
    return (
      <div style={{ ...style, overflow: "hidden" }}>
        <img
          src={src}
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
        src={src}
        alt={shape.name ?? ""}
        style={{ width: "100%", height: "100%", objectFit: "fill", display: "block" }}
      />
    </div>
  );
}
