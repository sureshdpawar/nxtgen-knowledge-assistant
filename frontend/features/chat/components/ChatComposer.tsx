"use client";

import {
  FormEvent,
  KeyboardEvent,
  useState,
} from "react";

import {
  Send,
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
    useState("");


  async function submit(
    event?: FormEvent,
  ) {
    event?.preventDefault();

    const value =
      message.trim();

    if (
      !value ||
      disabled
    ) {
      return;
    }

    setMessage("");

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
      event.key ===
        "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      void submit();
    }
  }


  return (
    <form
      onSubmit={submit}
      className="border-t bg-white p-4"
    >

      <div className="flex items-end gap-3">

        <textarea
          value={message}
          onChange={(event) =>
            setMessage(
              event.target.value,
            )
          }
          onKeyDown={
            handleKeyDown
          }
          rows={2}
          placeholder="Ask a question..."
          disabled={disabled}
          className="max-h-40 min-h-12 flex-1 resize-none rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 disabled:bg-slate-50"
        />


        <button
          type="submit"
          disabled={
            disabled ||
            !message.trim()
          }
          className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Send className="h-5 w-5" />
        </button>

      </div>


      <p className="mt-2 text-xs text-slate-400">
        Enter to send •
        Shift + Enter for a new line
      </p>

    </form>
  );
}