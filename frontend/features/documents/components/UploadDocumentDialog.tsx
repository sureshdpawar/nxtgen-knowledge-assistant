"use client";

import {
  useState,
} from "react";

import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";


type Props = {
  onUpload:
    (file: File) =>
      Promise<void>;
};


const ACCEPTED_EXTENSIONS = [
  ".pdf",
  ".txt",
  ".md",
  ".csv",
  ".doc",
  ".docx",
  ".ppt",
  ".pptx",
  ".xls",
  ".xlsx",
].join(",");


export default function UploadDocumentDialog({
  onUpload,
}: Props) {
  const [
    open,
    setOpen,
  ] =
    useState(false);

  const [
    file,
    setFile,
  ] =
    useState<File | null>(
      null,
    );

  const [
    uploading,
    setUploading,
  ] =
    useState(false);


  async function submit() {
    if (!file) {
      return;
    }

    try {
      setUploading(true);

      await onUpload(
        file,
      );

      setFile(
        null,
      );

      setOpen(
        false,
      );
    } finally {
      setUploading(
        false,
      );
    }
  }


  return (
    <>

      <button
        type="button"
        onClick={() =>
          setOpen(
            true,
          )
        }
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        + Upload Document
      </button>


      <Dialog
        open={
          open
        }
        onOpenChange={
          setOpen
        }
      >

        <DialogContent>

          <DialogHeader>
            <DialogTitle>
              Upload Document
            </DialogTitle>
          </DialogHeader>


          <div className="space-y-4">

            <div>

              <input
                type="file"
                accept={
                  ACCEPTED_EXTENSIONS
                }
                onChange={(
                  event,
                ) =>
                  setFile(
                    event
                      .target
                      .files?.[0]
                    ?? null,
                  )
                }
                className="block w-full text-sm"
              />

              <p className="mt-2 text-xs text-slate-500">
                Supported: PDF, TXT,
                Markdown, CSV, Word,
                PowerPoint and Excel.
              </p>

              <p className="mt-1 text-xs text-slate-400">
                Word: .doc, .docx ·
                PowerPoint: .ppt, .pptx ·
                Excel: .xls, .xlsx
              </p>

            </div>


            {file && (
              <div className="rounded-lg bg-slate-50 p-3 text-sm">

                <div className="font-medium">
                  {file.name}
                </div>

                <div className="mt-1 text-xs text-slate-500">
                  {(
                    file.size
                    / 1024
                    / 1024
                  ).toFixed(
                    2,
                  )}{" "}
                  MB
                </div>

              </div>
            )}

          </div>


          <DialogFooter>

            <button
              type="button"
              onClick={
                submit
              }
              disabled={
                !file
                || uploading
              }
              className="rounded-lg bg-blue-600 px-5 py-2 text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              {
                uploading
                  ? "Uploading..."
                  : "Upload"
              }
            </button>

          </DialogFooter>

        </DialogContent>

      </Dialog>

    </>
  );
}