"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AlertTriangle,
  Check,
  CheckCircle2,
  Clock3,
  Eye,
  ShieldCheck,
  X,
  XCircle,
} from "lucide-react";

import { useAuth } from "@/hooks/useAuth";

import {
  useAgentActionApprovals,
  useApproveAgentAction,
  useRejectAgentAction,
} from "@/features/agent-action-approvals/hooks";

import type {
  AgentActionApproval,
  AgentActionApprovalAction,
  AgentActionApprovalStatus,
} from "@/features/agent-action-approvals/types";


type StatusFilter =
  | "PENDING"
  | "APPROVED"
  | "REJECTED";


function formatDateTime(
  value: string | null,
) {
  if (!value) {
    return "—";
  }

  const date = new Date(
    value,
  );

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value;
  }

  return new Intl.DateTimeFormat(
    undefined,
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(
    date,
  );
}


function statusBadge(
  status: AgentActionApprovalStatus,
) {
  if (
    status === "APPROVED"
  ) {
    return (
      <span
        className="
          inline-flex
          items-center
          gap-1.5
          rounded-full
          bg-emerald-50
          px-2.5
          py-1
          text-xs
          font-semibold
          text-emerald-700
        "
      >
        <CheckCircle2
          className="h-3.5 w-3.5"
        />
        Approved
      </span>
    );
  }

  if (
    status === "REJECTED"
  ) {
    return (
      <span
        className="
          inline-flex
          items-center
          gap-1.5
          rounded-full
          bg-rose-50
          px-2.5
          py-1
          text-xs
          font-semibold
          text-rose-700
        "
      >
        <XCircle
          className="h-3.5 w-3.5"
        />
        Rejected
      </span>
    );
  }

  return (
    <span
      className="
        inline-flex
        items-center
        gap-1.5
        rounded-full
        bg-amber-50
        px-2.5
        py-1
        text-xs
        font-semibold
        text-amber-700
      "
    >
      <Clock3
        className="h-3.5 w-3.5"
      />
      Pending
    </span>
  );
}


function actionLabel(
  action: AgentActionApprovalAction,
) {
  return (
    action.name?.trim()
    || "Unnamed action"
  );
}


function actionSummary(
  approval: AgentActionApproval,
) {
  if (
    approval.actions.length
    === 0
  ) {
    return "No action details";
  }

  const first =
    actionLabel(
      approval.actions[0],
    );

  if (
    approval.actions.length
    === 1
  ) {
    return first;
  }

  return (
    `${first} +${
      approval.actions.length - 1
    } more`
  );
}


function JsonBlock({
  value,
}: {
  value: unknown;
}) {
  return (
    <pre
      className="
        max-h-72
        overflow-auto
        rounded-lg
        bg-slate-950
        p-3
        text-xs
        leading-5
        text-slate-100
      "
    >
      {JSON.stringify(
        value,
        null,
        2,
      )}
    </pre>
  );
}


