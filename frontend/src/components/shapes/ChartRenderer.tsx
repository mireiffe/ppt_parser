import type { Shape } from "../../api/types";
import type { CSSProperties } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar, Line, Pie, Doughnut, Scatter } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
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

function alphaColor(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
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

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: chart.series.length > 1 || isPie || isDoughnut,
        position: "bottom" as const,
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
    const data = {
      labels: chart.categories,
      datasets: chart.series.map((s) => ({
        label: s.name ?? "",
        data: s.values,
        backgroundColor: s.values.map((_, i) => PALETTE[i % PALETTE.length]),
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
      datasets: chart.series.map((s, i) => ({
        label: s.name ?? `Series ${i + 1}`,
        data: (s.x_values ?? s.values).map((x, j) => ({
          x: s.x_values ? x : j,
          y: s.values[j],
        })),
        backgroundColor: alphaColor(PALETTE[i % PALETTE.length], 0.6),
        borderColor: PALETTE[i % PALETTE.length],
        pointRadius: 4,
      })),
    };
    return (
      <div style={style}>
        <div style={chartInner}>
          <Scatter data={data} options={commonOptions} />
        </div>
      </div>
    );
  }

  // Line / Area
  if (isLine || isArea) {
    const data = {
      labels: chart.categories,
      datasets: chart.series.map((s, i) => ({
        label: s.name ?? `Series ${i + 1}`,
        data: s.values,
        borderColor: PALETTE[i % PALETTE.length],
        backgroundColor: isArea
          ? alphaColor(PALETTE[i % PALETTE.length], 0.4)
          : "transparent",
        fill: isArea,
        tension: 0.1,
        pointRadius: ct.includes("marker") ? 4 : 2,
      })),
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
    datasets: chart.series.map((s, i) => ({
      label: s.name ?? `Series ${i + 1}`,
      data: s.values,
      backgroundColor: alphaColor(PALETTE[i % PALETTE.length], 0.85),
      borderColor: PALETTE[i % PALETTE.length],
      borderWidth: 1,
    })),
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
