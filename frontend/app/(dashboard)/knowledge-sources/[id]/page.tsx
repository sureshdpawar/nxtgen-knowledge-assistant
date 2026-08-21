"use client";

import {
  useState,
} from "react";

import Link from "next/link";

import {
  useParams,
} from "next/navigation";

import {
  ChevronRight,
  ExternalLink,
  RefreshCw,
} from "lucide-react";

import {
  useKnowledgeSource,
  useKnowledgeSourceSyncs,
  useSyncKnowledgeSource,
} from "@/features/knowledge-sources/hooks";

import {
  useDocuments,
} from "@/features/documents/hooks";

import KnowledgeSourceSyncHistory from "@/features/knowledge-sources/components/KnowledgeSourceSyncHistory";

import DocumentList from "@/features/documents/components/DocumentList";


type Tab =
  | "overview"
  | "content"
  | "history";


export default function KnowledgeSourceDetailPage() {
  const params = useParams<{
    id: string;
  }>();

  const id = params.id;

  const [
    activeTab,
    setActiveTab,
  ] = useState<Tab>(
    "overview",
  );

  const {
    data: knowledgeSource,
    isLoading,
    error,
  } = useKnowledgeSource(
    id,
  );

  const {
    data: syncs,
  } = useKnowledgeSourceSyncs(
    id,
  );

  const {
    data: documents,
  } = useDocuments(
    id,
  );

  const syncMutation =
    useSyncKnowledgeSource(
      knowledgeSource
        ?.knowledge_base_id
      ?? "",
    );


  if (isLoading) {
    return (
      <p className="text-sm text-slate-500">
        Loading knowledge source...
      </p>
    );
  }


  if (
    error
    || !knowledgeSource
  ) {
    return (
      <p className="text-sm text-red-600">
        Failed to load knowledge source.
      </p>
    );
  }


  const isExternalSource =
    knowledgeSource.type
    === "WEBSITE"
    || knowledgeSource.type
    === "GOOGLE_DRIVE";

  const latestSync =
    syncs?.[0];

  const websiteUrl =
    knowledgeSource.type
    === "WEBSITE"
      ? String(
          knowledgeSource
            .configuration
            .base_url
          ?? "",
        )
      : null;


  async function handleSync() {
    if (
      !isExternalSource
    ) {
      return;
    }

    await syncMutation
      .mutateAsync(
        knowledgeSource.id,
      );
  }


  return (
    <div className="space-y-6">

      {/* Breadcrumb */}
      <nav className="flex flex-wrap items-center gap-1 text-sm text-slate-500">

        <Link
          href="/knowledge-bases"
          className="hover:text-slate-900"
        >
          Knowledge Bases
        </Link>

        <ChevronRight className="h-4 w-4" />

        <Link
          href={`/knowledge-bases/${knowledgeSource.knowledge_base_id}`}
          className="hover:text-slate-900"
        >
          Knowledge Sources
        </Link>

        <ChevronRight className="h-4 w-4" />

        <span className="font-medium text-slate-900">
          {knowledgeSource.name}
        </span>

      </nav>


      {/* Source Header */}
      <section className="rounded-2xl border bg-white p-6 shadow-sm">

        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">

          <div className="min-w-0">

            <div className="flex flex-wrap items-center gap-2">

              <h1 className="text-2xl font-bold text-slate-900">
                {knowledgeSource.name}
              </h1>

              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                {knowledgeSource.type}
              </span>

              <span
                className={
                  knowledgeSource.status
                  === "ACTIVE"
                    ? "rounded-full bg-green-100 px-2.5 py-1 text-xs font-medium text-green-700"
                    : knowledgeSource.status
                      === "ERROR"
                      ? "rounded-full bg-red-100 px-2.5 py-1 text-xs font-medium text-red-700"
                      : "rounded-full bg-amber-100 px-2.5 py-1 text-xs font-medium text-amber-700"
                }
              >
                {knowledgeSource.status}
              </span>

            </div>


            {websiteUrl && (
              <a
                href={
                  websiteUrl
                }
                target="_blank"
                rel="noreferrer"
                className="mt-3 flex w-fit items-center gap-1.5 break-all text-sm text-blue-600 hover:underline"
              >
                {websiteUrl}

                <ExternalLink className="h-3.5 w-3.5 shrink-0" />
              </a>
            )}


            <p className="mt-3 text-xs text-slate-400">
              {
                isExternalSource
                  ? (
                    knowledgeSource
                      .last_sync_at
                      ? (
                        "Last synced "
                        + new Date(
                            knowledgeSource
                              .last_sync_at,
                          ).toLocaleString()
                      )
                      : "Never synced"
                  )
                  : (
                    "Created "
                    + new Date(
                        knowledgeSource
                          .created_at,
                      ).toLocaleString()
                  )
              }
            </p>

          </div>


          {isExternalSource && (
            <button
              type="button"
              onClick={
                handleSync
              }
              disabled={
                syncMutation.isPending
              }
              className="flex shrink-0 items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <RefreshCw
                className={
                  syncMutation.isPending
                    ? "h-4 w-4 animate-spin"
                    : "h-4 w-4"
                }
              />

              {
                syncMutation.isPending
                  ? "Syncing..."
                  : "Sync Now"
              }
            </button>
          )}

        </div>

      </section>


      {/* Tabs */}
      <div className="border-b">

        <nav className="flex gap-6">

          <TabButton
            label="Overview"
            active={
              activeTab
              === "overview"
            }
            onClick={() =>
              setActiveTab(
                "overview",
              )
            }
          />

          <TabButton
            label={
              isExternalSource
                ? "Content"
                : "Documents"
            }
            active={
              activeTab
              === "content"
            }
            onClick={() =>
              setActiveTab(
                "content",
              )
            }
          />

          {isExternalSource && (
            <TabButton
              label="Sync History"
              active={
                activeTab
                === "history"
              }
              onClick={() =>
                setActiveTab(
                  "history",
                )
              }
            />
          )}

        </nav>

      </div>


      {/* Overview */}
      {activeTab === "overview" && (
        <OverviewTab
          external={
            isExternalSource
          }
          latestSync={
            latestSync
          }
          documents={
            documents
          }
          onViewHistory={() =>
            setActiveTab(
              "history",
            )
          }
        />
      )}


      {/* Content / Documents */}
      {activeTab === "content" && (
        <DocumentList
          knowledgeSourceId={
            knowledgeSource.id
          }
          allowUpload={
            !isExternalSource
          }
          allowManualProcess={
            !isExternalSource
          }
          allowDelete
          emptyTitle={
            isExternalSource
              ? "No indexed content"
              : "No documents"
          }
          emptyDescription={
            isExternalSource
              ? "Run Sync Now to discover and index content."
              : "Upload a document to this knowledge source."
          }
        />
      )}


      {/* Sync History */}
      {activeTab === "history"
        && isExternalSource
        && (
          <KnowledgeSourceSyncHistory
            knowledgeSourceId={
              knowledgeSource.id
            }
          />
        )}

    </div>
  );
}