function ApprovalDetails({
  approval,
  onClose,
}: {
  approval:
    AgentActionApproval;
  onClose: (
    resolved?:
      AgentActionApproval,
  ) => void;
}) {
  const approveMutation =
    useApproveAgentAction();

  const rejectMutation =
    useRejectAgentAction();

  const [
    reason,
    setReason,
  ] = useState("");

  const [
    decisionError,
    setDecisionError,
  ] = useState<
    string | null
  >(null);

  const isPending =
    approval.status
    === "PENDING";

  const isMutating =
    approveMutation.isPending
    || rejectMutation.isPending;


  async function decide(
    decision:
      | "approve"
      | "reject",
  ) {
    setDecisionError(
      null,
    );

    try {
      const payload = {
        reason:
          reason.trim()
          || null,
      };

      let resolved:
        AgentActionApproval;

      if (
        decision === "approve"
      ) {
        resolved =
          await approveMutation.mutateAsync(
            {
              id:
                approval.id,
              payload,
            },
          );
      } else {
        resolved =
          await rejectMutation.mutateAsync(
            {
              id:
                approval.id,
              payload,
            },
          );
      }

      onClose(
        resolved,
      );
    } catch (
      error
    ) {
      setDecisionError(
        error instanceof Error
          ? error.message
          : (
              "Unable to record "
              + "the approval decision."
            ),
      );
    }
  }


  return (
    <div
      className="
        fixed
        inset-0
        z-50
        flex
        items-end
        justify-center
        bg-slate-950/40
        p-0
        sm:items-center
        sm:p-4
      "
      role="dialog"
      aria-modal="true"
      aria-label="Agent action approval details"
    >
      <div
        className="
          flex
          max-h-[92vh]
          w-full
          max-w-3xl
          flex-col
          overflow-hidden
          rounded-t-2xl
          bg-white
          shadow-2xl
          sm:rounded-2xl
        "
      >
        <div
          className="
            flex
            shrink-0
            items-start
            justify-between
            gap-4
            border-b
            border-slate-200
            px-5
            py-4
          "
        >
          <div>
            <div
              className="
                flex
                flex-wrap
                items-center
                gap-2
              "
            >
              <h2
                className="
                  text-lg
                  font-semibold
                  text-slate-900
                "
              >
                Agent Action Approval
              </h2>

              {statusBadge(
                approval.status,
              )}
            </div>

            <p
              className="
                mt-1
                text-sm
                text-slate-500
              "
            >
              Review the exact
              proposed action before
              allowing the paused
              agent run to continue.
            </p>
          </div>

          <button
            type="button"
            onClick={
              onClose
            }
            className="
              inline-flex
              h-9
              w-9
              shrink-0
              items-center
              justify-center
              rounded-lg
              text-slate-500
              hover:bg-slate-100
              hover:text-slate-900
            "
            aria-label="Close approval details"
          >
            <X
              className="h-5 w-5"
            />
          </button>
        </div>


        <div
          className="
            min-h-0
            flex-1
            space-y-6
            overflow-y-auto
            px-5
            py-5
          "
        >
          <section
            className="
              grid
              gap-4
              rounded-xl
              border
              border-slate-200
              bg-slate-50
              p-4
              sm:grid-cols-2
            "
          >
            <div>
              <p
                className="
                  text-xs
                  font-medium
                  uppercase
                  tracking-wide
                  text-slate-400
                "
              >
                Agent
              </p>

              <p
                className="
                  mt-1
                  text-sm
                  font-semibold
                  text-slate-900
                "
              >
                {
                  approval.agent_name
                }
              </p>
            </div>

            <div>
              <p
                className="
                  text-xs
                  font-medium
                  uppercase
                  tracking-wide
                  text-slate-400
                "
              >
                Requested by
              </p>

              <p
                className="
                  mt-1
                  break-all
                  text-sm
                  font-semibold
                  text-slate-900
                "
              >
                {
                  approval.actor_type
                }
                {" · "}
                {
                  approval.actor_id
                }
              </p>
            </div>

            <div>
              <p
                className="
                  text-xs
                  font-medium
                  uppercase
                  tracking-wide
                  text-slate-400
                "
              >
                Requested at
              </p>

              <p
                className="
                  mt-1
                  text-sm
                  text-slate-700
                "
              >
                {formatDateTime(
                  approval.requested_at,
                )}
              </p>
            </div>

            <div>
              <p
                className="
                  text-xs
                  font-medium
                  uppercase
                  tracking-wide
                  text-slate-400
                "
              >
                Run status
              </p>

              <p
                className="
                  mt-1
                  text-sm
                  text-slate-700
                "
              >
                {
                  approval.run_status
                }
              </p>
            </div>
          </section>


          <section>
            <h3
              className="
                text-sm
                font-semibold
                text-slate-900
              "
            >
              User request
            </h3>

            <div
              className="
                mt-2
                rounded-xl
                border
                border-slate-200
                bg-white
                p-4
                text-sm
                leading-6
                text-slate-700
              "
            >
              {
                approval.run_query
              }
            </div>
          </section>


          <section>
            <div
              className="
                flex
                items-center
                justify-between
                gap-3
              "
            >
              <h3
                className="
                  text-sm
                  font-semibold
                  text-slate-900
                "
              >
                Proposed actions
              </h3>

              <span
                className="
                  text-xs
                  text-slate-500
                "
              >
                {
                  approval.actions.length
                } action{
                  approval.actions.length
                  === 1
                    ? ""
                    : "s"
                }
              </span>
            </div>

            <div
              className="
                mt-3
                space-y-3
              "
            >
              {
                approval.actions.map(
                  (
                    action,
                    index,
                  ) => (
                    <div
                      key={
                        action.tool_call_id
                        || `${actionLabel(
                          action,
                        )}-${index}`
                      }
                      className="
                        rounded-xl
                        border
                        border-slate-200
                        bg-white
                        p-4
                      "
                    >
                      <div
                        className="
                          flex
                          flex-wrap
                          items-center
                          gap-2
                        "
                      >
                        <p
                          className="
                            font-mono
                            text-sm
                            font-semibold
                            text-slate-900
                          "
                        >
                          {
                            actionLabel(
                              action,
                            )
                          }
                        </p>

                        {
                          action.risk_level
                          && (
                            <span
                              className="
                                rounded-full
                                bg-rose-50
                                px-2
                                py-0.5
                                text-[11px]
                                font-semibold
                                text-rose-700
                              "
                            >
                              {
                                action.risk_level
                              }
                            </span>
                          )
                        }

                        {
                          action.execution_policy
                          && (
                            <span
                              className="
                                rounded-full
                                bg-amber-50
                                px-2
                                py-0.5
                                text-[11px]
                                font-semibold
                                text-amber-700
                              "
                            >
                              {
                                action.execution_policy
                              }
                            </span>
                          )
                        }
                      </div>

                      <p
                        className="
                          mt-3
                          text-xs
                          font-medium
                          text-slate-500
                        "
                      >
                        Arguments
                      </p>

                      <div
                        className="mt-2"
                      >
                        <JsonBlock
                          value={
                            action.args
                            ?? {}
                          }
                        />
                      </div>

                      {
                        action.tool_call_id
                        && (
                          <p
                            className="
                              mt-3
                              break-all
                              text-[11px]
                              text-slate-400
                            "
                          >
                            Tool call ID:{" "}
                            {
                              action.tool_call_id
                            }
                          </p>
                        )
                      }
                    </div>
                  ),
                )
              }
            </div>
          </section>


          {
            !isPending
            && (
              <section
                className="
                  rounded-xl
                  border
                  border-slate-200
                  bg-slate-50
                  p-4
                "
              >
                <h3
                  className="
                    text-sm
                    font-semibold
                    text-slate-900
                  "
                >
                  Decision
                </h3>

                <dl
                  className="
                    mt-3
                    grid
                    gap-3
                    text-sm
                    sm:grid-cols-2
                  "
                >
                  <div>
                    <dt
                      className="
                        text-xs
                        text-slate-500
                      "
                    >
                      Decided at
                    </dt>

                    <dd
                      className="
                        mt-1
                        text-slate-800
                      "
                    >
                      {
                        formatDateTime(
                          approval.decided_at,
                        )
                      }
                    </dd>
                  </div>

                  <div>
                    <dt
                      className="
                        text-xs
                        text-slate-500
                      "
                    >
                      Decided by
                    </dt>

                    <dd
                      className="
                        mt-1
                        break-all
                        text-slate-800
                      "
                    >
                      {
                        approval.decided_by_user_id
                        ?? "—"
                      }
                    </dd>
                  </div>
                </dl>

                {
                  approval.decision_reason
                  && (
                    <div
                      className="
                        mt-4
                      "
                    >
                      <p
                        className="
                          text-xs
                          text-slate-500
                        "
                      >
                        Reason
                      </p>

                      <p
                        className="
                          mt-1
                          whitespace-pre-wrap
                          text-sm
                          text-slate-800
                        "
                      >
                        {
                          approval.decision_reason
                        }
                      </p>
                    </div>
                  )
                }
              </section>
            )
          }


          {
            isPending
            && (
              <section>
                <label
                  className="
                    block
                    text-sm
                    font-medium
                    text-slate-700
                  "
                >
                  Decision reason
                  <span
                    className="
                      ml-1
                      font-normal
                      text-slate-400
                    "
                  >
                    optional
                  </span>
                </label>

                <textarea
                  value={
                    reason
                  }
                  onChange={(
                    event,
                  ) =>
                    setReason(
                      event.target.value,
                    )
                  }
                  maxLength={
                    2000
                  }
                  rows={3}
                  placeholder="Add context for the audit trail..."
                  className="
                    mt-2
                    w-full
                    resize-y
                    rounded-lg
                    border
                    border-slate-300
                    bg-white
                    px-3
                    py-2
                    text-sm
                    text-slate-900
                    outline-none
                    focus:border-blue-500
                    focus:ring-2
                    focus:ring-blue-100
                  "
                />
              </section>
            )
          }


          {
            decisionError
            && (
              <div
                className="
                  flex
                  items-start
                  gap-3
                  rounded-xl
                  border
                  border-rose-200
                  bg-rose-50
                  p-4
                  text-sm
                  text-rose-800
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

                <p>
                  {
                    decisionError
                  }
                </p>
              </div>
            )
          }
        </div>


        <div
          className="
            flex
            shrink-0
            flex-col-reverse
            gap-2
            border-t
            border-slate-200
            bg-white
            px-5
            py-4
            sm:flex-row
            sm:justify-end
          "
        >
          <button
            type="button"
            onClick={
              onClose
            }
            disabled={
              isMutating
            }
            className="
              inline-flex
              h-10
              items-center
              justify-center
              rounded-lg
              border
              border-slate-300
              bg-white
              px-4
              text-sm
              font-semibold
              text-slate-700
              hover:bg-slate-50
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >
            Close
          </button>

          {
            isPending
            && (
              <>
                <button
                  type="button"
                  onClick={() =>
                    decide(
                      "reject",
                    )
                  }
                  disabled={
                    isMutating
                  }
                  className="
                    inline-flex
                    h-10
                    items-center
                    justify-center
                    gap-2
                    rounded-lg
                    border
                    border-rose-200
                    bg-white
                    px-4
                    text-sm
                    font-semibold
                    text-rose-700
                    hover:bg-rose-50
                    disabled:cursor-not-allowed
                    disabled:opacity-50
                  "
                >
                  <XCircle
                    className="h-4 w-4"
                  />
                  Reject
                </button>

                <button
                  type="button"
                  onClick={() =>
                    decide(
                      "approve",
                    )
                  }
                  disabled={
                    isMutating
                  }
                  className="
                    inline-flex
                    h-10
                    items-center
                    justify-center
                    gap-2
                    rounded-lg
                    bg-blue-600
                    px-4
                    text-sm
                    font-semibold
                    text-white
                    shadow-sm
                    hover:bg-blue-700
                    disabled:cursor-not-allowed
                    disabled:opacity-50
                  "
                >
                  <Check
                    className="h-4 w-4"
                  />
                  {
                    approveMutation.isPending
                      ? "Approving..."
                      : "Approve"
                  }
                </button>
              </>
            )
          }
        </div>
      </div>
    </div>
  );
}


