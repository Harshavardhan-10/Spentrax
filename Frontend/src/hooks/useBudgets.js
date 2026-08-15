import { useCallback, useEffect, useState } from "react";
import { budgetService } from "../services/budgetService";

export function useBudgets(month, year) {
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (month) params.month = month;
      if (year) params.year = year;
      const data = await budgetService.list(params);
      setBudgets(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [month, year]);

  useEffect(() => {
    load();
  }, [load]);

  const refresh = useCallback(() => load(), [load]);

  return { budgets, loading, error, refresh };
}
