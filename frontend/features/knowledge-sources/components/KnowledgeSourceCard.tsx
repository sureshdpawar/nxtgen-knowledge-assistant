import {
  Database,
  Pencil,
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
};

export default function KnowledgeSourceCard({
  knowledgeSource,
  onEdit,
  onDelete,
}: Props) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">

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

            <span className="rounded-full bg-green-100 px-2 py-1 text-green-700">
              {knowledgeSource.status}
            </span>

          </div>

          <p className="mt-3 text-xs text-slate-400">
            Created{" "}
            {new Date(
              knowledgeSource.created_at,
            ).toLocaleDateString()}
          </p>

        </div>

      </div>

      <div className="mt-5 flex justify-end gap-2">

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