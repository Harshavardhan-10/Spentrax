import { useCallback, useEffect, useState } from "react";
import { expenseService } from "../services/expenseService";

export function useExpenses(filters = {}) {
  const [data, setData] = useState({ items: [], total: 0, page: 1, limit: 20, pages: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await expenseService.list(filters);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(filters)]);

  useEffect(() => {
    load();
  }, [load]);

  const refresh = useCallback(() => load(), [load]);

  return { ...data, loading, error, refresh };
}
