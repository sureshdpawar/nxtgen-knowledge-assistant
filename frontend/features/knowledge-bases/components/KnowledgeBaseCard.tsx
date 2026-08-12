import Link from "next/link";

import {
  Database,
  Pencil,
  Trash2,
} from "lucide-react";

import type {
  KnowledgeBase,
} from "../types";

type Props = {
  knowledgeBase: KnowledgeBase;

  onEdit: (
    knowledgeBase: KnowledgeBase,
  ) => void;

  onDelete: (
    knowledgeBase: KnowledgeBase,
  ) => void;
};

export default function KnowledgeBaseCard({
  knowledgeBase,
  onEdit,
  onDelete,
}: Props) {
  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm transition hover:shadow-md">
      <Link
        href={`/knowledge-bases/${knowledgeBase.id}`}
        className="block"
      >
        <div className="flex gap-4">
          <div className="rounded-lg bg-blue-100 p-3">
            <Database className="h-6 w-6 text-blue-600" />
          </div>

          <div>
            <h2 className="text-lg font-semibold">
              {knowledgeBase.name}
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              {knowledgeBase.description ||
                "No description"}
            </p>

            <p className="mt-4 text-xs text-slate-400">
              Created{" "}
              {new Date(
                knowledgeBase.created_at,
              ).toLocaleDateString()}
            </p>
          </div>
        </div>
      </Link>

      <div className="mt-6 flex justify-end gap-2">
        <button
          type="button"
          onClick={() =>
            onEdit(knowledgeBase)
          }
          className="flex items-center gap-2 rounded-lg border px-4 py-2 text-sm hover:bg-slate-100"
        >
          <Pencil className="h-4 w-4" />
          Edit
        </button>

        <button
          type="button"
          onClick={() =>
            onDelete(
              knowledgeBase,
            )
          }
          className="flex items-center gap-2 rounded-lg border border-red-200 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
        >
          <Trash2 className="h-4 w-4" />
          Delete
        </button>
      </div>
    </div>
  );
}