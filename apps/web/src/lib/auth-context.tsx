"use client";

import type React from "react";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import {
  type AuthResponse,
  type RegistrationResponse,
  type UserProfile,
  apiRequest,
  refreshAccessToken,
} from "./api";

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: {
    first_name: string;
    last_name: string;
    username: string;
    email: string;
    password: string;
    confirm_password: string;
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const logout = useCallback(() => {
    const refresh = localStorage.getItem("refresh_token");
    if (refresh) {
      apiRequest("/auth/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refresh }),
      }).catch(() => {
        // Best-effort backend logout; local state is cleared below regardless.
      });
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setToken(null);
    setRefreshToken(null);
    setUser(null);
  }, []);

  const restoreSession = useCallback(
    async (authToken: string) => {
      try {
        const profile = await apiRequest<UserProfile>("/auth/me", {
          headers: { Authorization: `Bearer ${authToken}` },
        });
        setUser(profile);
      } catch {
        const storedRefresh = localStorage.getItem("refresh_token");
        if (storedRefresh) {
          try {
            const refreshed = await refreshAccessToken(storedRefresh);
            localStorage.setItem("access_token", refreshed.access_token);
            localStorage.setItem("refresh_token", refreshed.refresh_token);
            setToken(refreshed.access_token);
            setRefreshToken(refreshed.refresh_token);
            setUser(refreshed.user);
            return;
          } catch {
            logout();
          }
        } else {
          logout();
        }
      } finally {
        setIsLoading(false);
      }
    },
    [logout],
  );

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    if (storedToken) {
      setToken(storedToken);
      const storedRefresh = localStorage.getItem("refresh_token");
      if (storedRefresh) {
        setRefreshToken(storedRefresh);
      }
      restoreSession(storedToken);
    } else {
      setIsLoading(false);
    }
  }, [restoreSession]);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await apiRequest<AuthResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      localStorage.setItem("access_token", res.access_token);
      localStorage.setItem("refresh_token", res.refresh_token);
      setToken(res.access_token);
      setRefreshToken(res.refresh_token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(
    async (payload: {
      first_name: string;
      last_name: string;
      username: string;
      email: string;
      password: string;
      confirm_password: string;
    }) => {
      setIsLoading(true);
      try {
        await apiRequest<RegistrationResponse>("/auth/register", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        refreshToken,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
