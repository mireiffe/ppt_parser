/** SVG path data for common MSO_SHAPE preset geometries.
 * Paths are defined in a 1x1 viewBox — scale to shape dimensions.
 */

const GEOMETRY_PATHS: Record<string, string> = {
  // Rectangles
  RECTANGLE: "M0,0 L1,0 L1,1 L0,1 Z",
  ROUNDED_RECTANGLE: "M0.1,0 L0.9,0 Q1,0 1,0.1 L1,0.9 Q1,1 0.9,1 L0.1,1 Q0,1 0,0.9 L0,0.1 Q0,0 0.1,0 Z",

  // Basic shapes
  ELLIPSE: "", // Use CSS border-radius instead
  TRIANGLE: "M0.5,0 L1,1 L0,1 Z",
  RIGHT_TRIANGLE: "M0,0 L1,1 L0,1 Z",
  DIAMOND: "M0.5,0 L1,0.5 L0.5,1 L0,0.5 Z",
  PARALLELOGRAM: "M0.2,0 L1,0 L0.8,1 L0,1 Z",
  TRAPEZOID: "M0.2,0 L0.8,0 L1,1 L0,1 Z",
  PENTAGON: "M0.5,0 L1,0.38 L0.81,1 L0.19,1 L0,0.38 Z",
  HEXAGON: "M0.25,0 L0.75,0 L1,0.5 L0.75,1 L0.25,1 L0,0.5 Z",
  OCTAGON: "M0.29,0 L0.71,0 L1,0.29 L1,0.71 L0.71,1 L0.29,1 L0,0.71 L0,0.29 Z",

  // Arrows
  RIGHT_ARROW: "M0,0.2 L0.7,0.2 L0.7,0 L1,0.5 L0.7,1 L0.7,0.8 L0,0.8 Z",
  LEFT_ARROW: "M0,0.5 L0.3,0 L0.3,0.2 L1,0.2 L1,0.8 L0.3,0.8 L0.3,1 Z",
  UP_ARROW: "M0.5,0 L1,0.3 L0.8,0.3 L0.8,1 L0.2,1 L0.2,0.3 L0,0.3 Z",
  DOWN_ARROW: "M0.2,0 L0.8,0 L0.8,0.7 L1,0.7 L0.5,1 L0,0.7 L0.2,0.7 Z",

  // Stars
  STAR_5_POINT: "M0.5,0 L0.62,0.38 L1,0.38 L0.69,0.62 L0.81,1 L0.5,0.76 L0.19,1 L0.31,0.62 L0,0.38 L0.38,0.38 Z",

  // Callouts
  ROUNDED_RECTANGULAR_CALLOUT: "M0.1,0 L0.9,0 Q1,0 1,0.1 L1,0.7 Q1,0.8 0.9,0.8 L0.4,0.8 L0.2,1 L0.3,0.8 L0.1,0.8 Q0,0.8 0,0.7 L0,0.1 Q0,0 0.1,0 Z",

  // Plus/Cross
  CROSS: "M0.35,0 L0.65,0 L0.65,0.35 L1,0.35 L1,0.65 L0.65,0.65 L0.65,1 L0.35,1 L0.35,0.65 L0,0.65 L0,0.35 L0.35,0.35 Z",

  // Chevron
  CHEVRON: "M0,0 L0.8,0 L1,0.5 L0.8,1 L0,1 L0.2,0.5 Z",
};

export function getGeometryPath(presetName: string | null): string | null {
  if (!presetName) return GEOMETRY_PATHS.RECTANGLE;
  return GEOMETRY_PATHS[presetName] ?? null;
}

export function isEllipse(presetName: string | null): boolean {
  return presetName === "ELLIPSE" || presetName === "OVAL";
}
