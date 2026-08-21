"use client";

import {
  useKnowledgeSourceSyncs,
} from "../hooks";

import type {
  KnowledgeSourceSync,
} from "../types";


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
                  />
                ),
              )}

            </tbody>

          </table>

        </div>

      </div>

    </section>
  );
}


function SyncRow({
  sync,
  latest,
}: {
  sync:
    KnowledgeSourceSync;

  latest: boolean;
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

    </tr>
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