import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { CHART_COLORS } from "../../utils/constants";
import { formatCurrency } from "../../utils/formatCurrency";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function CategoryChart({ breakdown }) {
  if (!breakdown || breakdown.length === 0) {
    return <p className="empty-text">No category data available.</p>;
  }

  const data = {
    labels: breakdown.map((item) => `${item.category_name} (${item.percentage}%)`),
    datasets: [
      {
        data: breakdown.map((item) => item.amount),
        backgroundColor: breakdown.map((_, index) => CHART_COLORS[index % CHART_COLORS.length]),
      },
    ],
  };

  return (
    <div className="chart-container doughnut-container">
      <Doughnut
        data={data}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: "bottom" },
            tooltip: { callbacks: { label: (context) => formatCurrency(context.parsed) } },
          },
        }}
      />
    </div>
  );
}
