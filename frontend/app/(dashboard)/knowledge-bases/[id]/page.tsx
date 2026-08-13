"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import {
  ChevronRight,
  FileText,
  MessageSquare,
} from "lucide-react";

import {
  useKnowledgeBase,
} from "@/features/knowledge-bases/hooks";

import KnowledgeSourceList from "@/features/knowledge-sources/components/KnowledgeSourceList";


export default function KnowledgeBaseDetailPage() {
  const params = useParams<{
    id: string;
  }>();

  const id = params.id;

  const {
    data: knowledgeBase,
    isLoading,
    error,
  } = useKnowledgeBase(id);


  if (isLoading) {
    return (
      <p className="text-slate-500">
        Loading knowledge base...
      </p>
    );
  }


  if (error || !knowledgeBase) {
    return (
      <p className="text-red-600">
        Failed to load knowledge base.
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

        <span className="font-medium text-slate-900">
          Knowledge Sources
        </span>

      </nav>


      {/* Knowledge Base Header */}
      <div>

        <p className="text-sm font-medium text-slate-500">
          Knowledge Base Details
        </p>

        <h1 className="mt-1 text-3xl font-bold text-slate-900">
          {knowledgeBase.name}
        </h1>

        <p className="mt-2 text-slate-500">
          {knowledgeBase.description ||
            "No description"}
        </p>

        <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-slate-400">

          <span>
            Knowledge Base ID:{" "}
            {knowledgeBase.id}
          </span>

          <span>•</span>

          <span>
            {knowledgeBase.visibility}
          </span>

          <span>•</span>

          <span>
            {knowledgeBase.status}
          </span>

        </div>

      </div>


      {/* Knowledge Sources */}
      <section className="space-y-4">

        <div>

          <h2 className="text-xl font-semibold text-slate-900">
            Knowledge Sources
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Sources connected to this
            knowledge base.
          </p>

        </div>


        <KnowledgeSourceList
          knowledgeBaseId={
            knowledgeBase.id
          }
        />

      </section>


      {/* Documents + Chat */}
      <section className="grid gap-6 lg:grid-cols-2">

        {/* Documents */}
        <div className="rounded-xl border bg-white p-6 shadow-sm transition hover:shadow-md">

          <div className="flex items-center gap-3">

            <div className="rounded-lg bg-blue-100 p-3">
              <FileText className="h-5 w-5 text-blue-600" />
            </div>

            <h2 className="text-lg font-semibold">
              Documents
            </h2>

          </div>

          <p className="mt-4 text-sm text-slate-500">
            View and upload documents
            through the knowledge sources
            connected to this knowledge base.
          </p>

        </div>


        {/* Chat */}
        <div className="rounded-xl border bg-white p-6 shadow-sm transition hover:shadow-md">

          <div className="flex items-center gap-3">

            <div className="rounded-lg bg-blue-100 p-3">
              <MessageSquare className="h-5 w-5 text-blue-600" />
            </div>

            <h2 className="text-lg font-semibold">
              Chat
            </h2>

          </div>

          <p className="mt-4 text-sm text-slate-500">
            Ask questions against this
            knowledge base.
          </p>

        </div>

      </section>

    </div>
  );
}