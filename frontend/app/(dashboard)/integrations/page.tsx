"use client";

import {
  Cable,
} from "lucide-react";

import {
  useIntegrations,
} from "@/features/integrations/hooks";

import CreateIntegrationDialog from "@/features/integrations/components/CreateIntegrationDialog";
import IntegrationList from "@/features/integrations/components/IntegrationList";


export default function IntegrationsPage() {
  const integrationsQuery =
    useIntegrations();


  return (
    <div className="space-y-8">

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

        <div>

          <p className="text-sm font-medium text-slate-500">
            Agent Studio
          </p>

          <h1 className="mt-1 text-3xl font-bold text-slate-900">
            Integrations
          </h1>

          <p className="mt-2 max-w-2xl text-slate-500">
            Connect enterprise REST
            APIs and MCP servers that
            can provide capabilities
            to your agents.
          </p>

        </div>


        <CreateIntegrationDialog />

      </div>


      {integrationsQuery.isLoading && (
        <div className="rounded-xl border bg-white p-8 text-center text-sm text-slate-500">
          Loading integrations...
        </div>
      )}


      {integrationsQuery.isError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to load integrations.
        </div>
      )}


      {integrationsQuery.data && (
        <IntegrationList
          integrations={
            integrationsQuery.data
          }
        />
      )}


      {!integrationsQuery.isLoading &&
        integrationsQuery.data?.length ===
          0 && (
          <div className="rounded-xl border border-dashed bg-white p-10 text-center">

            <Cable className="mx-auto h-10 w-10 text-slate-300" />

            <h2 className="mt-4 text-lg font-semibold text-slate-900">
              No integrations yet
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              Connect a REST API or
              MCP server to start
              exposing enterprise
              capabilities to agents.
            </p>

          </div>
        )}

    </div>
  );
}