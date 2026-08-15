import { useCallback, useEffect, useState } from "react";
import { aiService } from "../services/aiService";

export function useAI() {
  const [insights, setInsights] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadInsights = useCallback(async (refresh = false) => {
    setLoading(true);
    setError(null);
    try {
      const data = await aiService.insights({ refresh });
      setInsights(data);
      return data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const loadRecommendations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await aiService.recommendations();
      setRecommendations(data);
      return data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const loadSummary = useCallback(async (month, year) => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (month) params.month = month;
      if (year) params.year = year;
      const data = await aiService.summary(params);
      setSummary(data);
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const categorize = useCallback(async (description, merchant) => {
    try {
      return await aiService.categorize({ description, merchant });
    } catch (err) {
      throw new Error(err.message);
    }
  }, []);

  useEffect(() => {
    loadInsights();
    loadRecommendations();
  }, [loadInsights, loadRecommendations]);

  return {
    insights,
    recommendations,
    summary,
    loading,
    error,
    loadInsights,
    loadRecommendations,
    loadSummary,
    categorize,
  };
}
