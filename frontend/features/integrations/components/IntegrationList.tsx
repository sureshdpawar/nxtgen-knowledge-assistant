"use client";

import {
  Cable,
  Globe2,
  ServerCog,
} from "lucide-react";

import type {
  Integration,
} from "../types";

import DeleteIntegrationDialog from "./DeleteIntegrationDialog";
import EditIntegrationDialog from "./EditIntegrationDialog";


type Props = {
  integrations:
    Integration[];
};


export default function IntegrationList({
  integrations,
}: Props) {
  if (
    integrations.length === 0
  ) {
    return null;
  }


  return (
    <div className="grid gap-4 lg:grid-cols-2">

      {integrations.map(
        (
          integration,
        ) => (
          <div
            key={
              integration.id
            }
            className="rounded-xl border bg-white p-5 shadow-sm"
          >

            <div className="flex items-start justify-between gap-4">

              <div className="flex items-start gap-3">

                <div className="rounded-xl bg-blue-50 p-3">

                  {integration.integration_type ===
                  "MCP" ? (
                    <ServerCog className="h-5 w-5 text-blue-600" />
                  ) : (
                    <Globe2 className="h-5 w-5 text-blue-600" />
                  )}

                </div>


                <div>

                  <div className="flex flex-wrap items-center gap-2">

                    <h3 className="font-semibold text-slate-900">
                      {
                        integration.name
                      }
                    </h3>


                    <span
                      className={
                        integration.is_active
                          ? "rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700"
                          : "rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600"
                      }
                    >
                      {
                        integration.is_active
                          ? "ACTIVE"
                          : "INACTIVE"
                      }
                    </span>

                  </div>


                  <div className="mt-3 space-y-2 text-sm text-slate-500">

                    <div className="flex items-center gap-2">

                      <Cable className="h-4 w-4" />

                      {
                        integration.integration_type
                      }

                    </div>


                    <p className="break-all font-mono text-xs">
                      {
                        integration.base_url
                      }
                    </p>


                    <p className="text-xs">
                      Auth:{" "}
                      {
                        integration.auth_type
                      }
                    </p>

                  </div>

                </div>

              </div>

            </div>


            <div className="mt-5 flex flex-wrap gap-2">

              <EditIntegrationDialog
                integration={
                  integration
                }
              />


              <DeleteIntegrationDialog
                integration={
                  integration
                }
              />

            </div>

          </div>
        ),
      )}

    </div>
  );
}