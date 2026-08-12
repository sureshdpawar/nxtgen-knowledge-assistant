"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";

import authService from "@/services/auth.service";

import {
  AuthUser,
  LoginRequest,
} from "@/types/auth";

type AuthContextType = {
  user: AuthUser | null;

  loading: boolean;

  authenticated: boolean;

  login: (
    credentials: LoginRequest,
  ) => Promise<void>;

  logout: () => void;
};

const AuthContext =
  createContext<AuthContextType | null>(
    null,
  );

type Props = {
  children: ReactNode;
};

export function AuthProvider({
  children,
}: Props) {
  const [user, setUser] =
    useState<AuthUser | null>(null);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    initialize();
  }, []);

  async function initialize() {
    const token =
      localStorage.getItem(
        "access_token",
      );

    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const currentUser =
        await authService.me();

      setUser(currentUser);
    } catch {
      localStorage.removeItem(
        "access_token",
      );

      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  async function login(
    credentials: LoginRequest,
  ) {
    setLoading(true);

    try {
      const response =
        await authService.login(
          credentials,
        );

      localStorage.setItem(
        "access_token",
        response.access_token,
      );

      const currentUser =
        await authService.me();

      setUser(currentUser);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    authService.logout();

    localStorage.removeItem(
      "access_token",
    );

    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,

        loading,

        authenticated:
          user !== null,

        login,

        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider",
    );
  }

  return context;
}