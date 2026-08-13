"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { ChevronRight } from "lucide-react";

import {
  useKnowledgeSource,
} from "@/features/knowledge-sources/hooks";

import DocumentList from "@/features/documents/components/DocumentList";


export default function KnowledgeSourceDetailPage() {
  const params = useParams<{
    id: string;
  }>();

  const id = params.id;


  const {
    data: knowledgeSource,
    isLoading,
    error,
  } = useKnowledgeSource(id);


  if (isLoading) {
    return (
      <p className="text-slate-500">
        Loading knowledge source...
      </p>
    );
  }


  if (error || !knowledgeSource) {
    return (
      <p className="text-red-600">
        Failed to load knowledge source.
      </p>
    );
  }


  return (
    <div className="space-y-8">

      {/* Breadcrumb */}
      <nav className="flex flex-wrap items-center gap-1 text-sm text-slate-500">

        <Link
          href="/knowledge-bases"
          className="transition hover:text-slate-900"
        >
          Knowledge Bases
        </Link>

        <ChevronRight className="h-4 w-4" />

        <Link
          href={`/knowledge-bases/${knowledgeSource.knowledge_base_id}`}
          className="transition hover:text-slate-900"
        >
          Knowledge Sources
        </Link>

        <ChevronRight className="h-4 w-4" />

        <span className="font-medium text-slate-900">
          Documents
        </span>

      </nav>


      {/* Knowledge Source Header */}
      <div>

        <p className="text-sm font-medium text-slate-500">
          Knowledge Source Details
        </p>

        <h1 className="mt-1 text-3xl font-bold text-slate-900">
          {knowledgeSource.name}
        </h1>

        <p className="mt-2 text-xs text-slate-400">
          Knowledge Source ID:{" "}
          {knowledgeSource.id}
        </p>

        <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-slate-400">

          <span>
            {knowledgeSource.type}
          </span>

          <span>•</span>

          <span>
            {knowledgeSource.status}
          </span>

          {knowledgeSource.last_sync_at && (
            <>
              <span>•</span>

              <span>
                Last Sync:{" "}
                {new Date(
                  knowledgeSource.last_sync_at,
                ).toLocaleString()}
              </span>
            </>
          )}

        </div>

      </div>


      {/* Documents */}
      <section className="space-y-4">

        <div>

          <h2 className="text-xl font-semibold text-slate-900">
            Documents
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Documents uploaded to this
            knowledge source.
          </p>

        </div>


        <DocumentList
          knowledgeSourceId={
            knowledgeSource.id
          }
        />

      </section>

    </div>
  );
}