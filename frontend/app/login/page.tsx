"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";

import { useAuth } from "@/hooks/useAuth";

import { LoginRequest } from "@/types/auth";

export default function LoginPage() {

  const router = useRouter();

  const { login } = useAuth();

  const {
    register,
    handleSubmit,
  } = useForm<LoginRequest>();

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function onSubmit(
    data: LoginRequest,
  ) {

    try {

      setLoading(true);

      setError("");

      await login(data);

      router.push("/dashboard");

    } catch {

      setError(
        "Invalid email or password.",
      );

    } finally {

      setLoading(false);

    }

  }

  return (

    <div className="flex min-h-screen items-center justify-center bg-slate-100">

      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-lg">

        <h1 className="mb-8 text-center text-3xl font-bold">
          NXTGEN Knowledge Assistant
        </h1>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-5"
        >

          <div>

            <label className="mb-2 block text-sm font-medium">
              Email
            </label>

            <input
              type="email"
              {...register("email")}
              className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500"
            />

          </div>

          <div>

            <label className="mb-2 block text-sm font-medium">
              Password
            </label>

            <input
              type="password"
              {...register("password")}
              className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500"
            />

          </div>

          {error && (

            <div className="rounded bg-red-100 p-3 text-sm text-red-700">

              {error}

            </div>

          )}

          <Button
            type="submit"
            className="w-full"
            disabled={loading}
          >

            {loading
              ? "Signing In..."
              : "Sign In"}

          </Button>

        </form>

      </div>

    </div>

  );

}