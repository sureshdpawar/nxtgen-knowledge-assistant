"use client";

import {
  ExternalLink,
  FileText,
} from "lucide-react";

import {
  openDocumentFile,
} from "@/features/documents/api";

import type {
  SearchResult,
} from "../types";


type Props = {
  result: SearchResult;
};


export default function SearchResultCard({
  result,
}: Props) {
  const similarity = (
    result.similarity *
    100
  ).toFixed(1);


  async function handleOpenDocument() {
    await openDocumentFile(
      result.document_id,
      result.page,
    );
  }


  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">

      <div className="flex items-start gap-4">

        <div className="rounded-lg bg-blue-100 p-3">
          <FileText className="h-5 w-5 text-blue-600" />
        </div>


        <div className="min-w-0 flex-1">

          <h3 className="font-semibold text-slate-900">
            {result.document_name}
          </h3>


          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500">

            <span>
              Source:{" "}
              <strong>
                {
                  result
                    .knowledge_source_name
                }
              </strong>
            </span>

            <span>•</span>

            <span>
              Page {result.page}
            </span>

            <span>•</span>

            <span>
              Similarity{" "}
              {similarity}%
            </span>

          </div>

        </div>

      </div>


      <div className="mt-5 rounded-lg bg-slate-50 p-4">

        <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">
          {result.text}
        </p>

      </div>


      <div className="mt-5 flex justify-between gap-4">

        <div className="space-y-1 text-xs text-slate-400">

          <p className="break-all">
            Document ID:{" "}
            {result.document_id}
          </p>

          <p>
            Chunk Index:{" "}
            {result.chunk_index}
          </p>

        </div>


        <button
          type="button"
          onClick={
            handleOpenDocument
          }
          className="flex shrink-0 items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
        >
          <ExternalLink className="h-4 w-4" />

          Open Document
        </button>

      </div>

    </div>
  );
}