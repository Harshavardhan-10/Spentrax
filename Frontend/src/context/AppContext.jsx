import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { categoryService } from "../services/categoryService";
import { useAuth } from "./AuthContext";

const AppContext = createContext(null);

function readCache(key) {
  try {
    const parsed = JSON.parse(localStorage.getItem(key));
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function AppProvider({ children }) {
  const { user } = useAuth();
  const cacheKey = user?.email ? `spentrax_categories_${user.email}` : null;

  const [categories, setCategories] = useState([]);
  const [loadingCategories, setLoadingCategories] = useState(true);

  const refreshCategories = useCallback(async () => {
    try {
      const data = await categoryService.list();
      setCategories(data);
      if (cacheKey) localStorage.setItem(cacheKey, JSON.stringify(data));
    } finally {
      setLoadingCategories(false);
    }
  }, [cacheKey]);

  // Hydrate instantly from the per-user cache, then refresh from the server.
  useEffect(() => {
    setCategories(cacheKey ? readCache(cacheKey) : []);
    setLoadingCategories(true);
    refreshCategories();
  }, [cacheKey, refreshCategories]);

  const value = useMemo(
    () => ({ categories, loadingCategories, refreshCategories }),
    [categories, loadingCategories, refreshCategories]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
}