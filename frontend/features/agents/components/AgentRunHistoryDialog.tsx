"use client";

import {
  useState,
} from "react";

import {
  Clock3,
  History,
} from "lucide-react";

import {
  Button,
} from "@/components/ui/button";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import {
  useAgentRuns,
} from "../hooks";

import type {
  Agent,
} from "../types";

import AgentRunDetailsDialog from "./AgentRunDetailsDialog";


type Props = {
  agent: Agent;
};


export default function AgentRunHistoryDialog({
  agent,
}: Props) {
  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    selectedRunId,
    setSelectedRunId,
  ] = useState<
    string | null
  >(null);

  const [
    detailsOpen,
    setDetailsOpen,
  ] = useState(false);


  const runsQuery =
    useAgentRuns(
      open
        ? agent.id
        : null,
    );


  function openRun(
    runId: string,
  ) {
    setSelectedRunId(
      runId,
    );

    setDetailsOpen(
      true,
    );
  }


  return (
    <>
      <Button
        type="button"
        variant="outline"
        onClick={() =>
          setOpen(true)
        }
      >
        <History className="mr-2 h-4 w-4" />

        Run History
      </Button>


      <Dialog
        open={open}
        onOpenChange={
          setOpen
        }
      >
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-5xl">

          <DialogHeader>

            <DialogTitle>
              Run History
            </DialogTitle>

            <DialogDescription>
              Past executions for{" "}
              <span className="font-medium text-slate-700">
                {
                  agent.name
                }
              </span>
              .
            </DialogDescription>

          </DialogHeader>


          {runsQuery.isLoading && (
            <div className="rounded-lg border bg-slate-50 p-6 text-sm text-slate-500">
              Loading run history...
            </div>
          )}


          {runsQuery.isError && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              Failed to load run
              history.
            </div>
          )}


          {runsQuery.data?.length ===
            0 && (
            <div className="rounded-lg border border-dashed p-8 text-center">

              <History className="mx-auto h-8 w-8 text-slate-300" />

              <p className="mt-3 text-sm text-slate-500">
                This agent has no
                recorded runs yet.
              </p>

            </div>
          )}


          {runsQuery.data &&
            runsQuery.data.length > 0 && (
            <div className="overflow-hidden rounded-xl border">

              <div className="overflow-x-auto">

                <table className="w-full text-left text-sm">

                  <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">

                    <tr>

                      <th className="px-4 py-3 font-medium">
                        Status
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Query
                      </th>

                      <th className="px-4 py-3 font-medium">
                        LLM Calls
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Tools
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Duration
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Started
                      </th>

                      <th className="px-4 py-3" />

                    </tr>

                  </thead>


                  <tbody className="divide-y">

                    {runsQuery.data.map(
                      (
                        run,
                      ) => (
                        <tr
                          key={
                            run.id
                          }
                          className="bg-white"
                        >

                          <td className="px-4 py-3">

                            <span
                              className={
                                run.status ===
                                "COMPLETED"
                                  ? "rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700"
                                  : run.status ===
                                    "RUNNING"
                                    ? "rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700"
                                    : "rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700"
                              }
                            >
                              {
                                run.status
                              }
                            </span>

                          </td>


                          <td className="max-w-sm px-4 py-3">

                            <p className="truncate text-slate-700">
                              {
                                run.query
                              }
                            </p>

                          </td>


                          <td className="px-4 py-3 text-slate-600">
                            {
                              run.llm_calls
                            }
                          </td>


                          <td className="px-4 py-3 text-slate-600">
                            {
                              run.tools_used.length
                            }
                          </td>


                          <td className="px-4 py-3 text-slate-600">

                            {run.duration_ms
                              ? `${(
                                  run.duration_ms
                                  / 1000
                                ).toFixed(
                                  2,
                                )}s`
                              : "-"}

                          </td>


                          <td className="px-4 py-3 text-slate-500">

                            <span className="flex items-center gap-1">

                              <Clock3 className="h-3.5 w-3.5" />

                              {
                                new Date(
                                  run.started_at,
                                )
                                  .toLocaleString()
                              }

                            </span>

                          </td>


                          <td className="px-4 py-3 text-right">

                            <Button
                              type="button"
                              size="sm"
                              variant="outline"
                              onClick={() =>
                                openRun(
                                  run.id,
                                )
                              }
                            >
                              View
                            </Button>

                          </td>

                        </tr>
                      ),
                    )}

                  </tbody>

                </table>

              </div>

            </div>
          )}

        </DialogContent>
      </Dialog>


      <AgentRunDetailsDialog
        runId={
          selectedRunId
        }
        open={
          detailsOpen
        }
        onOpenChange={
          setDetailsOpen
        }
      />
    </>
  );
}