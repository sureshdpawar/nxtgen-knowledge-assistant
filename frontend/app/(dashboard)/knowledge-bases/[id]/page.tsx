"use client";

import Link from "next/link";

import {
  useParams,
} from "next/navigation";

import {
  ChevronRight,
  MessageSquare,
} from "lucide-react";

import {
  useKnowledgeBase,
} from "@/features/knowledge-bases/hooks";

import KnowledgeSourceList from "@/features/knowledge-sources/components/KnowledgeSourceList";

import ChatChannelList from "@/features/chat-channels/components/ChatChannelList";


export default function KnowledgeBaseDetailPage() {
  const params = useParams<{
    id: string;
  }>();

  const id =
    params.id;

  const {
    data:
      knowledgeBase,

    isLoading,

    error,

  } = useKnowledgeBase(
    id,
  );


  if (isLoading) {
    return (
      <p className="text-slate-500">
        Loading knowledge base...
      </p>
    );
  }


  if (
    error
    || !knowledgeBase
  ) {
    return (
      <p className="text-red-600">
        Failed to load knowledge base.
      </p>
    );
  }


  return (
    <div className="space-y-8">

      <nav className="flex flex-wrap items-center gap-1 text-sm text-slate-500">

        <Link
          href="/knowledge-bases"
          className="transition hover:text-slate-900"
        >
          Knowledge Bases
        </Link>

        <ChevronRight className="h-4 w-4" />

        <span className="font-medium text-slate-900">
          {
            knowledgeBase.name
          }
        </span>

      </nav>


      <section className="rounded-2xl border bg-white p-6 shadow-sm">

        <div className="flex flex-col gap-3">

          <div className="flex flex-wrap items-center gap-3">

            <h1 className="text-3xl font-bold text-slate-900">
              {
                knowledgeBase.name
              }
            </h1>

            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
              {
                knowledgeBase.visibility
              }
            </span>

            <span
              className={
                knowledgeBase.status
                === "ACTIVE"
                  ? "rounded-full bg-green-100 px-2.5 py-1 text-xs font-medium text-green-700"
                  : "rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600"
              }
            >
              {
                knowledgeBase.status
              }
            </span>

          </div>


          <p className="text-sm text-slate-500">
            {
              knowledgeBase.description
              || "No description"
            }
          </p>


          <p className="text-xs text-slate-400">
            Knowledge Base ID:{" "}
            {
              knowledgeBase.id
            }
          </p>

        </div>

      </section>


      <section className="space-y-4">

        <div>

          <h2 className="text-xl font-semibold text-slate-900">
            Knowledge Sources
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Manage the sources that provide
            knowledge to this knowledge base.
          </p>

        </div>


        <KnowledgeSourceList
          knowledgeBaseId={
            knowledgeBase.id
          }
        />

      </section>


      <section className="border-t pt-8">

        <ChatChannelList
          knowledgeBaseId={
            knowledgeBase.id
          }
        />

      </section>


      <section className="rounded-2xl border bg-white p-6 shadow-sm">

        <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">

          <div className="flex items-start gap-4">

            <div className="rounded-xl bg-blue-100 p-3">

              <MessageSquare className="h-5 w-5 text-blue-600" />

            </div>


            <div>

              <h2 className="text-lg font-semibold text-slate-900">
                Ask this Knowledge Base
              </h2>

              <p className="mt-1 max-w-2xl text-sm text-slate-500">
                Chat searches across all active
                knowledge sources connected to
                this knowledge base.
              </p>

            </div>

          </div>


          <Link
            href={
              `/chat?knowledge_base_id=${knowledgeBase.id}`
            }
            className="inline-flex shrink-0 items-center justify-center rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
          >
            Open Chat
          </Link>

        </div>

      </section>

    </div>
  );
}