import {
  Bot,
  User,
} from "lucide-react";

import type {
  ChatMessage as ChatMessageType,
} from "../types";

import ChatSources from "./ChatSources";


type Props = {
  message:
    ChatMessageType;
};


export default function ChatMessage({
  message,
}: Props) {
  const isUser =
    message.role === "user";


  return (
    <div
      className={
        isUser
          ? "flex justify-end"
          : "flex justify-start"
      }
    >

      <div
        className={
          isUser
            ? "max-w-3xl rounded-2xl bg-blue-600 px-5 py-4 text-white"
            : "w-full max-w-4xl rounded-2xl border bg-white px-5 py-4 shadow-sm"
        }
      >

        <div className="flex items-start gap-3">

          {!isUser && (
            <div className="rounded-full bg-blue-100 p-2">
              <Bot className="h-4 w-4 text-blue-600" />
            </div>
          )}


          <div className="min-w-0 flex-1">

            <div
              className={
                isUser
                  ? "whitespace-pre-wrap text-sm leading-6"
                  : "whitespace-pre-wrap text-sm leading-7 text-slate-800"
              }
            >
              {message.content}
            </div>


            {!isUser &&
              message.sources &&
              message.sources.length >
                0 && (
                <ChatSources
                  sources={
                    message.sources
                  }
                />
              )}

          </div>


          {isUser && (
            <User className="mt-0.5 h-4 w-4 shrink-0" />
          )}

        </div>

      </div>

    </div>
  );
}