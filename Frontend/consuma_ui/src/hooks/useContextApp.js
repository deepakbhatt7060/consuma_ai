import { useState } from "react";
import { useBasicData } from "./useBasicData";

export const useNavigation = () => {
  const [loading, setLoading] = useState(undefined);
  const { data, error, isLoading } = useBasicData({
    url: "http://127.0.0.1:8000/healthz",
    refreshInterval: 2000,
  });
  console.log("Health data:", data, error, isLoading);
  return {
    health: data,
    healthError: error,
    healthLoading: isLoading,
    loading,
    setLoading,
  };
};
