import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import { formatCurrency } from "../../utils/formatCurrency";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function SpendingChart({ trend }) {
  if (!trend || trend.length === 0) {
    return <p className="empty-text">No spending data available yet.</p>;
  }

  const data = {
    labels: trend.map((point) => point.label),
    datasets: [
      {
        label: "Monthly spending",
        data: trend.map((point) => point.total),
        borderColor: "#6366f1",
        backgroundColor: "rgba(99, 102, 241, 0.1)",
        fill: true,
        tension: 0.35,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => formatCurrency(context.parsed.y),
        },
      },
    },
    scales: {
      y: {
        ticks: { callback: (value) => `₹${value}` },
      },
    },
  };

  return (
    <div className="chart-container">
      <Line data={data} options={options} />
    </div>
  );
}
