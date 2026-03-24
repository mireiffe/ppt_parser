export interface PresentationSummary {
  db_no: number;
  filename: string;
  slide_width: number;
  slide_height: number;
  slide_count: number;
}

export interface PresentationDetail extends PresentationSummary {
  theme: Theme | null;
  slides: SlideSummary[];
}

export interface Theme {
  id: number;
  clr_dk1: string | null;
  clr_lt1: string | null;
  clr_dk2: string | null;
  clr_lt2: string | null;
  clr_accent1: string | null;
  clr_accent2: string | null;
  clr_accent3: string | null;
  clr_accent4: string | null;
  clr_accent5: string | null;
  clr_accent6: string | null;
  font_major_latin: string | null;
  font_minor_latin: string | null;
  font_major_ea: string | null;
  font_minor_ea: string | null;
}

export interface SlideSummary {
  id: number;
  slide_number: number;
  name: string | null;
}

export interface SlideData {
  id: number;
  slide_number: number;
  slide_width: number;
  slide_height: number;
  background: Background;
  notes: string | null;
  shapes: Shape[];
}

export interface Background {
  fill_type: string;
  fill_color: string | null;
  fill_json: GradientData | null;
}

export interface GradientData {
  stops: { position: number; color: string | null }[];
}

export interface Fill {
  type: string;
  color: string | null;
  opacity: number | null;
  details?: GradientData;
}

export interface Line {
  color: string | null;
  width: number | null;
  dash_style: string | null;
  head_type?: string | null;
  head_w?: string | null;
  head_len?: string | null;
  tail_type?: string | null;
  tail_w?: string | null;
  tail_len?: string | null;
}

export interface Shadow {
  style: string;
  blur_radius?: number;
  distance?: number;
  direction?: number;
  color?: string;
  alpha?: number;
}

export interface TextFrame {
  word_wrap: boolean;
  auto_size: string | null;
  margin_left: number | null;
  margin_right: number | null;
  margin_top: number | null;
  margin_bottom: number | null;
  vertical_anchor: string | null;
  text_direction: string | null;
  paragraphs: Paragraph[];
}

export interface Paragraph {
  alignment: string | null;
  level: number;
  space_before: number | null;
  space_after: number | null;
  line_spacing: number | null;
  line_spacing_rule: string | null;
  bullet_type: string | null;
  bullet_char: string | null;
  bullet_color: string | null;
  indent: number | null;
  margin_left: number | null;
  runs: Run[];
}

export interface Run {
  text: string;
  font_name: string | null;
  font_size: number | null;
  font_bold: boolean | null;
  font_italic: boolean | null;
  font_underline: string | null;
  font_color: string | null;
  font_color_theme: string | null;
  is_line_break: boolean;
  hyperlink_url: string | null;
}

export interface CropData {
  left: number | null;
  top: number | null;
  right: number | null;
  bottom: number | null;
}

export interface TableData {
  num_rows: number;
  num_cols: number;
  col_widths: number[];
  row_heights: number[];
  cells: TableCell[];
}

export interface TableCell {
  row_idx: number;
  col_idx: number;
  row_span: number;
  col_span: number;
  is_merge_origin: boolean;
  fill_type: string | null;
  fill_color: string | null;
  vertical_anchor: string | null;
  margin_left: number | null;
  margin_right: number | null;
  margin_top: number | null;
  margin_bottom: number | null;
  borders: {
    left: { color: string | null; width: number | null };
    right: { color: string | null; width: number | null };
    top: { color: string | null; width: number | null };
    bottom: { color: string | null; width: number | null };
  };
  text_frame: TextFrame | null;
}

export interface GroupTransform {
  ch_off_x: number | null;
  ch_off_y: number | null;
  ch_ext_cx: number | null;
  ch_ext_cy: number | null;
}

export interface Shape {
  id: number;
  shape_type: string;
  name: string | null;
  preset_geometry: string | null;
  pos_x: number;
  pos_y: number;
  width: number;
  height: number;
  rotation: number;
  flip_h: boolean;
  flip_v: boolean;
  z_order: number;
  placeholder_type: string | null;
  fill: Fill | null;
  line: Line | null;
  shadow: Shadow | null;
  text_frame: TextFrame | null;
  table: TableData | null;
  children: Shape[] | null;
  hyperlink_url: string | null;
  media_url?: string;
  crop?: CropData;
  chart?: ChartData;
  begin_x?: number;
  begin_y?: number;
  end_x?: number;
  end_y?: number;
  group_transform?: GroupTransform;
}

export interface ChartSeries {
  name: string | null;
  values: number[];
  x_values?: number[];
  color?: string;
}

export interface ChartData {
  chart_type: string;
  title: string | null;
  categories: string[];
  series: ChartSeries[];
  legend_position?: string | null;
}
