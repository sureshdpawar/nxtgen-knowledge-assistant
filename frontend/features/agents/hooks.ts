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
  getAgentRun,
  getAgentRuns,
  getAgents,
  runAgent,
  updateAgent,
} from "./api";

import type {
  AgentRunRequest,
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
      Boolean(
        id,
      ),
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
          "tools",
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
      Boolean(
        agentId,
      ),
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
      Boolean(
        runId,
      ),
  });
}