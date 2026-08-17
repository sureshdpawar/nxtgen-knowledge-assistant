"use client";

import {
  Cable,
  Shield,
  Wrench,
} from "lucide-react";

import {
  useIntegrations,
} from "@/features/integrations/hooks";

import type {
  ToolDefinition,
} from "../types";

import DeleteToolDialog from "./DeleteToolDialog";
import EditToolDialog from "./EditToolDialog";


type Props = {
  tools:
    ToolDefinition[];
};


export default function ToolList({
  tools,
}: Props) {
  const integrationsQuery =
    useIntegrations();


  if (
    tools.length === 0
  ) {
    return null;
  }


  function getIntegrationName(
    integrationId:
      string | null,
  ) {
    if (!integrationId) {
      return "NXTGEN";
    }

    return (
      integrationsQuery.data
        ?.find(
          (integration) =>
            integration.id ===
            integrationId,
        )
        ?.name
      ?? "Integration"
    );
  }


  return (
    <div className="space-y-4">

      {tools.map(
        (
          tool,
        ) => (
          <div
            key={
              tool.id
            }
            className="rounded-xl border bg-white p-5 shadow-sm"
          >

            <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">

              <div className="flex items-start gap-4">

                <div className="rounded-xl bg-violet-50 p-3">

                  <Wrench className="h-5 w-5 text-violet-600" />

                </div>


                <div>

                  <div className="flex flex-wrap items-center gap-2">

                    <h3 className="font-semibold text-slate-900">
                      {
                        tool.name
                      }
                    </h3>


                    <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
                      {
                        tool.tool_type
                      }
                    </span>


                    <span
                      className={
                        tool.risk_level ===
                        "WRITE"
                          ? "rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700"
                          : "rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700"
                      }
                    >
                      {
                        tool.risk_level
                      }
                    </span>


                    <span
                      className={
                        tool.is_active
                          ? "rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700"
                          : "rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600"
                      }
                    >
                      {
                        tool.is_active
                          ? "ACTIVE"
                          : "INACTIVE"
                      }
                    </span>

                  </div>


                  <p className="mt-2 max-w-2xl text-sm text-slate-600">
                    {
                      tool.description
                    }
                  </p>


                  <div className="mt-4 flex flex-wrap gap-4 text-xs text-slate-500">

                    <div className="flex items-center gap-1.5">

                      <Cable className="h-3.5 w-3.5" />

                      {
                        getIntegrationName(
                          tool.integration_id,
                        )
                      }

                    </div>


                    <div className="flex items-center gap-1.5">

                      <Shield className="h-3.5 w-3.5" />

                      {
                        tool.risk_level ===
                        "WRITE"
                          ? "May change external systems"
                          : "Read-only capability"
                      }

                    </div>

                  </div>

                </div>

              </div>


              <div className="flex flex-wrap gap-2">

                <EditToolDialog
                  tool={
                    tool
                  }
                />


                <DeleteToolDialog
                  tool={
                    tool
                  }
                />

              </div>

            </div>

          </div>
        ),
      )}

    </div>
  );
}