import { formatCurrency } from "../../utils/formatCurrency";

const svg = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  width: 22,
  height: 22,
};

const ICONS = {
  wallet: (
    <svg {...svg}>
      <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4" />
      <path d="M3 5v14a2 2 0 0 0 2 2h16v-5" />
      <path d="M18 12a2 2 0 0 0 0 4h4v-4Z" />
    </svg>
  ),
  calendar: (
    <svg {...svg}>
      <path d="M8 2v4" />
      <path d="M16 2v4" />
      <rect width="18" height="18" x="3" y="4" rx="2" />
      <path d="M3 10h18" />
      <path d="M8 14h.01" />
      <path d="M12 14h.01" />
    </svg>
  ),
  target: (
    <svg {...svg}>
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="2" />
    </svg>
  ),
  piggyBank: (
    <svg {...svg}>
      <path d="M19 5c-1.5 0-2.8 1.4-3 2-3.5-1.5-11-.3-11 5 0 1.8 0 3 2 4.5V20h4v-2h3v2h4v-4c1-.5 1.7-1 2-2h2v-4h-2c0-1-.5-1.5-1-2V5z" />
      <path d="M2 9v1c0 1.1.9 2 2 2h1" />
      <path d="M16 11h.01" />
    </svg>
  ),
};

export default function SummaryCards({ data }) {
  if (!data) return null;

  const cards = [
    { label: "Total Expenses", value: formatCurrency(data.total_expenses), icon: ICONS.wallet, tint: "indigo" },
    { label: "Monthly Spending", value: formatCurrency(data.monthly_expenses), icon: ICONS.calendar, tint: "blue" },
    { label: "Budget", value: formatCurrency(data.budget), icon: ICONS.target, tint: "violet" },
    { label: "Remaining Budget", value: formatCurrency(data.remaining_budget), icon: ICONS.piggyBank, tint: "green" },
  ];

  return (
    <div className="summary-grid">
      {cards.map((card) => (
        <div className="card summary-card" key={card.label}>
          <span className={`summary-icon tint-${card.tint}`}>{card.icon}</span>
          <div>
            <p className="summary-label">{card.label}</p>
            <p className="summary-value">{card.value}</p>
          </div>
        </div>
      ))}
    </div>
  );
}