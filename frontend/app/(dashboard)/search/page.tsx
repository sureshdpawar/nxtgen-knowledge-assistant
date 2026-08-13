"use client";

import {
  useState,
} from "react";

import {
  useSearchKnowledgeBase,
} from "@/features/search/hooks";

import type {
  SearchResult,
} from "@/features/search/types";

import SearchForm from "@/features/search/components/SearchForm";
import SearchResults from "@/features/search/components/SearchResults";


export default function SearchPage() {
  const searchMutation =
    useSearchKnowledgeBase();

  const [
    results,
    setResults,
  ] =
    useState<
      SearchResult[]
    >([]);


  const [
    searched,
    setSearched,
  ] =
    useState(false);


  async function handleSearch(
    knowledgeBaseId: string,
    query: string,
  ) {
    const response =
      await searchMutation
        .mutateAsync({
          knowledge_base_id:
            knowledgeBaseId,
          query,
        });

    setResults(
      response.results,
    );

    setSearched(true);
  }


  return (
    <div className="space-y-8">

      {/* Header */}
      <div>

        <p className="text-sm font-medium text-slate-500">
          Knowledge Search
        </p>

        <h1 className="mt-1 text-3xl font-bold text-slate-900">
          Search
        </h1>

        <p className="mt-2 text-slate-500">
          Search across documents
          in the knowledge bases
          available to you.
        </p>

      </div>


      <SearchForm
        onSearch={
          handleSearch
        }
        searching={
          searchMutation.isPending
        }
      />


      {searchMutation.isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Search failed. Please
          try again.
        </div>
      )}


      {searched && (
        <SearchResults
          results={
            results
          }
        />
      )}

    </div>
  );
}