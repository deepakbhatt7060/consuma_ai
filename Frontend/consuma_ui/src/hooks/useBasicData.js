import useSWR from "swr";

import { fetcher } from "../utils";

export const useBasicData = ({ url, refreshInterval }) => {
  const { data, error, isLoading } = useSWR(url, fetcher, { refreshInterval });
  return { data, error, isLoading };
};
