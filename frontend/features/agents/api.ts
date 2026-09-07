import api from "@/services/api";

import type { ToolDefinition } from "@/features/tools/types";

import type {
  Agent,
  AgentAssignedTool,
  AgentCheckpointHistory,
  AgentGraphState,
  AgentProgressEvent,
  AgentRun,
  AgentRunDetail,
  AgentRunRequest,
  AgentRunResponse,
  AgentToolExecutionPolicy,
  AgentToolPolicy,
  AssignAgentToolsRequest,
  CreateAgentRequest,
  UpdateAgentRequest,
} from "./types";


export async function getAgents() {
  const response = await api.get<Agent[]>("/agents");
  return response.data;
}


export async function getAgent(id: string) {
  const response = await api.get<Agent>(
    `/agents/${id}`,
  );
  return response.data;
}


export async function createAgent(
  payload: CreateAgentRequest,
) {
  const response = await api.post<Agent>(
    "/agents",
    payload,
  );
  return response.data;
}


export async function updateAgent(
  id: string,
  payload: UpdateAgentRequest,
) {
  const response = await api.put<Agent>(
    `/agents/${id}`,
    payload,
  );
  return response.data;
}


export async function deleteAgent(
  id: string,
) {
  await api.delete(
    `/agents/${id}`,
  );
}


export async function getAgentAssignedTools(
  agentId: string,
) {
  const response = await api.get<
    AgentAssignedTool[]
  >(
    `/agents/${agentId}/tools`,
  );

  return response.data;
}


export async function getAgentToolPolicies(
  agentId: string,
) {
  const response = await api.get<
    AgentToolPolicy[]
  >(
    `/agents/${agentId}/tools/policies`,
  );

  return response.data;
}


export async function assignAgentTools(
  agentId: string,
  payload: AssignAgentToolsRequest,
) {
  const response = await api.put<
    ToolDefinition[]
  >(
    `/agents/${agentId}/tools`,
    payload,
  );

  return response.data;
}


export async function updateAgentToolPolicy(
  agentId: string,
  toolId: string,
  executionPolicy:
    AgentToolExecutionPolicy,
) {
  const response = await api.put<
    AgentToolPolicy
  >(
    `/agents/${agentId}/tools/${toolId}/policy`,
    {
      execution_policy:
        executionPolicy,
    },
  );

  return response.data;
}


export async function runAgent(
  id: string,
  payload: AgentRunRequest,
) {
  const response = await api.post<
    AgentRunResponse
  >(
    `/agents/${id}/run`,
    payload,
  );

  return response.data;
}


export async function getAgentGraphState(
  agentId: string,
  threadId: string,
) {
  const response = await api.get<
    AgentGraphState
  >(
    `/agents/${agentId}/threads/${threadId}/state`,
  );

  return response.data;
}


export async function getAgentCheckpointHistory(
  agentId: string,
  threadId: string,
  limit = 20,
) {
  const response = await api.get<
    AgentCheckpointHistory
  >(
    `/agents/${agentId}/threads/${threadId}/checkpoints`,
    {
      params: {
        limit,
      },
    },
  );

  return response.data;
}


export async function runAgentStream(
  id: string,
  payload: AgentRunRequest,
  onEvent: (
    event: AgentProgressEvent,
  ) => void,
) {
  let consumedLength = 0;
  let buffer = "";

  function processBuffer() {
    while (true) {
      const boundary =
        buffer.indexOf(
          "\n\n",
        );

      if (
        boundary === -1
      ) {
        break;
      }

      const block =
        buffer.slice(
          0,
          boundary,
        );

      buffer =
        buffer.slice(
          boundary + 2,
        );

      const dataLines =
        block
          .split("\n")
          .filter(
            (line) =>
              line.startsWith(
                "data:",
              ),
          );

      if (
        dataLines.length === 0
      ) {
        continue;
      }

      const json =
        dataLines
          .map(
            (line) =>
              line
                .slice(5)
                .trimStart(),
          )
          .join("\n");

      if (!json) {
        continue;
      }

      try {
        onEvent(
          JSON.parse(
            json,
          ) as AgentProgressEvent,
        );
      } catch {
        // Ignore malformed SSE frames.
      }
    }
  }

  await api.post(
    `/agents/${id}/run/stream`,
    payload,
    {
      responseType:
        "text",
      transformResponse: [
        (data) => data,
      ],
      onDownloadProgress(
        progressEvent,
      ) {
        const event =
          progressEvent.event;

        if (!event) {
          return;
        }

        const rawEvent =
          event as ProgressEvent<
            XMLHttpRequest
          >;

        const xhr =
          rawEvent.currentTarget
          ?? rawEvent.target;

        if (
          !(
            xhr
            instanceof XMLHttpRequest
          )
        ) {
          return;
        }

        const responseText =
          xhr.responseText
          ?? "";

        if (
          responseText.length
          <= consumedLength
        ) {
          return;
        }

        buffer +=
          responseText.slice(
            consumedLength,
          );

        consumedLength =
          responseText.length;

        processBuffer();
      },
    },
  );

  processBuffer();
}


export async function getAgentRuns(
  agentId: string,
) {
  const response = await api.get<
    AgentRun[]
  >(
    `/agent-runs/agent/${agentId}`,
  );

  return response.data;
}


export async function getAgentRun(
  runId: string,
) {
  const response = await api.get<
    AgentRunDetail
  >(
    `/agent-runs/${runId}`,
  );

  return response.data;
}
