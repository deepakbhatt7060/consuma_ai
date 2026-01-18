import { createContext, useMemo } from "react";

import { useNavigation } from "../hooks/useContextApp";

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const navigationValues = useNavigation();

  const value = useMemo(
    () => ({
      ...navigationValues,
    }),
    [navigationValues],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
