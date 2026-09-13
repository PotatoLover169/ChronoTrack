import { useContext } from "react";

import { AuthContext } from "../context/AuthContextValue";

export function useAuthContext() {
  return useContext(AuthContext);
}