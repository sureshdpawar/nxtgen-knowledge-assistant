"use client";

import {
  useMemo,
  useState,
} from "react";

import {
  AlertTriangle,
  CalendarDays,
  Coins,
  Cpu,
  Database,
  Layers3,
  MessageSquareText,
} from "lucide-react";

import {
  useCostAnalytics,
} from "@/features/cost-analytics/hooks";

import {
  useKnowledgeBases,
} from "@/features/knowledge-bases/hooks";

import type {
  CurrencyCostTotal,
} from "@/features/cost-analytics/types";


function toDateInput(
  value: Date,
) {
  return value
    .toISOString()
    .slice(
      0,
      10,
    );
}


function initialStartDate() {
  const value = new Date();

  value.setUTCDate(
    value.getUTCDate() - 29,
  );

  return toDateInput(
    value,
  );
}


function initialEndDate() {
  return toDateInput(
    new Date(),
  );
}


function formatNumber(
  value: number,
) {
  return new Intl.NumberFormat(
    undefined,
    {
      notation:
        value >= 1000000
          ? "compact"
          : "standard",

      maximumFractionDigits: 1,
    },
  ).format(
    value,
  );
}


function formatMoney(
  value: number,
  currency: string,
) {
  try {
    return new Intl.NumberFormat(
      undefined,
      {
        style: "currency",
        currency,
        maximumFractionDigits: 4,
      },
    ).format(
      value,
    );
  } catch {
    return `${currency} ${value.toFixed(4)}`;
  }
}


function renderCostTotals(
  totals: CurrencyCostTotal[],
) {
  if (totals.length === 0) {
    return "Unknown";
  }

  return totals
    .map(
      (item) =>
        formatMoney(
          item.total_cost,
          item.currency,
        ),
    )
    .join(" + ");
}


function totalForCurrency(
  totals: CurrencyCostTotal[],
  currency: string,
) {
  return (
    totals.find(
      (item) =>
        item.currency === currency,
    )?.total_cost
    ?? 0
  );
}


function StatCard({
  title,
  value,
  caption,
  icon: Icon,
}: {
  title: string;
  value: string;
  caption: string;
  icon: React.ComponentType<{
    className?: string;
  }>;
}) {
  return (
    <div
      className="
        rounded-xl
        border
        border-slate-200
        bg-white
        p-5
        shadow-sm
      "
    >
      <div
        className="
          flex
          items-start
          justify-between
          gap-3
        "
      >
        <div className="min-w-0">
          <p
            className="
              text-sm
              font-medium
              text-slate-500
            "
          >
            {title}
          </p>

          <p
            className="
              mt-2
              break-words
              text-2xl
              font-semibold
              tracking-tight
              text-slate-900
            "
          >
            {value}
          </p>

          <p
            className="
              mt-1
              text-xs
              text-slate-500
            "
          >
            {caption}
          </p>
        </div>

        <div
          className="
            rounded-lg
            bg-slate-100
            p-2
          "
        >
          <Icon
            className="
              h-5
              w-5
              text-slate-600
            "
          />
        </div>
      </div>
    </div>
  );
}


function BreakdownRow({
  title,
  subtitle,
  cost,
  requests,
  tokens,
}: {
  title: string;
  subtitle?: string;
  cost: string;
  requests: number;
  tokens: number;
}) {
  return (
    <div
      className="
        flex
        flex-col
        gap-3
        border-b
        border-slate-100
        py-4
        last:border-b-0
        sm:flex-row
        sm:items-center
        sm:justify-between
      "
    >
      <div className="min-w-0">
        <p
          className="
            truncate
            text-sm
            font-semibold
            text-slate-900
          "
        >
          {title}
        </p>

        {subtitle && (
          <p
            className="
              mt-0.5
              truncate
              text-xs
              text-slate-500
            "
          >
            {subtitle}
          </p>
        )}
      </div>

      <div
        className="
          flex
          flex-wrap
          items-center
          gap-x-5
          gap-y-1
          text-xs
          text-slate-500
          sm:justify-end
        "
      >
        <span>
          {formatNumber(
            requests,
          )} calls
        </span>

        <span>
          {formatNumber(
            tokens,
          )} tokens
        </span>

        <span
          className="
            text-sm
            font-semibold
            text-slate-900
          "
        >
          {cost}
        </span>
      </div>
    </div>
  );
}


