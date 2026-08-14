"use client";

import {
  useAuth,
} from "@/hooks/useAuth";

import {
  useLLMProfiles,
} from "@/features/llm-config/hooks";

import CreateLLMProfileDialog from "@/features/llm-config/components/CreateLLMProfileDialog";
import LLMProfileList from "@/features/llm-config/components/LLMProfileList";


export default function SettingsPage() {
  const {
    user,
  } =
    useAuth();


  const isAdmin =
    user?.role === "ADMIN";


  const {
    data:
      profiles,

    isLoading,

    error,
  } =
    useLLMProfiles(
      isAdmin,
    );


  if (!user) {
    return null;
  }


  if (!isAdmin) {
    return (
      <div className="rounded-xl border bg-white p-8 shadow-sm">

        <h1 className="text-2xl font-bold text-slate-900">
          Settings
        </h1>

        <p className="mt-2 text-slate-500">
          No tenant settings are
          available for this role.
        </p>

      </div>
    );
  }


  return (
    <div className="space-y-8">

      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">

        <div>

          <p className="text-sm font-medium text-slate-500">
            Tenant Administration
          </p>

          <h1 className="mt-1 text-3xl font-bold text-slate-900">
            LLM Profiles
          </h1>

          <p className="mt-2 max-w-2xl text-slate-500">
            Configure reusable AI
            profiles for this tenant.
            Knowledge bases can inherit
            the default profile or use
            their own profile.
          </p>

        </div>


        <CreateLLMProfileDialog />

      </div>


      {isLoading && (
        <p className="text-sm text-slate-500">
          Loading LLM profiles...
        </p>
      )}


      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to load LLM profiles.
        </div>
      )}


      {profiles && (
        <LLMProfileList
          profiles={
            profiles
          }
        />
      )}

    </div>
  );
}