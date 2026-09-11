import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import api from "@/services/api";


export interface AgentA2AConnection {
  target_agent_id: string;
  target_agent_name: string;
  target_agent_description: string | null;
  target_agent_status: string;
  protocol: "A2A";
  protocol_version: "1.0";
}


export async function getAgentA2AConnections(
  agentId: string,
) {
  const response = await api.get<
    AgentA2AConnection[]
  >(
    `/agents/${agentId}/connected-agents`,
  );

  return response.data;
}


export async function replaceAgentA2AConnections(
  agentId: string,
  targetAgentIds: string[],
) {
  const response = await api.put<
    AgentA2AConnection[]
  >(
    `/agents/${agentId}/connected-agents`,
    {
      target_agent_ids:
        targetAgentIds,
    },
  );

  return response.data;
}


export function useAgentA2AConnections(
  agentId: string,
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "agent-a2a-connections",
      agentId,
    ],
    queryFn: () =>
      getAgentA2AConnections(
        agentId,
      ),
    enabled:
      Boolean(agentId)
      && enabled,
  });
}


export function useReplaceAgentA2AConnections() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      agentId,
      targetAgentIds,
    }: {
      agentId: string;
      targetAgentIds: string[];
    }) =>
      replaceAgentA2AConnections(
        agentId,
        targetAgentIds,
      ),

    onSuccess(
      _connections,
      variables,
    ) {
      queryClient.invalidateQueries({
        queryKey: [
          "agent-a2a-connections",
          variables.agentId,
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "agents",
        ],
      });
    },
  });
}