export default function CostAnalyticsPage() {
  const [
    startDate,
    setStartDate,
  ] = useState(
    initialStartDate,
  );

  const [
    endDate,
    setEndDate,
  ] = useState(
    initialEndDate,
  );

  const [
    knowledgeBaseId,
    setKnowledgeBaseId,
  ] = useState("");

  const [
    requestType,
    setRequestType,
  ] = useState("");

  const {
    data:
      knowledgeBases = [],
  } = useKnowledgeBases();

  const filters = useMemo(
    () => ({
      startDate,
      endDate,

      knowledgeBaseId:
        knowledgeBaseId
        || undefined,

      requestType:
        requestType
        || undefined,
    }),
    [
      startDate,
      endDate,
      knowledgeBaseId,
      requestType,
    ],
  );

  const {
    data,
    isLoading,
    isError,
    error,
  } = useCostAnalytics(
    filters,
  );

  const primaryCurrency =
    data?.overview
      .cost_totals[0]
      ?.currency
    ?? null;

  const maxDailyCost =
    primaryCurrency
      ? Math.max(
          0,
          ...(
            data?.daily
            ?? []
          ).map(
            (item) =>
              totalForCurrency(
                item.cost_totals,
                primaryCurrency,
              ),
          ),
        )
      : 0;

  const totalCostLabel =
    data
      ? renderCostTotals(
          data.overview.cost_totals,
        )
      : "—";

  return (
    <div
      className="
        space-y-6
      "
    >
      <div
        className="
          flex
          flex-col
          gap-2
        "
      >
        <h1
          className="
            text-2xl
            font-semibold
            tracking-tight
            text-slate-900
          "
        >
          Cost Analytics
        </h1>

        <p
          className="
            max-w-3xl
            text-sm
            text-slate-600
          "
        >
          Understand LLM spend across
          tenants, knowledge bases,
          workloads, providers, and
          models using the historical
          price captured when each call
          occurred.
        </p>
      </div>


      <section
        className="
          rounded-xl
          border
          border-slate-200
          bg-white
          p-4
          shadow-sm
        "
      >
        <div
          className="
            grid
            gap-4
            md:grid-cols-2
            xl:grid-cols-4
          "
        >
          <label
            className="
              space-y-1.5
              text-sm
              font-medium
              text-slate-700
            "
          >
            <span>
              Start date
            </span>

            <input
              type="date"
              value={startDate}
              max={endDate}
              onChange={(event) =>
                setStartDate(
                  event.target.value,
                )
              }
              className="
                h-10
                w-full
                rounded-lg
                border
                border-slate-300
                bg-white
                px-3
                text-sm
                text-slate-900
                outline-none
                focus:border-blue-500
                focus:ring-2
                focus:ring-blue-100
              "
            />
          </label>

          <label
            className="
              space-y-1.5
              text-sm
              font-medium
              text-slate-700
            "
          >
            <span>
              End date
            </span>

            <input
              type="date"
              value={endDate}
              min={startDate}
              onChange={(event) =>
                setEndDate(
                  event.target.value,
                )
              }
              className="
                h-10
                w-full
                rounded-lg
                border
                border-slate-300
                bg-white
                px-3
                text-sm
                text-slate-900
                outline-none
                focus:border-blue-500
                focus:ring-2
                focus:ring-blue-100
              "
            />
          </label>

          <label
            className="
              space-y-1.5
              text-sm
              font-medium
              text-slate-700
            "
          >
            <span>
              Knowledge Base
            </span>

            <select
              value={
                knowledgeBaseId
              }
              onChange={(event) =>
                setKnowledgeBaseId(
                  event.target.value,
                )
              }
              className="
                h-10
                w-full
                rounded-lg
                border
                border-slate-300
                bg-white
                px-3
                text-sm
                text-slate-900
                outline-none
                focus:border-blue-500
                focus:ring-2
                focus:ring-blue-100
              "
            >
              <option value="">
                All Knowledge Bases
              </option>

              {knowledgeBases.map(
                (kb) => (
                  <option
                    key={kb.id}
                    value={kb.id}
                  >
                    {kb.name}
                  </option>
                ),
              )}
            </select>
          </label>

          <label
            className="
              space-y-1.5
              text-sm
              font-medium
              text-slate-700
            "
          >
            <span>
              Workload
            </span>

            <select
              value={requestType}
              onChange={(event) =>
                setRequestType(
                  event.target.value,
                )
              }
              className="
                h-10
                w-full
                rounded-lg
                border
                border-slate-300
                bg-white
                px-3
                text-sm
                text-slate-900
                outline-none
                focus:border-blue-500
                focus:ring-2
                focus:ring-blue-100
              "
            >
              <option value="">
                All workloads
              </option>

              <option value="chat">
                Chat
              </option>

              <option value="agent">
                Agent
              </option>

              <option value="eval">
                Evaluation
              </option>
            </select>
          </label>
        </div>
      </section>


      {isLoading && (
        <div
          className="
            rounded-xl
            border
            border-slate-200
            bg-white
            p-8
            text-center
            text-sm
            text-slate-500
          "
        >
          Loading cost analytics...
        </div>
      )}


      {isError && (
        <div
          className="
            flex
            items-start
            gap-3
            rounded-xl
            border
            border-amber-200
            bg-amber-50
            p-4
            text-sm
            text-amber-900
          "
        >
          <AlertTriangle
            className="
              mt-0.5
              h-5
              w-5
              shrink-0
            "
          />

          <div>
            <p className="font-semibold">
              Unable to load cost analytics
            </p>

            <p className="mt-1">
              {error instanceof Error
                ? error.message
                : "Please try again."}
            </p>
          </div>
        </div>
      )}


      {data && (
        <>
          <section
            className="
              grid
              gap-4
              sm:grid-cols-2
              xl:grid-cols-4
            "
          >
            <StatCard
              title="Total AI Cost"
              value={totalCostLabel}
              caption={
                data.overview
                  .uncosted_request_count
                  > 0
                  ? `${formatNumber(
                      data.overview
                        .uncosted_request_count,
                    )} calls have unknown pricing`
                  : "All calls in range are costed"
              }
              icon={Coins}
            />

            <StatCard
              title="Total Tokens"
              value={formatNumber(
                data.overview
                  .total_tokens,
              )}
              caption={`${formatNumber(
                data.overview
                  .input_tokens,
              )} input · ${formatNumber(
                data.overview
                  .output_tokens,
              )} output`}
              icon={Cpu}
            />

            <StatCard
              title="LLM Calls"
              value={formatNumber(
                data.overview
                  .request_count,
              )}
              caption={`${formatNumber(
                data.overview
                  .costed_request_count,
              )} costed`}
              icon={MessageSquareText}
            />

            <StatCard
              title="Uncosted Calls"
              value={formatNumber(
                data.overview
                  .uncosted_request_count,
              )}
              caption={
                data.overview
                  .uncosted_request_count
                  > 0
                  ? "Pricing configuration required"
                  : "No missing pricing in this range"
              }
              icon={AlertTriangle}
            />
          </section>


          <section
            className="
              rounded-xl
              border
              border-slate-200
              bg-white
              p-5
              shadow-sm
            "
          >
            <div
              className="
                flex
                flex-col
                gap-1
                sm:flex-row
                sm:items-center
                sm:justify-between
              "
            >
              <div>
                <h2
                  className="
                    text-base
                    font-semibold
                    text-slate-900
                  "
                >
                  Cost over time
                </h2>

                <p
                  className="
                    mt-1
                    text-xs
                    text-slate-500
                  "
                >
                  Daily historical LLM spend.
                </p>
              </div>

              <div
                className="
                  flex
                  items-center
                  gap-1.5
                  text-xs
                  text-slate-500
                "
              >
                <CalendarDays
                  className="
                    h-4
                    w-4
                  "
                />

                {data.start_date}
                {" → "}
                {data.end_date}
              </div>
            </div>

            {!primaryCurrency ? (
              <div
                className="
                  mt-6
                  rounded-lg
                  border
                  border-dashed
                  border-slate-300
                  p-8
                  text-center
                  text-sm
                  text-slate-500
                "
              >
                No priced usage exists
                in this range yet.
              </div>
            ) : (
              <div
                className="
                  mt-6
                  overflow-x-auto
                "
              >
                <div
                  className="
                    flex
                    h-52
                    min-w-[640px]
                    items-end
                    gap-2
                    border-b
                    border-slate-200
                    px-1
                  "
                >
                  {data.daily.map(
                    (point) => {
                      const amount =
                        totalForCurrency(
                          point.cost_totals,
                          primaryCurrency,
                        );

                      const height =
                        maxDailyCost > 0
                          ? Math.max(
                              2,
                              (
                                amount
                                / maxDailyCost
                              )
                              * 100,
                            )
                          : 2;

                      return (
                        <div
                          key={point.date}
                          className="
                            group
                            relative
                            flex
                            min-w-3
                            flex-1
                            items-end
                            justify-center
                          "
                          title={`${point.date}: ${formatMoney(
                            amount,
                            primaryCurrency,
                          )}`}
                        >
                          <div
                            className="
                              w-full
                              rounded-t
                              bg-blue-500
                              transition
                              group-hover:bg-blue-600
                            "
                            style={{
                              height:
                                `${height}%`,
                            }}
                          />
                        </div>
                      );
                    },
                  )}
                </div>

                <div
                  className="
                    mt-2
                    flex
                    min-w-[640px]
                    justify-between
                    text-[11px]
                    text-slate-400
                  "
                >
                  <span>
                    {data.start_date}
                  </span>

                  <span>
                    {primaryCurrency}
                  </span>

                  <span>
                    {data.end_date}
                  </span>
                </div>
              </div>
            )}

            {data.overview
              .cost_totals.length
              > 1 && (
              <p
                className="
                  mt-4
                  text-xs
                  text-amber-700
                "
              >
                Multiple currencies are
                present. The trend shows
                {` ${primaryCurrency} `}
                only; totals are not
                converted between
                currencies.
              </p>
            )}
          </section>


          <section
            className="
              grid
              gap-6
              xl:grid-cols-2
            "
          >
            <div
              className="
                rounded-xl
                border
                border-slate-200
                bg-white
                p-5
                shadow-sm
              "
            >
              <div
                className="
                  flex
                  items-center
                  gap-2
                "
              >
                <Database
                  className="
                    h-5
                    w-5
                    text-slate-500
                  "
                />

                <h2
                  className="
                    text-base
                    font-semibold
                    text-slate-900
                  "
                >
                  Cost by Knowledge Base
                </h2>
              </div>

              <div className="mt-3">
                {data.by_knowledge_base
                  .length === 0 ? (
                  <p
                    className="
                      py-6
                      text-sm
                      text-slate-500
                    "
                  >
                    No usage for this range.
                  </p>
                ) : (
                  data.by_knowledge_base.map(
                    (item) => (
                      <BreakdownRow
                        key={
                          item.knowledge_base_id
                          ?? "unassigned"
                        }
                        title={
                          item.knowledge_base_name
                          ?? "Not tied to a Knowledge Base"
                        }
                        cost={renderCostTotals(
                          item.cost_totals,
                        )}
                        requests={
                          item.request_count
                        }
                        tokens={
                          item.total_tokens
                        }
                      />
                    ),
                  )
                )}
              </div>
            </div>


            <div
              className="
                rounded-xl
                border
                border-slate-200
                bg-white
                p-5
                shadow-sm
              "
            >
              <div
                className="
                  flex
                  items-center
                  gap-2
                "
              >
                <Layers3
                  className="
                    h-5
                    w-5
                    text-slate-500
                  "
                />

                <h2
                  className="
                    text-base
                    font-semibold
                    text-slate-900
                  "
                >
                  Cost by Workload
                </h2>
              </div>

              <div className="mt-3">
                {data.by_workload
                  .length === 0 ? (
                  <p
                    className="
                      py-6
                      text-sm
                      text-slate-500
                    "
                  >
                    No usage for this range.
                  </p>
                ) : (
                  data.by_workload.map(
                    (item) => (
                      <BreakdownRow
                        key={item.request_type}
                        title={
                          item.request_type
                        }
                        cost={renderCostTotals(
                          item.cost_totals,
                        )}
                        requests={
                          item.request_count
                        }
                        tokens={
                          item.total_tokens
                        }
                      />
                    ),
                  )
                )}
              </div>
            </div>
          </section>


          <section
            className="
              rounded-xl
              border
              border-slate-200
              bg-white
              p-5
              shadow-sm
            "
          >
            <div
              className="
                flex
                items-center
                gap-2
              "
            >
              <Cpu
                className="
                  h-5
                  w-5
                  text-slate-500
                "
              />

              <h2
                className="
                  text-base
                  font-semibold
                  text-slate-900
                "
              >
                Cost by Provider / Model
              </h2>
            </div>

            <div className="mt-3">
              {data.by_model
                .length === 0 ? (
                <p
                  className="
                    py-6
                    text-sm
                    text-slate-500
                  "
                >
                  No usage for this range.
                </p>
              ) : (
                data.by_model.map(
                  (item) => (
                    <BreakdownRow
                      key={
                        `${item.provider}:${item.model}`
                      }
                      title={item.model}
                      subtitle={item.provider}
                      cost={renderCostTotals(
                        item.cost_totals,
                      )}
                      requests={
                        item.request_count
                      }
                      tokens={
                        item.total_tokens
                      }
                    />
                  ),
                )
              )}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
