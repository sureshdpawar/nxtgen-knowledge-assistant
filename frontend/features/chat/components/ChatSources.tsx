"use client";

import {
  ExternalLink,
  FileText,
} from "lucide-react";

import {
  openDocumentFile,
} from "@/features/documents/api";

import type {
  ChatSource,
} from "../types";


type Props = {
  sources: ChatSource[];
};


export default function ChatSources({
  sources,
}: Props) {
  if (
    sources.length === 0
  ) {
    return null;
  }


  return (
    <div className="mt-5 border-t pt-4">

      <p className="mb-3 text-sm font-medium text-slate-700">
        Sources
      </p>


      <div className="space-y-2">

        {sources.map(
          (
            source,
            index,
          ) => {
            const similarity =
              (
                source.similarity *
                100
              ).toFixed(1);


            return (
              <div
                key={`${source.document_id}-${source.chunk_index}`}
                className="flex flex-col gap-3 rounded-lg border bg-white p-3 sm:flex-row sm:items-center sm:justify-between"
              >

                <div className="flex min-w-0 items-start gap-3">

                  <FileText className="mt-0.5 h-4 w-4 shrink-0 text-blue-600" />


                  <div className="min-w-0">

                    <p className="truncate text-sm font-medium text-slate-800">
                      {index + 1}.{" "}
                      {
                        source.document_name
                      }
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      {
                        source.knowledge_source_name
                      }
                      {" • "}
                      Page{" "}
                      {source.page}
                      {" • "}
                      {similarity}%
                    </p>

                  </div>

                </div>


                <button
                  type="button"
                  onClick={() =>
                    openDocumentFile(
                      source.document_id,
                      source.page,
                    )
                  }
                  className="flex shrink-0 items-center gap-2 rounded-md border px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
                >
                  <ExternalLink className="h-3.5 w-3.5" />

                  Open
                </button>

              </div>
            );
          },
        )}

      </div>

    </div>
  );
}