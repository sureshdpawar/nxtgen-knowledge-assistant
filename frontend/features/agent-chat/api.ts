import api from "@/services/api";

import type {
  AgentChatResult,
  AgentChatResumeRequest,
  AgentChatStreamCallbacks,
  AgentChatStreamRequest,
  AgentChatProgressEvent,
} from "./types";

export async function streamAgentChat(
  payload: AgentChatStreamRequest,
  callbacks: AgentChatStreamCallbacks,
) {
  await streamAgentChatRequest(
    "/agent-chat/stream",
    payload,
    callbacks,
  );
}

export async function resumeAgentChatStream(
  payload: AgentChatResumeRequest,
  callbacks: AgentChatStreamCallbacks,
) {
  await streamAgentChatRequest(
    "/agent-chat/resume/stream",
    payload,
    callbacks,
  );
}

async function streamAgentChatRequest(
  path: string,
  payload:
    | AgentChatStreamRequest
    | AgentChatResumeRequest,
  callbacks: AgentChatStreamCallbacks,
) {
  const token =
    localStorage.getItem(
      "access_token",
    );

  const url =
    api.getUri({
      url: path,
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
    throw new Error(
      await readErrorMessage(
        response,
      ),
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
    } = await reader.read();

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

    const blocks =
      buffer.split("\n\n");

    buffer =
      blocks.pop() ?? "";

    for (const block of blocks) {
      processEventBlock(
        block,
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
  callbacks: AgentChatStreamCallbacks,
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

  const rawData =
    dataLines.join("\n");

  if (!rawData) {
    return;
  }

  let data: unknown;

  try {
    data =
      JSON.parse(
        rawData,
      );
  } catch {
    return;
  }

  if (
    eventType === "progress"
  ) {
    callbacks.onProgress?.(
      data as AgentChatProgressEvent,
    );

    return;
  }

  if (
    eventType ===
    "approval_required"
  ) {
    callbacks.onApprovalRequired(
      data as AgentChatResult,
    );

    return;
  }

  if (
    eventType === "completed"
  ) {
    callbacks.onCompleted(
      data as AgentChatResult,
    );

    return;
  }

  if (
    eventType === "error"
  ) {
    const errorPayload =
      data as {
        message?: string;
      };

    throw new Error(
      errorPayload.message
      ?? "Agent chat failed.",
    );
  }
}

async function readErrorMessage(
  response: Response,
) {
  let message =
    "Agent chat request failed.";

  try {
    const error =
      await response.json();

    message =
      error?.error?.message
      ?? error?.detail
      ?? error?.message
      ?? message;
  } catch {
    // Keep generic fallback.
  }

  return message;
}
