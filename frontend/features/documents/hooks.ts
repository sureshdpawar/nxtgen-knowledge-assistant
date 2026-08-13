import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  deleteDocument,
  getDocument,
  getDocuments,
  processDocument,
  uploadDocument,
} from "./api";

export function useDocuments(
  knowledgeSourceId: string,
) {
  return useQuery({
    queryKey: [
      "documents",
      knowledgeSourceId,
    ],

    queryFn: () =>
      getDocuments(
        knowledgeSourceId,
      ),

    enabled:
      !!knowledgeSourceId,
  });
}

export function useDocument(
  documentId: string,
) {
  return useQuery({
    queryKey: [
      "document",
      documentId,
    ],

    queryFn: () =>
      getDocument(
        documentId,
      ),

    enabled:
      !!documentId,
  });
}

export function useUploadDocument(
  knowledgeSourceId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      file: File,
    ) =>
      uploadDocument(
        knowledgeSourceId,
        file,
      ),

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "documents",
          knowledgeSourceId,
        ],
      });
    },
  });
}

export function useProcessDocument(
  knowledgeSourceId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      processDocument,

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: [
          "documents",
          knowledgeSourceId,
        ],
      });

      await queryClient.refetchQueries({
        queryKey: [
          "documents",
          knowledgeSourceId,
        ],
      });
    },
  });
}

export function useDeleteDocument(
  knowledgeSourceId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      deleteDocument,

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "documents",
          knowledgeSourceId,
        ],
      });
    },
  });
}