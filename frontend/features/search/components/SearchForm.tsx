"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  Search,
} from "lucide-react";

import {
  useAccessibleKnowledgeBases,
} from "@/features/knowledge-bases/hooks";


type Props = {
  onSearch: (
    knowledgeBaseId: string,
    query: string,
  ) => Promise<void>;

  searching: boolean;
};


export default function SearchForm({
  onSearch,
  searching,
}: Props) {
  const {
    data: knowledgeBases,
    isLoading,
  } =
    useAccessibleKnowledgeBases();

  const [
    knowledgeBaseId,
    setKnowledgeBaseId,
  ] =
    useState("");

  const [
    query,
    setQuery,
  ] =
    useState("");


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (
      !knowledgeBaseId ||
      !query.trim()
    ) {
      return;
    }

    await onSearch(
      knowledgeBaseId,
      query.trim(),
    );
  }


  return (
    <form
      onSubmit={submit}
      className="rounded-xl border bg-white p-6 shadow-sm"
    >
      <div className="grid gap-5 lg:grid-cols-[280px_1fr_auto] lg:items-end">

        {/* Knowledge Base */}
        <div>

          <label
            htmlFor="knowledge-base"
            className="text-sm font-medium text-slate-700"
          >
            Knowledge Base
          </label>

          <select
            id="knowledge-base"
            value={
              knowledgeBaseId
            }
            onChange={(event) =>
              setKnowledgeBaseId(
                event.target.value,
              )
            }
            disabled={
              isLoading
            }
            className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm outline-none focus:border-blue-500"
          >
            <option value="">
              Select knowledge base
            </option>

            {knowledgeBases?.map(
              (knowledgeBase) => (
                <option
                  key={
                    knowledgeBase.id
                  }
                  value={
                    knowledgeBase.id
                  }
                >
                  {
                    knowledgeBase.name
                  }
                </option>
              ),
            )}
          </select>

        </div>


        {/* Query */}
        <div>

          <label
            htmlFor="search-query"
            className="text-sm font-medium text-slate-700"
          >
            Search
          </label>

          <input
            id="search-query"
            type="text"
            value={query}
            onChange={(event) =>
              setQuery(
                event.target.value,
              )
            }
            placeholder="Ask something about this knowledge base..."
            className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
          />

        </div>


        {/* Search Button */}
        <button
          type="submit"
          disabled={
            searching ||
            !knowledgeBaseId ||
            !query.trim()
          }
          className="flex h-10 items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Search className="h-4 w-4" />

          {searching
            ? "Searching..."
            : "Search"}
        </button>

      </div>
    </form>
  );
}