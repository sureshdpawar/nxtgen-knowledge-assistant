"use client";

import {
  useState,
} from "react";

import {
  useKnowledgeSourceSyncs,
} from "../hooks";

import type {
  KnowledgeSourceSync,
} from "../types";

import {
  Button,
} from "@/components/ui/button";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";


type Props = {
  knowledgeSourceId: string;
};


export default function KnowledgeSourceSyncHistory({
  knowledgeSourceId,
}: Props) {
  const {
    data,
    isLoading,
    error,
  } =
    useKnowledgeSourceSyncs(
      knowledgeSourceId,
    );

  const [
    selectedSync,
    setSelectedSync,
  ] =
    useState<KnowledgeSourceSync | null>(
      null,
    );


  if (isLoading) {
    return (
      <p className="text-sm text-slate-500">
        Loading sync history...
      </p>
    );
  }


  if (error) {
    return (
      <p className="text-sm text-red-600">
        Failed to load sync history.
      </p>
    );
  }


  if (
    !data
    || data.length === 0
  ) {
    return (
      <div className="rounded-xl border border-dashed bg-white p-8 text-center">

        <p className="text-sm text-slate-500">
          No sync history yet.
        </p>

      </div>
    );
  }


  return (
    <section className="space-y-4">

      <div>
        <h2 className="text-lg font-semibold text-slate-900">
          Sync History
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Previous manual synchronization runs.
        </p>
      </div>


      <div className="overflow-hidden rounded-xl border bg-white">

        <div className="overflow-x-auto">

          <table className="min-w-full text-sm">

            <thead className="border-b bg-slate-50">

              <tr className="text-left text-xs font-medium uppercase tracking-wide text-slate-500">

                <th className="px-4 py-3">
                  Date
                </th>

                <th className="px-4 py-3">
                  Status
                </th>

                <th className="px-4 py-3 text-right">
                  Discovered
                </th>

                <th className="px-4 py-3 text-right">
                  New
                </th>

                <th className="px-4 py-3 text-right">
                  Changed
                </th>

                <th className="px-4 py-3 text-right">
                  Unchanged
                </th>

                <th className="px-4 py-3 text-right">
                  Missing
                </th>

                <th className="px-4 py-3 text-right">
                  Failed
                </th>

                <th className="px-4 py-3 text-right">
                  Details
                </th>

              </tr>

            </thead>


            <tbody className="divide-y">

              {data.map(
                (
                  sync,
                  index,
                ) => (
                  <SyncRow
                    key={
                      sync.id
                    }
                    sync={
                      sync
                    }
                    latest={
                      index === 0
                    }
                    onViewDetails={() =>
                      setSelectedSync(
                        sync,
                      )
                    }
                  />
                ),
              )}

            </tbody>

          </table>

        </div>

      </div>


      <SyncDetailsDialog
        sync={selectedSync}
        open={selectedSync !== null}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedSync(
              null,
            );
          }
        }}
      />

    </section>
  );
}


function SyncRow({
  sync,
  latest,
  onViewDetails,
}: {
  sync:
    KnowledgeSourceSync;

  latest: boolean;

  onViewDetails: () => void;
}) {
  return (
    <tr className="hover:bg-slate-50">

      <td className="whitespace-nowrap px-4 py-3">

        <div className="font-medium text-slate-900">
          {
            sync.started_at
              ? new Date(
                  sync.started_at,
                ).toLocaleDateString()
              : "—"
          }
        </div>

        <div className="mt-0.5 text-xs text-slate-400">
          {
            sync.started_at
              ? new Date(
                  sync.started_at,
                ).toLocaleTimeString()
              : ""
          }

          {latest && (
            <span className="ml-2 text-blue-600">
              Latest
            </span>
          )}
        </div>

      </td>


      <td className="px-4 py-3">

        <span
          className={[
            "rounded-full px-2 py-1 text-xs font-medium",
            getStatusClass(
              sync.status,
            ),
          ].join(" ")}
        >
          {sync.status}
        </span>

      </td>


      <NumberCell
        value={
          sync.items_discovered
        }
      />

      <NumberCell
        value={
          sync.items_new
        }
      />

      <NumberCell
        value={
          sync.items_changed
        }
      />

      <NumberCell
        value={
          sync.items_unchanged
        }
      />

      <NumberCell
        value={
          sync.items_missing
        }
      />

      <NumberCell
        value={
          sync.items_failed
        }
      />


      <td className="whitespace-nowrap px-4 py-3 text-right">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={
            onViewDetails
          }
        >
          View
        </Button>
      </td>

    </tr>
  );
}


