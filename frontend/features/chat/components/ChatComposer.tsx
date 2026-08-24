"use client";

import {
  FormEvent,
  KeyboardEvent,
  useState,
} from "react";

import {
  ArrowUp,
} from "lucide-react";


type Props = {
  onSend: (
    message: string,
  ) => Promise<void>;

  disabled: boolean;
};


export default function ChatComposer({
  onSend,
  disabled,
}: Props) {
  const [
    message,
    setMessage,
  ] =
    useState(
      "",
    );


  async function submit(
    event?: FormEvent,
  ) {
    event?.preventDefault();

    const value =
      message.trim();

    if (
      !value
      || disabled
    ) {
      return;
    }

    setMessage(
      "",
    );

    await onSend(
      value,
    );
  }


  function handleKeyDown(
    event:
      KeyboardEvent<
        HTMLTextAreaElement
      >,
  ) {
    if (
      event.key
      === "Enter"
      && !event.shiftKey
    ) {
      event.preventDefault();

      void submit();
    }
  }


  return (
    <div className="shrink-0 border-t border-slate-200 bg-white">

      <form
        onSubmit={
          submit
        }
        className="mx-auto w-full max-w-4xl px-4 pb-4 pt-3 sm:px-6"
      >

        <div className="rounded-2xl border border-slate-200 bg-white p-2 shadow-sm transition focus-within:border-slate-300 focus-within:shadow-md">

          <div className="flex items-end gap-2">

            <textarea
              value={
                message
              }
              onChange={(
                event,
              ) =>
                setMessage(
                  event.target.value,
                )
              }
              onKeyDown={
                handleKeyDown
              }
              rows={
                1
              }
              placeholder={
                disabled
                  ? "Select a knowledge base to start..."
                  : "Ask anything about your knowledge base..."
              }
              disabled={
                disabled
              }
              className="max-h-40 min-h-11 flex-1 resize-none border-0 bg-transparent px-3 py-3 text-sm leading-5 text-slate-800 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed"
            />


            <button
              type="submit"
              disabled={
                disabled
                || !message.trim()
              }
              aria-label="Send message"
              className="mb-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-900 text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
            >

              <ArrowUp className="h-4 w-4" />

            </button>

          </div>

        </div>


        <p className="mt-2 text-center text-[11px] text-slate-400">
          Enter to send ·
          Shift + Enter for a new line
        </p>

      </form>

    </div>
  );
}