"use client";

import {
  Wrench,
} from "lucide-react";

import {
  useTools,
} from "@/features/tools/hooks";

import CreateToolDialog from "@/features/tools/components/CreateToolDialog";
import ToolList from "@/features/tools/components/ToolList";


export default function ToolsPage() {
  const toolsQuery =
    useTools();


  return (
    <div className="space-y-8">

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

        <div>

          <p className="text-sm font-medium text-slate-500">
            Agent Studio
          </p>

          <h1 className="mt-1 text-3xl font-bold text-slate-900">
            Tools
          </h1>

          <p className="mt-2 max-w-2xl text-slate-500">
            Define capabilities that
            agents can invoke through
            native services, REST APIs,
            or MCP integrations.
          </p>

        </div>


        <CreateToolDialog />

      </div>


      {toolsQuery.isLoading && (
        <div className="rounded-xl border bg-white p-8 text-center text-sm text-slate-500">
          Loading tools...
        </div>
      )}


      {toolsQuery.isError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to load tools.
        </div>
      )}


      {toolsQuery.data && (
        <ToolList
          tools={
            toolsQuery.data
          }
        />
      )}


      {!toolsQuery.isLoading &&
        toolsQuery.data?.length ===
          0 && (
          <div className="rounded-xl border border-dashed bg-white p-10 text-center">

            <Wrench className="mx-auto h-10 w-10 text-slate-300" />

            <h2 className="mt-4 text-lg font-semibold text-slate-900">
              No tools yet
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              Create a tool from an
              integration and later
              assign it to an agent.
            </p>

          </div>
        )}

    </div>
  );
}