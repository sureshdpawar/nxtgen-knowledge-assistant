import type {
  SearchResult,
} from "../types";

import SearchResultCard from "./SearchResultCard";


type Props = {
  results: SearchResult[];
};


export default function SearchResults({
  results,
}: Props) {
  if (
    results.length === 0
  ) {
    return (
      <div className="rounded-xl border border-dashed bg-white p-10 text-center">

        <h3 className="font-semibold">
          No results found
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          Try a different search
          query.
        </p>

      </div>
    );
  }

  return (
    <div className="space-y-4">

      <div className="text-sm text-slate-500">
        {results.length}{" "}
        {results.length === 1
          ? "result"
          : "results"}
      </div>


      {results.map(
        (result) => (
          <SearchResultCard
            key={
              result.chunk_id
            }
            result={result}
          />
        ),
      )}

    </div>
  );
}