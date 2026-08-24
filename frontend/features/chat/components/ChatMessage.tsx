import {
  Bot,
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
    message.role
    === "user";


  if (isUser) {
    return (
      <div className="flex justify-end">

        <div className="max-w-[80%] rounded-2xl rounded-br-md bg-slate-200 px-4 py-3 text-sm leading-6 text-slate-900 sm:max-w-2xl">

          <div className="whitespace-pre-wrap">
            {message.content}
          </div>

        </div>

      </div>
    );
  }


  return (
    <div className="flex items-start gap-4">

      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-600">

        <Bot className="h-4 w-4 text-white" />

      </div>


      <div className="min-w-0 flex-1">

        <div className="whitespace-pre-wrap text-sm leading-7 text-slate-800">
          {message.content}
        </div>


        {message.sources
          && message.sources.length
          > 0
          && (
            <ChatSources
              sources={
                message.sources
              }
            />
          )
        }

      </div>

    </div>
  );
}