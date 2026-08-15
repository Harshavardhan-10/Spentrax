import { useId } from "react";

export default function Brand({ light = false, tagline = "", size = 34 }) {
  const id = useId().replace(/[^a-zA-Z0-9]/g, "");

  return (
    <div className={`brand ${light ? "brand-light" : ""}`}>
      <svg className="brand-logo" width={size} height={size} viewBox="0 0 48 48" aria-hidden="true">
        <defs>
          <linearGradient id={`spentrax-g-${id}`} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>
        <rect x="2" y="2" width="44" height="44" rx="13" fill={`url(#spentrax-g-${id})`} />
        <rect x="12" y="26" width="4" height="8" rx="1" fill="#fff" opacity="0.9" />
        <rect x="21" y="22" width="4" height="12" rx="1" fill="#fff" opacity="0.9" />
        <rect x="30" y="17" width="4" height="17" rx="1" fill="#fff" opacity="0.9" />
        <path d="M38 4 L39.6 8.4 L44 10 L39.6 11.6 L38 16 L36.4 11.6 L32 10 L36.4 8.4 Z" fill="#fff" />
      </svg>
      <div className="brand-text">
        <strong className="brand-name">Spentrax</strong>
        {tagline && <small className="brand-tagline">{tagline}</small>}
      </div>
    </div>
  );
}
