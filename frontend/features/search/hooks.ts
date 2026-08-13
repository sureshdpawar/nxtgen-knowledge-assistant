import {
  useMutation,
} from "@tanstack/react-query";

import {
  searchKnowledgeBase,
} from "./api";


export function useSearchKnowledgeBase() {
  return useMutation({
    mutationFn:
      searchKnowledgeBase,
  });
}