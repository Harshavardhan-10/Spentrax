import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from "chart.js";
import { formatCurrency } from "../../utils/formatCurrency";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function MonthlyChart({ trends }) {
  if (!trends || trends.length === 0) {
    return <p className="empty-text">No trend data available.</p>;
  }

  const data = {
    labels: trends.map((point) => point.label),
    datasets: [
      {
        label: "Monthly total",
        data: trends.map((point) => point.total),
        borderColor: "#6366f1",
        backgroundColor: "rgba(99, 102, 241, 0.15)",
        fill: true,
        tension: 0.3,
      },
    ],
  };

  return (
    <div className="chart-container">
      <Line
        data={data}
        options={{
          responsive: true,
          plugins: {
            tooltip: { callbacks: { label: (context) => formatCurrency(context.parsed.y) } },
          },
          scales: { y: { ticks: { callback: (value) => `₹${value}` } } },
        }}
      />
    </div>
  );
}
