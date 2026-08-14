"use client";

import {
  CheckCircle2,
  Cpu,
} from "lucide-react";

import {
  Button,
} from "@/components/ui/button";

import {
  useSetDefaultLLMProfile,
} from "../hooks";

import type {
  LLMProfile,
} from "../types";

import DeleteLLMProfileDialog from "./DeleteLLMProfileDialog";
import EditLLMProfileDialog from "./EditLLMProfileDialog";


type Props = {
  profiles: LLMProfile[];
};


export default function LLMProfileList({
  profiles,
}: Props) {
  const setDefaultMutation =
    useSetDefaultLLMProfile();


  if (
    profiles.length === 0
  ) {
    return (
      <div className="rounded-xl border border-dashed bg-white p-8 text-center">

        <Cpu className="mx-auto h-8 w-8 text-slate-300" />

        <h3 className="mt-3 font-semibold text-slate-900">
          No LLM profiles
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          Create your first tenant
          LLM profile.
        </p>

      </div>
    );
  }


  return (
    <div className="space-y-3">

      {profiles.map(
        (
          profile,
        ) => (
          <div
            key={
              profile.id
            }
            className="rounded-xl border bg-white p-5 shadow-sm"
          >

            <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">

              <div className="flex items-start gap-3">

                <div className="rounded-lg bg-blue-50 p-3">

                  <Cpu className="h-5 w-5 text-blue-600" />

                </div>


                <div>

                  <div className="flex flex-wrap items-center gap-2">

                    <h3 className="font-semibold text-slate-900">
                      {
                        profile.name
                      }
                    </h3>


                    {profile.is_default && (
                      <span className="flex items-center gap-1 rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700">

                        <CheckCircle2 className="h-3.5 w-3.5" />

                        DEFAULT

                      </span>
                    )}


                    <span
                      className={
                        profile.is_active
                          ? "rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700"
                          : "rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700"
                      }
                    >
                      {
                        profile.is_active
                          ? "ACTIVE"
                          : "INACTIVE"
                      }
                    </span>

                  </div>


                  <p className="mt-2 text-sm text-slate-600">
                    {
                      profile.provider
                    }{" "}
                    •{" "}
                    {
                      profile.model_name
                    }
                  </p>


                  <p className="mt-2 text-xs text-slate-400">
                    Temperature:{" "}
                    {
                      profile.temperature
                    }{" "}
                    • Max Tokens:{" "}
                    {
                      profile.max_tokens
                    }
                  </p>

                </div>

              </div>


              <div className="flex flex-wrap items-center gap-2">

                <EditLLMProfileDialog
                  profile={
                    profile
                  }
                />


                {!profile.is_default && (
                  <>
                    <Button
                      type="button"
                      variant="outline"
                      disabled={
                        !profile.is_active ||
                        setDefaultMutation.isPending
                      }
                      onClick={() =>
                        setDefaultMutation.mutate(
                          profile.id,
                        )
                      }
                    >
                      {
                        setDefaultMutation.isPending
                          ? "Updating..."
                          : "Set Default"
                      }
                    </Button>


                    <DeleteLLMProfileDialog
                      profile={
                        profile
                      }
                    />
                  </>
                )}

              </div>

            </div>

          </div>
        ),
      )}

    </div>
  );
}