function TabButton({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={
        onClick
      }
      className={[
        "border-b-2 px-1 pb-3 text-sm font-medium transition",
        active
          ? "border-blue-600 text-blue-600"
          : "border-transparent text-slate-500 hover:text-slate-900",
      ].join(" ")}
    >
      {label}
    </button>
  );
}


function OverviewTab({
  external,
  latestSync,
  documents,
  onViewHistory,
}: {
  external: boolean;

  latestSync:
    | {
        status: string;
        items_discovered: number;
        items_new: number;
        items_changed: number;
        items_unchanged: number;
        items_missing: number;
        items_failed: number;
        completed_at: string | null;
      }
    | undefined;

  documents:
    | Array<{
        status: string;
      }>
    | undefined;

  onViewHistory: () => void;
}) {

  /*
   * UPLOAD source overview
   */
  if (!external) {
    const total =
      documents?.length
      ?? 0;

    const ready =
      documents?.filter(
        (document) =>
          document.status
          === "READY",
      ).length
      ?? 0;

    const processing =
      documents?.filter(
        (document) =>
          document.status
          === "PROCESSING"
          || document.status
          === "PENDING",
      ).length
      ?? 0;

    const failed =
      documents?.filter(
        (document) =>
          document.status
          === "FAILED",
      ).length
      ?? 0;

    return (
      <div className="space-y-4">

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <SummaryCard
            label="Documents"
            value={
              total
            }
          />

          <SummaryCard
            label="Ready"
            value={
              ready
            }
          />

          <SummaryCard
            label="Processing"
            value={
              processing
            }
          />

          <SummaryCard
            label="Failed"
            value={
              failed
            }
          />

        </div>


        <div className="rounded-xl border bg-white p-5">

          {total === 0 ? (
            <p className="text-sm text-slate-500">
              No documents have been
              uploaded yet. Open the
              Documents tab to add files.
            </p>
          ) : (
            <div className="flex flex-wrap items-center justify-between gap-4">

              <p className="text-sm text-slate-500">
                <span className="font-medium text-slate-900">
                  {ready} of {total}
                </span>
                {" "}
                documents are indexed and
                available to Chat.
              </p>

              {failed > 0 && (
                <p className="text-sm font-medium text-red-600">
                  {failed} failed
                </p>
              )}

            </div>
          )}

        </div>

      </div>
    );
  }


  /*
   * External source overview
   */
  if (!latestSync) {
    return (
      <div className="rounded-xl border border-dashed bg-white p-8 text-center">

        <h2 className="font-semibold text-slate-900">
          No sync yet
        </h2>

        <p className="mt-2 text-sm text-slate-500">
          Use Sync Now to discover
          content from this source.
        </p>

      </div>
    );
  }


  return (
    <div className="space-y-4">

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

        <SummaryCard
          label="Indexed"
          value={
            latestSync
              .items_discovered
          }
        />

        <SummaryCard
          label="Latest Sync"
          value={
            latestSync.status
          }
        />

        <SummaryCard
          label="Changed"
          value={
            latestSync
              .items_changed
          }
        />

        <SummaryCard
          label="Failed"
          value={
            latestSync
              .items_failed
          }
        />

      </div>


      <div className="rounded-xl border bg-white p-5">

        <div className="flex flex-wrap items-center justify-between gap-4">

          <p className="text-sm text-slate-500">
            {
              latestSync.items_new
            } new ·{" "}
            {
              latestSync.items_changed
            } changed ·{" "}
            {
              latestSync.items_unchanged
            } unchanged ·{" "}
            {
              latestSync.items_missing
            } missing
          </p>

          <button
            type="button"
            onClick={
              onViewHistory
            }
            className="text-sm font-medium text-blue-600 hover:underline"
          >
            View sync history
          </button>

        </div>

      </div>

    </div>
  );
}


function SummaryCard({
  label,
  value,
}: {
  label: string;
  value:
    | string
    | number;
}) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">

      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="mt-2 text-2xl font-semibold text-slate-900">
        {value}
      </p>

    </div>
  );
}