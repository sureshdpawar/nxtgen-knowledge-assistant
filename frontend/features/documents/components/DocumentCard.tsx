import {
  Check,
  FileText,
  Play,
  RotateCcw,
  Trash2,
} from "lucide-react";

import type {
  Document,
} from "../types";


type Props = {
  document: Document;

  onProcess: (
    document: Document,
  ) => void;

  onDelete: (
    document: Document,
  ) => void;

  processing: boolean;
};


export default function DocumentCard({
  document,
  onProcess,
  onDelete,
  processing,
}: Props) {
  const sizeInMb = (
    document.file_size /
    1024 /
    1024
  ).toFixed(2);


  const isReady =
    document.status === "READY";

  const isFailed =
    document.status === "FAILED";

  const isBackendProcessing =
    document.status === "PROCESSING";

  const isProcessing =
    processing ||
    isBackendProcessing;


  function getProcessLabel() {
    if (isProcessing) {
      return "Processing...";
    }

    if (isReady) {
      return "Processed";
    }

    if (isFailed) {
      return "Reprocess";
    }

    return "Process";
  }


  function ProcessIcon() {
    if (isReady) {
      return (
        <Check className="h-4 w-4" />
      );
    }

    if (isFailed) {
      return (
        <RotateCcw className="h-4 w-4" />
      );
    }

    return (
      <Play className="h-4 w-4" />
    );
  }


  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">

      <div className="flex items-start gap-4">

        <div className="rounded-lg bg-blue-100 p-3">
          <FileText className="h-5 w-5 text-blue-600" />
        </div>


        <div className="min-w-0 flex-1">

          <h3 className="truncate font-semibold text-slate-900">
            {document.original_filename}
          </h3>


          <p className="mt-1 break-all text-xs text-slate-400">
            Document ID:{" "}
            {document.id}
          </p>


          <p className="mt-2 text-sm text-slate-500">
            {sizeInMb} MB
          </p>


          <div className="mt-3">
            <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">
              {document.status}
            </span>
          </div>

        </div>

      </div>


      <div className="mt-5 flex justify-end gap-2">

        <button
          type="button"
          onClick={() =>
            onProcess(document)
          }
          disabled={
            isReady ||
            isProcessing
          }
          className="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <ProcessIcon />

          {getProcessLabel()}
        </button>


        <button
          type="button"
          onClick={() =>
            onDelete(document)
          }
          disabled={isProcessing}
          className="flex items-center gap-2 rounded-lg border border-red-200 px-3 py-2 text-sm text-red-600 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Trash2 className="h-4 w-4" />

          Delete
        </button>

      </div>

    </div>
  );
}