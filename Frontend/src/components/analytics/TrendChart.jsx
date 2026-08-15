import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from "chart.js";
import { formatCurrency } from "../../utils/formatCurrency";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function TrendChart({ data, labels }) {
  if (!data || data.length === 0) {
    return <p className="empty-text">No data available.</p>;
  }

  const chartData = {
    labels,
    datasets: [
      {
        label: "Amount",
        data,
        backgroundColor: "#6366f1",
        borderRadius: 6,
      },
    ],
  };

  return (
    <div className="chart-container">
      <Bar
        data={chartData}
        options={{
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: (context) => formatCurrency(context.parsed.y) } },
          },
          scales: { y: { ticks: { callback: (value) => `₹${value}` } } },
        }}
      />
    </div>
  );
}
