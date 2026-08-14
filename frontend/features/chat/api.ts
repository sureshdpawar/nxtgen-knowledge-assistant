import api from "@/services/api";

import type {
  ChatStreamCallbacks,
  ChatStreamMetadata,
  ChatStreamRequest,
} from "./types";


export async function streamChat(
  payload: ChatStreamRequest,
  callbacks: ChatStreamCallbacks,
) {
  const token =
    localStorage.getItem(
      "access_token",
    );

  const url =
    api.getUri({
      url: "/chat/stream",
    });

  const response =
    await fetch(
      url,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",

          ...(token
            ? {
                Authorization:
                  `Bearer ${token}`,
              }
            : {}),
        },

        body:
          JSON.stringify(
            payload,
          ),
      },
    );


  if (!response.ok) {
    let message =
      "Chat request failed.";

    try {
      const error =
        await response.json();

      message =
        error?.error?.message ??
        error?.detail ??
        error?.message ??
        message;

    } catch {
      // Keep generic fallback.
    }

    throw new Error(
      message,
    );
  }


  if (!response.body) {
    throw new Error(
      "Streaming response is unavailable.",
    );
  }


  const reader =
    response.body.getReader();

  const decoder =
    new TextDecoder();

  let buffer = "";


  while (true) {
    const {
      value,
      done,
    } =
      await reader.read();

    if (done) {
      break;
    }

    buffer +=
      decoder.decode(
        value,
        {
          stream: true,
        },
      );


    const events =
      buffer.split("\n\n");

    buffer =
      events.pop() ?? "";


    for (
      const eventBlock
      of events
    ) {
      processEventBlock(
        eventBlock,
        callbacks,
      );
    }
  }


  if (buffer.trim()) {
    processEventBlock(
      buffer,
      callbacks,
    );
  }
}


function processEventBlock(
  block: string,
  callbacks:
    ChatStreamCallbacks,
) {
  const lines =
    block.split("\n");

  let eventType =
    "message";

  const dataLines:
    string[] = [];


  for (const line of lines) {
    if (
      line.startsWith(
        "event:",
      )
    ) {
      eventType =
        line
          .slice(
            "event:".length,
          )
          .trim();

      continue;
    }


    if (
      line.startsWith(
        "data:",
      )
    ) {
      let data =
        line.slice(
          "data:".length,
        );


      /*
       * SSE allows:
       *
       * data: hello
       *
       * Remove one separator space,
       * but preserve meaningful spaces
       * inside streamed tokens.
       */
      if (
        data.startsWith(" ")
      ) {
        data =
          data.slice(1);
      }


      dataLines.push(
        data,
      );
    }
  }


  const data =
    dataLines.join("\n");


  if (
    eventType ===
    "metadata"
  ) {
    const metadata =
      JSON.parse(
        data,
      ) as ChatStreamMetadata;

    callbacks.onMetadata(
      metadata,
    );

    return;
  }


  if (
    eventType ===
    "done"
  ) {
    return;
  }


  callbacks.onToken(
    data,
  );
}