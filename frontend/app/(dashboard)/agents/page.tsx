"use client";

import {
  Bot,
} from "lucide-react";

import {
  useAgents,
} from "@/features/agents/hooks";

import AgentList from "@/features/agents/components/AgentList";
import CreateAgentDialog from "@/features/agents/components/CreateAgentDialog";


export default function AgentsPage() {
  const agentsQuery =
    useAgents();


  return (
    <div className="space-y-8">

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

        <div>

          <p className="text-sm font-medium text-slate-500">
            Agent Platform
          </p>

          <h1 className="mt-1 text-3xl font-bold text-slate-900">
            Agents
          </h1>

          <p className="mt-2 max-w-2xl text-slate-500">
            Configure tenant-scoped AI
            agents with enterprise
            knowledge, LLM profiles,
            and governed capabilities.
          </p>

        </div>


        <CreateAgentDialog />

      </div>


      {agentsQuery.isLoading && (
        <div className="rounded-xl border bg-white p-8 text-center text-sm text-slate-500">
          Loading agents...
        </div>
      )}


      {agentsQuery.isError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to load agents.
        </div>
      )}


      {agentsQuery.data && (
        <AgentList
          agents={
            agentsQuery.data
          }
        />
      )}


      {!agentsQuery.isLoading &&
        agentsQuery.data?.length === 0 && (
          <div className="rounded-xl border border-dashed bg-white p-10 text-center">

            <Bot className="mx-auto h-10 w-10 text-slate-300" />

            <h2 className="mt-4 text-lg font-semibold text-slate-900">
              No agents yet
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              Create your first agent
              and connect it to an LLM
              profile and knowledge base.
            </p>

          </div>
        )}

    </div>
  );
}