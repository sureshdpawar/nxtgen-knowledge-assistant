import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  assignAgentTools,
  createAgent,
  deleteAgent,
  getAgent,
  getAgentCheckpointHistory,
  getAgentGraphState,
  getAgentRun,
  getAgentRuns,
  getAgents,
  resumeAgent,
  runAgent,
  updateAgent,
} from "./api";

import type {
  AgentResumeRequest,
  AgentRunRequest,
  AssignAgentToolsRequest,
  CreateAgentRequest,
  UpdateAgentRequest,
} from "./types";

export function useAgents(enabled = true) {
  return useQuery({ queryKey: ["agents"], queryFn: getAgents, enabled });
}

export function useAgent(id: string | null) {
  return useQuery({
    queryKey: ["agents", id],
    queryFn: () => getAgent(id!),
    enabled: Boolean(id),
  });
}

export function useCreateAgent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateAgentRequest) => createAgent(payload),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
  });
}

export function useUpdateAgent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateAgentRequest }) =>
      updateAgent(id, data),
    onSuccess(updatedAgent) {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
      queryClient.setQueryData(["agents", updatedAgent.id], updatedAgent);
    },
  });
}

export function useDeleteAgent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteAgent,
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
  });
}

export function useAssignAgentTools() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ agentId, toolIds }: { agentId: string; toolIds: string[] }) => {
      const payload: AssignAgentToolsRequest = { tool_ids: toolIds };
      return assignAgentTools(agentId, payload);
    },
    onSuccess(_assignedTools, variables) {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
      queryClient.invalidateQueries({ queryKey: ["agents", variables.agentId] });
      queryClient.invalidateQueries({ queryKey: ["tools"] });
    },
  });
}

export function useRunAgent(agentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: AgentRunRequest) => runAgent(agentId, payload),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: ["agent-runs", agentId] });
    },
  });
}

export function useResumeAgent(agentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ runId, payload }: { runId: string; payload: AgentResumeRequest }) =>
      resumeAgent(agentId, runId, payload),
    onSuccess(result) {
      queryClient.invalidateQueries({ queryKey: ["agent-runs", agentId] });
      queryClient.invalidateQueries({ queryKey: ["agent-run", result.run_id] });
      queryClient.invalidateQueries({ queryKey: ["agent-graph-state", agentId, result.thread_id] });
      queryClient.invalidateQueries({ queryKey: ["agent-checkpoints", agentId, result.thread_id] });
    },
  });
}

export function useAgentRuns(agentId: string | null) {
  return useQuery({
    queryKey: ["agent-runs", agentId],
    queryFn: () => getAgentRuns(agentId!),
    enabled: Boolean(agentId),
  });
}

export function useAgentRun(runId: string | null) {
  return useQuery({
    queryKey: ["agent-run", runId],
    queryFn: () => getAgentRun(runId!),
    enabled: Boolean(runId),
  });
}

export function useAgentGraphState(agentId: string, threadId: string | null) {
  return useQuery({
    queryKey: ["agent-graph-state", agentId, threadId],
    queryFn: () => getAgentGraphState(agentId, threadId!),
    enabled: Boolean(threadId),
  });
}

export function useAgentCheckpointHistory(agentId: string, threadId: string | null) {
  return useQuery({
    queryKey: ["agent-checkpoints", agentId, threadId],
    queryFn: () => getAgentCheckpointHistory(agentId, threadId!, 20),
    enabled: Boolean(threadId),
  });
}