export default function ApprovalsPage() {
  const {
    user,
  } = useAuth();

  const [
    status,
    setStatus,
  ] = useState<
    StatusFilter
  >("PENDING");

  const [
    selected,
    setSelected,
  ] = useState<
    AgentActionApproval
    | null
  >(null);

  const [
    decisionNotice,
    setDecisionNotice,
  ] = useState<
    string | null
  >(null);

  const {
    data:
      approvals = [],
    isLoading,
    isError,
    error,
  } = useAgentActionApprovals(
    status,
  );

  useEffect(
    () => {
      setSelected(
        null,
      );
    },
    [
      status,
    ],
  );

  const statusCounts =
    useMemo(
      () => ({
        total:
          approvals.length,
      }),
      [
        approvals,
      ],
    );


  if (
    !user
  ) {
    return null;
  }


  if (
    user.role
    !== "ADMIN"
  ) {
    return (
      <div
        className="
          rounded-xl
          border
          border-amber-200
          bg-amber-50
          p-5
          text-sm
          text-amber-900
        "
      >
        <div
          className="
            flex
            items-start
            gap-3
          "
        >
          <ShieldCheck
            className="
              mt-0.5
              h-5
              w-5
              shrink-0
            "
          />

          <div>
            <p
              className="
                font-semibold
              "
            >
              Admin access required
            </p>

            <p
              className="
                mt-1
              "
            >
              Agent action approvals
              are available only to
              tenant Admin users.
            </p>
          </div>
        </div>
      </div>
    );
  }


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
        <div
          className="
            flex
            items-center
            gap-2
          "
        >
          <ShieldCheck
            className="
              h-6
              w-6
              text-blue-600
            "
          />

          <h1
            className="
              text-2xl
              font-semibold
              tracking-tight
              text-slate-900
            "
          >
            Approvals
          </h1>
        </div>

        <p
          className="
            max-w-3xl
            text-sm
            text-slate-600
          "
        >
          Review agent-proposed
          actions that require human
          approval before the paused
          workflow can continue.
        </p>
      </div>


      {
        decisionNotice
        && (
          <div
            className="
              flex
              items-start
              gap-3
              rounded-xl
              border
              border-blue-200
              bg-blue-50
              p-4
              text-sm
              text-blue-900
            "
          >
            <CheckCircle2
              className="
                mt-0.5
                h-5
                w-5
                shrink-0
                text-blue-700
              "
            />

            <div
              className="
                min-w-0
                flex-1
              "
            >
              <p
                className="
                  font-semibold
                "
              >
                Approval decision recorded
              </p>

              <p
                className="
                  mt-1
                  text-blue-800
                "
              >
                {
                  decisionNotice
                }
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                setDecisionNotice(
                  null,
                )
              }
              aria-label="Dismiss approval notice"
              className="
                inline-flex
                h-8
                w-8
                shrink-0
                items-center
                justify-center
                rounded-lg
                text-blue-700
                hover:bg-blue-100
              "
            >
              <X
                className="h-4 w-4"
              />
            </button>
          </div>
        )
      }


      <div
        className="
          flex
          flex-wrap
          gap-2
        "
      >
        {
          (
            [
              "PENDING",
              "APPROVED",
              "REJECTED",
            ] as StatusFilter[]
          ).map(
            (
              item,
            ) => {
              const active =
                status === item;

              const Icon =
                item
                === "PENDING"
                  ? Clock3
                  : item
                    === "APPROVED"
                      ? CheckCircle2
                      : XCircle;

              return (
                <button
                  key={
                    item
                  }
                  type="button"
                  onClick={() =>
                    setStatus(
                      item,
                    )
                  }
                  className={`
                    inline-flex
                    h-10
                    items-center
                    gap-2
                    rounded-lg
                    border
                    px-4
                    text-sm
                    font-semibold
                    transition
                    ${
                      active
                        ? "border-blue-600 bg-blue-600 text-white shadow-sm"
                        : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                    }
                  `}
                >
                  <Icon
                    className="h-4 w-4"
                  />

                  {
                    item.charAt(0)
                    + item
                      .slice(1)
                      .toLowerCase()
                  }
                </button>
              );
            },
          )
        }
      </div>


      <section
        className="
          overflow-hidden
          rounded-xl
          border
          border-slate-200
          bg-white
          shadow-sm
        "
      >
        <div
          className="
            flex
            flex-col
            gap-1
            border-b
            border-slate-200
            px-5
            py-4
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
              {
                status.charAt(0)
                + status
                  .slice(1)
                  .toLowerCase()
              }{" "}
              approvals
            </h2>

            <p
              className="
                mt-1
                text-xs
                text-slate-500
              "
            >
              One approval record
              represents one paused
              agent checkpoint and
              may contain multiple
              proposed tool actions.
            </p>
          </div>

          {
            !isLoading
            && !isError
            && (
              <span
                className="
                  text-xs
                  font-medium
                  text-slate-500
                "
              >
                {
                  statusCounts.total
                } record{
                  statusCounts.total
                  === 1
                    ? ""
                    : "s"
                }
              </span>
            )
          }
        </div>


        {
          isLoading
          && (
            <div
              className="
                p-8
                text-center
                text-sm
                text-slate-500
              "
            >
              Loading approvals...
            </div>
          )
        }


        {
          isError
          && (
            <div
              className="
                m-5
                flex
                items-start
                gap-3
                rounded-xl
                border
                border-rose-200
                bg-rose-50
                p-4
                text-sm
                text-rose-800
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
                <p
                  className="
                    font-semibold
                  "
                >
                  Unable to load approvals
                </p>

                <p
                  className="
                    mt-1
                  "
                >
                  {
                    error instanceof Error
                      ? error.message
                      : "Please try again."
                  }
                </p>
              </div>
            </div>
          )
        }


        {
          !isLoading
          && !isError
          && approvals.length
          === 0
          && (
            <div
              className="
                px-5
                py-12
                text-center
              "
            >
              <ShieldCheck
                className="
                  mx-auto
                  h-8
                  w-8
                  text-slate-300
                "
              />

              <p
                className="
                  mt-3
                  text-sm
                  font-semibold
                  text-slate-800
                "
              >
                No {
                  status.toLowerCase()
                } approvals
              </p>

              <p
                className="
                  mt-1
                  text-xs
                  text-slate-500
                "
              >
                Agent actions will
                appear here when
                their execution
                policy requires
                Admin approval.
              </p>
            </div>
          )
        }


        {
          approvals.length
          > 0
          && (
            <div
              className="
                overflow-x-auto
              "
            >
              <table
                className="
                  w-full
                  min-w-[900px]
                  text-left
                  text-sm
                "
              >
                <thead
                  className="
                    bg-slate-50
                    text-xs
                    uppercase
                    tracking-wide
                    text-slate-500
                  "
                >
                  <tr>
                    <th
                      className="
                        px-5
                        py-3
                        font-semibold
                      "
                    >
                      Agent
                    </th>

                    <th
                      className="
                        px-5
                        py-3
                        font-semibold
                      "
                    >
                      Proposed action
                    </th>

                    <th
                      className="
                        px-5
                        py-3
                        font-semibold
                      "
                    >
                      Requested by
                    </th>

                    <th
                      className="
                        px-5
                        py-3
                        font-semibold
                      "
                    >
                      Requested at
                    </th>

                    <th
                      className="
                        px-5
                        py-3
                        font-semibold
                      "
                    >
                      Status
                    </th>

                    <th
                      className="
                        px-5
                        py-3
                        text-right
                        font-semibold
                      "
                    >
                      Review
                    </th>
                  </tr>
                </thead>

                <tbody
                  className="
                    divide-y
                    divide-slate-100
                  "
                >
                  {
                    approvals.map(
                      (
                        approval,
                      ) => (
                        <tr
                          key={
                            approval.id
                          }
                          className="
                            align-top
                            hover:bg-slate-50/70
                          "
                        >
                          <td
                            className="
                              px-5
                              py-4
                            "
                          >
                            <p
                              className="
                                font-semibold
                                text-slate-900
                              "
                            >
                              {
                                approval.agent_name
                              }
                            </p>

                            <p
                              className="
                                mt-1
                                max-w-[220px]
                                truncate
                                text-xs
                                text-slate-500
                              "
                              title={
                                approval.run_query
                              }
                            >
                              {
                                approval.run_query
                              }
                            </p>
                          </td>

                          <td
                            className="
                              px-5
                              py-4
                            "
                          >
                            <p
                              className="
                                font-mono
                                text-sm
                                font-semibold
                                text-slate-800
                              "
                            >
                              {
                                actionSummary(
                                  approval,
                                )
                              }
                            </p>

                            <p
                              className="
                                mt-1
                                text-xs
                                text-slate-500
                              "
                            >
                              {
                                approval.actions.length
                              } action{
                                approval.actions.length
                                === 1
                                  ? ""
                                  : "s"
                              }
                            </p>
                          </td>

                          <td
                            className="
                              px-5
                              py-4
                            "
                          >
                            <p
                              className="
                                text-sm
                                font-medium
                                text-slate-800
                              "
                            >
                              {
                                approval.actor_type
                              }
                            </p>

                            <p
                              className="
                                mt-1
                                max-w-[180px]
                                truncate
                                text-xs
                                text-slate-500
                              "
                              title={
                                approval.actor_id
                              }
                            >
                              {
                                approval.actor_id
                              }
                            </p>
                          </td>

                          <td
                            className="
                              whitespace-nowrap
                              px-5
                              py-4
                              text-sm
                              text-slate-600
                            "
                          >
                            {
                              formatDateTime(
                                approval.requested_at,
                              )
                            }
                          </td>

                          <td
                            className="
                              px-5
                              py-4
                            "
                          >
                            {
                              statusBadge(
                                approval.status,
                              )
                            }
                          </td>

                          <td
                            className="
                              px-5
                              py-4
                              text-right
                            "
                          >
                            <button
                              type="button"
                              onClick={() =>
                                setSelected(
                                  approval,
                                )
                              }
                              className="
                                inline-flex
                                h-9
                                items-center
                                justify-center
                                gap-2
                                rounded-lg
                                border
                                border-slate-300
                                bg-white
                                px-3
                                text-xs
                                font-semibold
                                text-slate-700
                                hover:bg-slate-50
                              "
                            >
                              <Eye
                                className="h-4 w-4"
                              />
                              Review
                            </button>
                          </td>
                        </tr>
                      ),
                    )
                  }
                </tbody>
              </table>
            </div>
          )
        }
      </section>


      {
        selected
        && (
          <ApprovalDetails
            approval={
              selected
            }
            onClose={(resolved) => {
              setSelected(
                null,
              );

              if (
                !resolved
              ) {
                return;
              }

              if (
                resolved.run_status
                === "WAITING_FOR_APPROVAL"
              ) {
                setDecisionNotice(
                  (
                    "This approval was recorded successfully. "
                    + "The resumed agent has proposed another "
                    + "action that also requires approval."
                  ),
                );
                return;
              }

              setDecisionNotice(
                resolved.status
                === "APPROVED"
                  ? (
                      "The action was approved and "
                      + "the agent run resumed."
                    )
                  : (
                      "The action was rejected and "
                      + "the agent run resumed."
                    ),
              );
            }}
          />
        )
      }
    </div>
  );
}
