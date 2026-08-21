"use client";

import type {
  ReactNode,
} from "react";

import {
  Activity,
  Bot,
  KeyRound,
  MessageSquare,
  MessagesSquare,
  UserRound,
} from "lucide-react";

import {
  useChatChannelMetrics,
} from "../hooks";

import type {
  ChatChannel,
} from "../types";


type Props = {
  channel: ChatChannel;
};


export default function ChannelMetricsPanel({
  channel,
}: Props) {
  const {
    data:
      metrics,

    isLoading,

    error,

  } = useChatChannelMetrics(
    channel.id,
  );


  function formatDate(
    value:
      string | null,
  ) {
    if (!value) {
      return "No activity yet";
    }

    const date =
      new Date(
        value,
      );

    if (
      Number.isNaN(
        date.getTime(),
      )
    ) {
      return value;
    }

    return date
      .toLocaleString();
  }


  if (isLoading) {
    return (
      <div className="mt-4 rounded-xl border bg-slate-50 p-4 text-sm text-slate-500">
        Loading usage...
      </div>
    );
  }


  if (
    error
    || !metrics
  ) {
    return (
      <div className="mt-4 rounded-xl border border-red-100 bg-red-50 p-4 text-sm text-red-700">
        Unable to load usage.
      </div>
    );
  }


  return (
    <div className="mt-4 rounded-xl border bg-slate-50 p-4">

      <div className="flex items-center gap-2">

        <Activity className="h-4 w-4 text-slate-500" />

        <p className="text-sm font-semibold text-slate-900">
          Usage
        </p>

      </div>


      <div className="mt-4 grid grid-cols-2 gap-3">

        <Metric
          icon={
            <MessagesSquare className="h-4 w-4" />
          }
          label="Conversations"
          value={
            metrics
              .conversation_count
          }
        />


        <Metric
          icon={
            <MessageSquare className="h-4 w-4" />
          }
          label="Messages"
          value={
            metrics
              .message_count
          }
        />


        <Metric
          icon={
            <UserRound className="h-4 w-4" />
          }
          label="User messages"
          value={
            metrics
              .user_message_count
          }
        />


        <Metric
          icon={
            <Bot className="h-4 w-4" />
          }
          label="AI messages"
          value={
            metrics
              .assistant_message_count
          }
        />

      </div>


      {channel.type
        === "PUBLIC_API"
        && (
          <div className="mt-3 grid grid-cols-2 gap-3">

            <Metric
              icon={
                <KeyRound className="h-4 w-4" />
              }
              label="Active keys"
              value={
                metrics
                  .active_api_key_count
              }
            />


            <Metric
              icon={
                <KeyRound className="h-4 w-4" />
              }
              label="Revoked keys"
              value={
                metrics
                  .revoked_api_key_count
              }
            />

          </div>
        )}


      <div className="mt-4 border-t pt-3">

        <p className="text-xs text-slate-400">
          Last activity
        </p>

        <p className="mt-1 text-sm font-medium text-slate-700">
          {
            formatDate(
              metrics
                .last_activity_at,
            )
          }
        </p>

      </div>

    </div>
  );
}


type MetricProps = {
  icon:
    ReactNode;

  label: string;

  value: number;
};


function Metric({
  icon,
  label,
  value,
}: MetricProps) {
  return (
    <div className="rounded-lg border bg-white p-3">

      <div className="flex items-center gap-2 text-slate-400">
        {
          icon
        }

        <span className="text-xs">
          {
            label
          }
        </span>
      </div>


      <p className="mt-2 text-lg font-semibold text-slate-900">
        {
          value
        }
      </p>

    </div>
  );
}