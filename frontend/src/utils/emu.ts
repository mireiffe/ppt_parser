/** EMU (English Metric Units) conversion utilities.
 * 1 inch = 914400 EMU, screen = 96 DPI → 1 px = 9525 EMU
 */
const EMU_PER_PX = 9525;

export function emuToPx(emu: number): number {
  return emu / EMU_PER_PX;
}

/** Convert centi-points to CSS pt. 1800 centi-points = 18pt */
export function centiPtToPt(cp: number): number {
  return cp / 100;
}

/** Convert EMU line width to px (minimum 1px for visible lines) */
export function lineWidthToPx(emu: number): number {
  const px = emu / EMU_PER_PX;
  return Math.max(px, 0.5);
}
