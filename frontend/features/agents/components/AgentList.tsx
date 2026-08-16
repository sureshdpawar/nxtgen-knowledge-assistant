"use client";

import {
  Bot,
  Database,
} from "lucide-react";

import type {
  Agent,
} from "../types";

import AgentRunHistoryDialog from "./AgentRunHistoryDialog";
import EditAgentDialog from "./EditAgentDialog";
import TestAgentDialog from "./TestAgentDialog";


type Props = {
  agents: Agent[];
};


export default function AgentList({
  agents,
}: Props) {
  if (
    agents.length === 0
  ) {
    return null;
  }


  return (
    <div className="space-y-4">

      {agents.map(
        (
          agent,
        ) => (
          <div
            key={
              agent.id
            }
            className="rounded-xl border bg-white p-5 shadow-sm"
          >

            <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">

              <div className="flex items-start gap-4">

                <div className="rounded-xl bg-violet-50 p-3">

                  <Bot className="h-6 w-6 text-violet-600" />

                </div>


                <div>

                  <div className="flex flex-wrap items-center gap-2">

                    <h3 className="text-lg font-semibold text-slate-900">
                      {
                        agent.name
                      }
                    </h3>


                    <span
                      className={
                        agent.status ===
                        "ACTIVE"
                          ? "rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700"
                          : agent.status ===
                            "DRAFT"
                            ? "rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700"
                            : "rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600"
                      }
                    >
                      {
                        agent.status
                      }
                    </span>

                  </div>


                  {agent.description && (
                    <p className="mt-2 max-w-2xl text-sm text-slate-600">
                      {
                        agent.description
                      }
                    </p>
                  )}


                  <div className="mt-4 flex flex-wrap gap-4 text-xs text-slate-500">

                    <div className="flex items-center gap-1.5">

                      <Database className="h-3.5 w-3.5" />

                      {
                        agent
                          .knowledge_base_ids
                          .length
                      }{" "}
                      knowledge base
                      {
                        agent
                          .knowledge_base_ids
                          .length === 1
                          ? ""
                          : "s"
                      }

                    </div>


                    <div>
                      Max steps:{" "}
                      {
                        agent.max_iterations
                      }
                    </div>


                    <div>
                      LLM:{" "}
                      {
                        agent
                          .llm_configuration_id
                          ? "Custom profile"
                          : "Tenant default"
                      }
                    </div>

                  </div>

                </div>

              </div>


              <div className="flex flex-wrap items-center gap-2">

                <AgentRunHistoryDialog
                  agent={
                    agent
                  }
                />


                <EditAgentDialog
                  agent={
                    agent
                  }
                />


                <TestAgentDialog
                  agent={
                    agent
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