function SyncDetailsDialog({
  sync,
  open,
  onOpenChange,
}: {
  sync: KnowledgeSourceSync | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  if (!sync) {
    return null;
  }

  return (
    <Dialog
      open={open}
      onOpenChange={
        onOpenChange
      }
    >
      <DialogContent className="max-h-[85vh] max-w-3xl overflow-y-auto">

        <DialogHeader>
          <DialogTitle>
            Sync Run Details
          </DialogTitle>

          <DialogDescription>
            Synchronization outcome and provider diagnostics for this run.
          </DialogDescription>
        </DialogHeader>


        <div className="space-y-5">

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">

            <DetailField
              label="Status"
              value={sync.status}
            />

            <DetailField
              label="Started"
              value={
                formatDateTime(
                  sync.started_at,
                )
              }
            />

            <DetailField
              label="Completed"
              value={
                formatDateTime(
                  sync.completed_at,
                )
              }
            />

            <DetailField
              label="Run ID"
              value={sync.id}
              mono
            />

          </div>


          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">

            <Metric
              label="Discovered"
              value={
                sync.items_discovered
              }
            />

            <Metric
              label="New"
              value={
                sync.items_new
              }
            />

            <Metric
              label="Changed"
              value={
                sync.items_changed
              }
            />

            <Metric
              label="Unchanged"
              value={
                sync.items_unchanged
              }
            />

            <Metric
              label="Missing"
              value={
                sync.items_missing
              }
            />

            <Metric
              label="Failed"
              value={
                sync.items_failed
              }
            />

          </div>


          <SummaryBlock
            title="Provider Summary"
            value={
              sync.provider_summary
            }
            emptyText="No provider diagnostics were recorded for this run."
          />


          {sync.error_message && (
            <SummaryBlock
              title="Error"
              value={
                sync.error_message
              }
              emptyText=""
              error
            />
          )}

        </div>


        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() =>
              onOpenChange(
                false,
              )
            }
          >
            Close
          </Button>
        </DialogFooter>

      </DialogContent>
    </Dialog>
  );
}


function Metric({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-lg border bg-slate-50 px-3 py-3">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </div>

      <div className="mt-1 text-lg font-semibold tabular-nums text-slate-900">
        {value}
      </div>
    </div>
  );
}


function DetailField({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div>
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </div>

      <div
        className={[
          "mt-1 break-words text-sm text-slate-900",
          mono
            ? "font-mono text-xs"
            : "",
        ].join(" ")}
      >
        {value}
      </div>
    </div>
  );
}


function SummaryBlock({
  title,
  value,
  emptyText,
  error = false,
}: {
  title: string;
  value: string | null;
  emptyText: string;
  error?: boolean;
}) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-slate-900">
        {title}
      </h3>

      <div
        className={[
          "mt-2 whitespace-pre-wrap break-words rounded-lg border p-4 text-sm leading-6",
          error
            ? "border-red-200 bg-red-50 text-red-800"
            : "border-slate-200 bg-slate-50 text-slate-700",
        ].join(" ")}
      >
        {
          value?.trim()
            ? value
            : emptyText
        }
      </div>
    </div>
  );
}


function NumberCell({
  value,
}: {
  value: number;
}) {
  return (
    <td className="px-4 py-3 text-right tabular-nums text-slate-700">
      {value}
    </td>
  );
}


function formatDateTime(
  value: string | null,
) {
  if (!value) {
    return "—";
  }

  return new Date(
    value,
  ).toLocaleString();
}


function getStatusClass(
  status:
    KnowledgeSourceSync["status"],
) {
  switch (status) {
    case "COMPLETED":
      return (
        "bg-green-100 text-green-700"
      );

    case "COMPLETED_WITH_ERRORS":
      return (
        "bg-amber-100 text-amber-700"
      );

    case "FAILED":
      return (
        "bg-red-100 text-red-700"
      );

    case "RUNNING":
      return (
        "bg-blue-100 text-blue-700"
      );

    default:
      return (
        "bg-slate-100 text-slate-600"
      );
  }
}
