"use client";

import { useState } from "react";

import {
  Database,
  FlaskConical,
  GitCompareArrows,
} from "lucide-react";

import AgentEvaluationCompare from "./AgentEvaluationCompare";
import AgentEvaluationDatasets from "./AgentEvaluationDatasets";
import AgentEvaluationExperiments from "./AgentEvaluationExperiments";


type Tab =
  | "datasets"
  | "experiments"
  | "compare";


export default function AgentEvaluationWorkspace() {
  const [tab, setTab] =
    useState<Tab>("datasets");

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2">
          <FlaskConical className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-semibold text-slate-900">
            Agent Evaluation
          </h1>
        </div>

        <p className="mt-2 max-w-3xl text-sm font-medium text-slate-700">
          Regression Testing
        </p>

        <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-600">
          Build regression datasets, execute real agent experiments,
          compare candidate behavior against a baseline, and measure
          outcome, tool, argument, and governance quality before
          promoting changes.
        </p>
      </div>

      <div className="inline-flex max-w-full overflow-x-auto rounded-xl border border-slate-200 bg-white p-1 shadow-sm">
        <button
          type="button"
          onClick={() =>
            setTab("datasets")
          }
          className={`inline-flex shrink-0 items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition ${
            tab === "datasets"
              ? "bg-blue-600 text-white"
              : "text-slate-600 hover:bg-slate-50"
          }`}
        >
          <Database className="h-4 w-4" />
          Datasets & Cases
        </button>

        <button
          type="button"
          onClick={() =>
            setTab("experiments")
          }
          className={`inline-flex shrink-0 items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition ${
            tab === "experiments"
              ? "bg-blue-600 text-white"
              : "text-slate-600 hover:bg-slate-50"
          }`}
        >
          <FlaskConical className="h-4 w-4" />
          Experiments & Results
        </button>

        <button
          type="button"
          onClick={() =>
            setTab("compare")
          }
          className={`inline-flex shrink-0 items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition ${
            tab === "compare"
              ? "bg-blue-600 text-white"
              : "text-slate-600 hover:bg-slate-50"
          }`}
        >
          <GitCompareArrows className="h-4 w-4" />
          Compare Experiments
        </button>
      </div>

      {tab === "datasets" && (
        <AgentEvaluationDatasets />
      )}

      {tab === "experiments" && (
        <AgentEvaluationExperiments />
      )}

      {tab === "compare" && (
        <AgentEvaluationCompare />
      )}
    </div>
  );
}
