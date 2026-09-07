import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  assignAgentTools,
  createAgent,
  deleteAgent,
  getAgent,
  getAgentAssignedTools,
  getAgentCheckpointHistory,
  getAgentGraphState,
  getAgentRun,
  getAgentRuns,
  getAgents,
  runAgent,
  updateAgent,
  updateAgentToolPolicy,
} from "./api";

import type {
  AgentRunRequest,
  AgentToolExecutionPolicy,
  AssignAgentToolsRequest,
  CreateAgentRequest,
  UpdateAgentRequest,
} from "./types";


export function useAgents(
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "agents",
    ],
    queryFn:
      getAgents,
    enabled,
  });
}


export function useAgent(
  id: string | null,
) {
  return useQuery({
    queryKey: [
      "agents",
      id,
    ],
    queryFn: () =>
      getAgent(
        id!,
      ),
    enabled:
      Boolean(id),
  });
}


export function useCreateAgent() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      payload:
        CreateAgentRequest,
    ) =>
      createAgent(
        payload,
      ),

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "agents",
        ],
      });
    },
  });
}


export function useUpdateAgent() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data:
        UpdateAgentRequest;
    }) =>
      updateAgent(
        id,
        data,
      ),

    onSuccess(
      updatedAgent,
    ) {
      queryClient.invalidateQueries({
        queryKey: [
          "agents",
        ],
      });

      queryClient.setQueryData(
        [
          "agents",
          updatedAgent.id,
        ],
        updatedAgent,
      );
    },
  });
}


export function useDeleteAgent() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      deleteAgent,

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "agents",
        ],
      });
    },
  });
}


export function useAgentAssignedTools(
  agentId: string,
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "agent-tools",
      agentId,
    ],
    queryFn: () =>
      getAgentAssignedTools(
        agentId,
      ),
    enabled:
      Boolean(agentId)
      && enabled,
  });
}


export function useAssignAgentTools() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      agentId,
      toolIds,
    }: {
      agentId: string;
      toolIds: string[];
    }) => {
      const payload:
        AssignAgentToolsRequest = {
          tool_ids:
            toolIds,
        };

      return assignAgentTools(
        agentId,
        payload,
      );
    },

    onSuccess(
      _assignedTools,
      variables,
    ) {
      queryClient.invalidateQueries({
        queryKey: [
          "agents",
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "agents",
          variables.agentId,
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "agent-tools",
          variables.agentId,
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "tools",
        ],
      });
    },
  });
}


export function useUpdateAgentToolPolicy() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      agentId,
      toolId,
      executionPolicy,
    }: {
      agentId: string;
      toolId: string;
      executionPolicy:
        AgentToolExecutionPolicy;
    }) =>
      updateAgentToolPolicy(
        agentId,
        toolId,
        executionPolicy,
      ),

    onSuccess(
      _updatedPolicy,
      variables,
    ) {
      queryClient.invalidateQueries({
        queryKey: [
          "agent-tools",
          variables.agentId,
        ],
      });
    },
  });
}


export function useRunAgent(
  agentId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      payload:
        AgentRunRequest,
    ) =>
      runAgent(
        agentId,
        payload,
      ),

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "agent-runs",
          agentId,
        ],
      });
    },
  });
}


export function useAgentRuns(
  agentId: string | null,
) {
  return useQuery({
    queryKey: [
      "agent-runs",
      agentId,
    ],
    queryFn: () =>
      getAgentRuns(
        agentId!,
      ),
    enabled:
      Boolean(agentId),
  });
}


export function useAgentRun(
  runId: string | null,
) {
  return useQuery({
    queryKey: [
      "agent-run",
      runId,
    ],
    queryFn: () =>
      getAgentRun(
        runId!,
      ),
    enabled:
      Boolean(runId),
  });
}


export function useAgentGraphState(
  agentId: string,
  threadId: string | null,
) {
  return useQuery({
    queryKey: [
      "agent-graph-state",
      agentId,
      threadId,
    ],
    queryFn: () =>
      getAgentGraphState(
        agentId,
        threadId!,
      ),
    enabled:
      Boolean(threadId),
  });
}


export function useAgentCheckpointHistory(
  agentId: string,
  threadId: string | null,
) {
  return useQuery({
    queryKey: [
      "agent-checkpoints",
      agentId,
      threadId,
    ],
    queryFn: () =>
      getAgentCheckpointHistory(
        agentId,
        threadId!,
        20,
      ),
    enabled:
      Boolean(threadId),
  });
}
