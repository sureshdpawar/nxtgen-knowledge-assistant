"use client";

import Link from "next/link";

import {
  Database,
  Pencil,
  RefreshCw,
  Trash2,
} from "lucide-react";

import type {
  KnowledgeSource,
} from "../types";


type Props = {
  knowledgeSource:
    KnowledgeSource;

  onEdit: (
    knowledgeSource:
      KnowledgeSource,
  ) => void;

  onDelete: (
    knowledgeSource:
      KnowledgeSource,
  ) => void;

  onSync: (
    knowledgeSource:
      KnowledgeSource,
  ) => Promise<void>;

  isSyncing?: boolean;
};


export default function KnowledgeSourceCard({
  knowledgeSource,
  onEdit,
  onDelete,
  onSync,
  isSyncing = false,
}: Props) {
  const canSync =
    knowledgeSource.type
    === "WEBSITE"
    || knowledgeSource.type
    === "GOOGLE_DRIVE";

  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm transition hover:shadow-md">

      <Link
        href={`/knowledge-sources/${knowledgeSource.id}`}
        className="block"
      >
        <div className="flex items-start gap-4">

          <div className="rounded-lg bg-blue-100 p-3">
            <Database className="h-5 w-5 text-blue-600" />
          </div>

          <div className="min-w-0 flex-1">

            <h3 className="font-semibold text-slate-900">
              {knowledgeSource.name}
            </h3>

            <div className="mt-2 flex flex-wrap gap-2 text-xs">

              <span className="rounded-full bg-slate-100 px-2 py-1 text-slate-600">
                {knowledgeSource.type}
              </span>

              <span
                className={
                  knowledgeSource.status
                  === "ACTIVE"
                    ? "rounded-full bg-green-100 px-2 py-1 text-green-700"
                    : knowledgeSource.status
                    === "ERROR"
                      ? "rounded-full bg-red-100 px-2 py-1 text-red-700"
                      : "rounded-full bg-amber-100 px-2 py-1 text-amber-700"
                }
              >
                {knowledgeSource.status}
              </span>

            </div>

            {knowledgeSource.type
              === "WEBSITE"
              && (
                <p className="mt-3 truncate text-xs text-slate-500">
                  {
                    String(
                      knowledgeSource
                        .configuration
                        .base_url
                      ?? "",
                    )
                  }
                </p>
              )}

            <p className="mt-3 text-xs text-slate-400">
              Created{" "}
              {new Date(
                knowledgeSource.created_at,
              ).toLocaleDateString()}
            </p>

            <p className="mt-1 text-xs text-slate-400">
              Last sync:{" "}
              {
                knowledgeSource.last_sync_at
                  ? new Date(
                      knowledgeSource.last_sync_at,
                    ).toLocaleString()
                  : "Never"
              }
            </p>

          </div>

        </div>
      </Link>

      <div className="mt-5 flex flex-wrap justify-end gap-2">

        {canSync && (
          <button
            type="button"
            disabled={isSyncing}
            onClick={() =>
              onSync(
                knowledgeSource,
              )
            }
            className="flex items-center gap-2 rounded-lg border border-blue-200 px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RefreshCw
              className={
                isSyncing
                  ? "h-4 w-4 animate-spin"
                  : "h-4 w-4"
              }
            />

            {
              isSyncing
                ? "Syncing..."
                : "Sync Now"
            }
          </button>
        )}

        <button
          type="button"
          onClick={() =>
            onEdit(
              knowledgeSource,
            )
          }
          className="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-slate-100"
        >
          <Pencil className="h-4 w-4" />
          Edit
        </button>

        <button
          type="button"
          onClick={() =>
            onDelete(
              knowledgeSource,
            )
          }
          className="flex items-center gap-2 rounded-lg border border-red-200 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
        >
          <Trash2 className="h-4 w-4" />
          Delete
        </button>

      </div>

    </div>
  );
}