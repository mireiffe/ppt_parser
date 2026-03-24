import type { Shape } from "../../api/types";
import type { CSSProperties } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  RadialLinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar, Line, Pie, Doughnut, Scatter, Radar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  RadialLinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Filler,
  Tooltip,
  Legend
);

interface Props {
  shape: Shape;
  style: CSSProperties;
}

const PALETTE = [
  "#4472C4",
  "#ED7D31",
  "#A5A5A5",
  "#FFC000",
  "#5B9BD5",
  "#70AD47",
  "#264478",
  "#9B57A0",
  "#636363",
  "#EB6B0A",
];

function seriesColor(i: number, color?: string): string {
  return color ?? PALETTE[i % PALETTE.length];
}

function alphaColor(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function legendPosition(pos: string | null | undefined): "top" | "bottom" | "left" | "right" {
  if (pos === "top") return "top";
  if (pos === "left") return "left";
  if (pos === "right") return "right";
  return "bottom";
}

const chartInner: CSSProperties = {
  position: 'relative',
  width: '100%',
  height: '100%',
  padding: 8,
  boxSizing: 'border-box',
};

export default function ChartRenderer({ shape, style }: Props) {
  const chart = shape.chart;
  if (!chart) return <div style={style} />;

  const ct = chart.chart_type;
  const isHorizontalBar = ct.startsWith("bar_");
  const isPie = ct === "pie";
  const isDoughnut = ct === "doughnut";
  const isLine = ct.startsWith("line");
  const isArea = ct.startsWith("area");
  const isScatter = ct.startsWith("xy_scatter") || ct === "scatter";
  const isColumn = ct.startsWith("column");
  const isStacked = ct.includes("stacked");
  const isRadar = ct.startsWith("radar");
  const isWaterfall = ct.startsWith("waterfall");
  const isCombo = ct.includes("combo");

  const showLegend = chart.series.length > 1 || isPie || isDoughnut;
  const legPos = legendPosition(chart.legend_position);

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: showLegend,
        position: legPos,
        labels: { font: { size: 11 } },
      },
      title: {
        display: !!chart.title,
        text: chart.title ?? "",
        font: { size: 14 },
      },
    },
    animation: { duration: 0 },
  };

  // Pie / Doughnut
  if (isPie || isDoughnut) {
    const colors = chart.series[0]?.values.map((_, i) => seriesColor(i, chart.series[0]?.color));
    // For pie/doughnut, use palette colors per slice (not per series)
    const sliceColors = chart.series[0]?.values.map((_, i) => PALETTE[i % PALETTE.length]);
    const data = {
      labels: chart.categories,
      datasets: chart.series.map((s) => ({
        label: s.name ?? "",
        data: s.values,
        backgroundColor: sliceColors,
        borderWidth: 1,
      })),
    };
    const Comp = isDoughnut ? Doughnut : Pie;
    return (
      <div style={style}>
        <div style={chartInner}>
          <Comp data={data} options={{ ...commonOptions }} />
        </div>
      </div>
    );
  }

  // Scatter
  if (isScatter) {
    const data = {
      datasets: chart.series.map((s, i) => {
        const c = seriesColor(i, s.color);
        const xVals = s.x_values;
        return {
          label: s.name ?? `Series ${i + 1}`,
          data: s.values.map((y, j) => ({
            x: xVals && xVals[j] != null ? xVals[j] : j,
            y,
          })),
          backgroundColor: alphaColor(c, 0.6),
          borderColor: c,
          pointRadius: 4,
        };
      }),
    };
    return (
      <div style={style}>
        <div style={chartInner}>
          <Scatter data={data} options={commonOptions} />
        </div>
      </div>
    );
  }

  // Radar
  if (isRadar) {
    const data = {
      labels: chart.categories,
      datasets: chart.series.map((s, i) => {
        const c = seriesColor(i, s.color);
        return {
          label: s.name ?? `Series ${i + 1}`,
          data: s.values,
          backgroundColor: alphaColor(c, 0.2),
          borderColor: c,
          pointBackgroundColor: c,
          borderWidth: 2,
        };
      }),
    };
    return (
      <div style={style}>
        <div style={chartInner}>
          <Radar
            data={data}
            options={{
              ...commonOptions,
              scales: {
                r: { beginAtZero: true },
              },
            }}
          />
        </div>
      </div>
    );
  }

  // Line / Area
  if (isLine || isArea) {
    const data = {
      labels: chart.categories,
      datasets: chart.series.map((s, i) => {
        const c = seriesColor(i, s.color);
        return {
          label: s.name ?? `Series ${i + 1}`,
          data: s.values,
          borderColor: c,
          backgroundColor: isArea ? alphaColor(c, 0.4) : "transparent",
          fill: isArea,
          tension: 0.1,
          pointRadius: ct.includes("marker") ? 4 : 2,
        };
      }),
    };
    return (
      <div style={style}>
        <div style={chartInner}>
          <Line
            data={data}
            options={{
              ...commonOptions,
              scales: {
                x: { stacked: isStacked },
                y: { stacked: isStacked, beginAtZero: true },
              },
            }}
          />
        </div>
      </div>
    );
  }

  // Bar (horizontal) or Column (vertical) - default
  const data = {
    labels: chart.categories,
    datasets: chart.series.map((s, i) => {
      const c = seriesColor(i, s.color);
      return {
        label: s.name ?? `Series ${i + 1}`,
        data: s.values,
        backgroundColor: alphaColor(c, 0.85),
        borderColor: c,
        borderWidth: 1,
      };
    }),
  };

  return (
    <div style={style}>
      <div style={chartInner}>
        <Bar
          data={data}
          options={{
            ...commonOptions,
            indexAxis: isHorizontalBar ? ("y" as const) : ("x" as const),
            scales: {
              x: { stacked: isStacked },
              y: { stacked: isStacked, beginAtZero: true },
            },
          }}
        />
      </div>
    </div>
  );
}
