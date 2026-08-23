"use client";

import {
  useState,
} from "react";

import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import {
  Input,
} from "@/components/ui/input";

import {
  Label,
} from "@/components/ui/label";

import type {
  CreateChatChannelRequest,
} from "../types";


type SupportedChannelType =
  | "WEBSITE"
  | "PUBLIC_API"
  | "SLACK";


type Props = {
  knowledgeBaseId: string;

  onCreate: (
    payload:
      CreateChatChannelRequest,
  ) => Promise<void>;
};


export default function CreateChatChannelDialog({
  knowledgeBaseId,
  onCreate,
}: Props) {
  const [
    open,
    setOpen,
  ] = useState(
    false,
  );

  const [
    name,
    setName,
  ] = useState(
    "",
  );

  const [
    type,
    setType,
  ] = useState<
    SupportedChannelType
  >(
    "WEBSITE",
  );

  const [
    origins,
    setOrigins,
  ] = useState(
    "http://localhost:3000",
  );

  const [
    widgetTitle,
    setWidgetTitle,
  ] = useState(
    "NXTGEN Assistant",
  );

  const [
    welcomeMessage,
    setWelcomeMessage,
  ] = useState(
    "Hi! How can I help?",
  );

  const [
    placeholder,
    setPlaceholder,
  ] = useState(
    "Ask me anything...",
  );

  const [
    showSources,
    setShowSources,
  ] = useState(
    true,
  );

  const [
    slackRespondToMentions,
    setSlackRespondToMentions,
  ] = useState(
    true,
  );

  const [
    slackRespondToDirectMessages,
    setSlackRespondToDirectMessages,
  ] = useState(
    false,
  );

  const [
    submitting,
    setSubmitting,
  ] = useState(
    false,
  );

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(
    null,
  );


  function resetForm() {
    setName(
      "",
    );

    setType(
      "WEBSITE",
    );

    setOrigins(
      "http://localhost:3000",
    );

    setWidgetTitle(
      "NXTGEN Assistant",
    );

    setWelcomeMessage(
      "Hi! How can I help?",
    );

    setPlaceholder(
      "Ask me anything...",
    );

    setShowSources(
      true,
    );

    setSlackRespondToMentions(
      true,
    );

    setSlackRespondToDirectMessages(
      false,
    );

    setError(
      null,
    );
  }


  function handleTypeChange(
    event:
      React.ChangeEvent<
        HTMLSelectElement
      >,
  ) {
    const value =
      event.currentTarget.value;

    if (
      value === "WEBSITE"
      || value === "PUBLIC_API"
      || value === "SLACK"
    ) {
      setType(
        value,
      );

      setError(
        null,
      );
    }
  }


  async function submit(
    event:
      React.FormEvent<
        HTMLFormElement
      >,
  ) {
    event.preventDefault();

    const normalizedName =
      name.trim();

    if (!normalizedName) {
      setError(
        "Channel name is required.",
      );

      return;
    }


    let configuration:
      Record<
        string,
        unknown
      > = {};


    if (
      type === "WEBSITE"
    ) {
      const allowedOrigins =
        origins
          .split(
            "\n",
          )
          .map(
            (
              value,
            ) =>
              value.trim(),
          )
          .filter(
            Boolean,
          );

      if (
        allowedOrigins.length
        === 0
      ) {
        setError(
          "At least one allowed origin is required.",
        );

        return;
      }

      configuration = {
        allowed_origins:
          allowedOrigins,

        widget_title:
          widgetTitle.trim()
          || "Assistant",

        welcome_message:
          welcomeMessage.trim(),

        placeholder:
          placeholder.trim()
          || "Ask a question...",

        show_sources:
          showSources,
      };
    }


    if (
      type === "PUBLIC_API"
    ) {
      configuration = {};
    }


    if (
      type === "SLACK"
    ) {
      configuration = {
        respond_to_mentions:
          slackRespondToMentions,

        respond_to_direct_messages:
          slackRespondToDirectMessages,

        allowed_slack_channel_ids:
          [],
      };
    }


    setSubmitting(
      true,
    );

    setError(
      null,
    );


    try {
      await onCreate({
        knowledge_base_id:
          knowledgeBaseId,

        name:
          normalizedName,

        type,

        configuration,
      });

      resetForm();

      setOpen(
        false,
      );

    } catch (
      submitError
    ) {
      console.error(
        submitError,
      );

      setError(
        "Unable to create channel.",
      );

    } finally {
      setSubmitting(
        false,
      );
    }
  }


  function handleOpenChange(
    nextOpen: boolean,
  ) {
    setOpen(
      nextOpen,
    );

    if (
      !nextOpen
      && !submitting
    ) {
      setError(
        null,
      );
    }
  }


  return (
    <>
      <button
        type="button"
        onClick={() =>
          setOpen(
            true,
          )
        }
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        + Create Channel
      </button>


      <Dialog
        open={
          open
        }
        onOpenChange={
          handleOpenChange
        }
      >
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-xl">

          <DialogHeader>

            <DialogTitle>
              Create Channel
            </DialogTitle>

          </DialogHeader>


          <form
            onSubmit={
              submit
            }
            className="space-y-5"
          >

            <div className="space-y-2">

              <Label
                htmlFor="channel-name"
              >
                Name
              </Label>


              <Input
                id="channel-name"
                value={
                  name
                }
                onChange={(
                  event,
                ) =>
                  setName(
                    event
                      .currentTarget
                      .value,
                  )
                }
                placeholder="Example: Company Website Assistant"
              />

            </div>


            <div className="space-y-2">

              <Label
                htmlFor="channel-type"
              >
                Channel Type
              </Label>


              <select
                id="channel-type"
                value={
                  type
                }
                onChange={
                  handleTypeChange
                }
                className="flex h-10 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none focus:border-blue-500"
              >

                <option value="WEBSITE">
                  Website Chatbot
                </option>

                <option value="PUBLIC_API">
                  Public API
                </option>

                <option value="SLACK">
                  Slack
                </option>

              </select>


              <p className="text-xs text-slate-500">
                Choose where users will
                interact with this
                knowledge base.
              </p>

            </div>


            {type === "WEBSITE" && (
              <>

                <div className="space-y-2">

                  <Label
                    htmlFor="allowed-origins"
                  >
                    Allowed Websites
                  </Label>


                  <textarea
                    id="allowed-origins"
                    value={
                      origins
                    }
                    onChange={(
                      event,
                    ) =>
                      setOrigins(
                        event
                          .currentTarget
                          .value,
                      )
                    }
                    rows={
                      4
                    }
                    className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500"
                    placeholder={
                      "https://example.com\nhttps://www.example.com"
                    }
                  />


                  <p className="text-xs text-slate-500">
                    One origin per line.
                    Include the scheme,
                    such as https://.
                  </p>

                </div>


                <div className="space-y-2">

                  <Label
                    htmlFor="widget-title"
                  >
                    Widget Title
                  </Label>


                  <Input
                    id="widget-title"
                    value={
                      widgetTitle
                    }
                    onChange={(
                      event,
                    ) =>
                      setWidgetTitle(
                        event
                          .currentTarget
                          .value,
                      )
                    }
                    placeholder="NXTGEN Assistant"
                  />

                </div>


                <div className="space-y-2">

                  <Label
                    htmlFor="welcome-message"
                  >
                    Welcome Message
                  </Label>


                  <Input
                    id="welcome-message"
                    value={
                      welcomeMessage
                    }
                    onChange={(
                      event,
                    ) =>
                      setWelcomeMessage(
                        event
                          .currentTarget
                          .value,
                      )
                    }
                    placeholder="Hi! How can I help?"
                  />

                </div>


                <div className="space-y-2">

                  <Label
                    htmlFor="placeholder"
                  >
                    Input Placeholder
                  </Label>


                  <Input
                    id="placeholder"
                    value={
                      placeholder
                    }
                    onChange={(
                      event,
                    ) =>
                      setPlaceholder(
                        event
                          .currentTarget
                          .value,
                      )
                    }
                    placeholder="Ask me anything..."
                  />

                </div>


                <label className="flex items-start gap-3 rounded-lg border p-4">

                  <input
                    type="checkbox"
                    checked={
                      showSources
                    }
                    onChange={(
                      event,
                    ) =>
                      setShowSources(
                        event
                          .currentTarget
                          .checked,
                      )
                    }
                    className="mt-1 h-4 w-4"
                  />


                  <div>

                    <p className="text-sm font-medium text-slate-900">
                      Show sources
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Display source documents
                      below chatbot answers.
                    </p>

                  </div>

                </label>


                <div className="rounded-lg bg-slate-50 p-4">

                  <p className="text-sm font-medium text-slate-900">
                    Website security
                  </p>

                  <p className="mt-1 text-xs leading-5 text-slate-600">
                    Only configured website
                    origins can initialize
                    this widget. Visitors
                    receive short-lived signed
                    session tokens.
                  </p>

                </div>

              </>
            )}


            {type === "PUBLIC_API" && (
              <div className="rounded-lg bg-blue-50 p-4">

                <p className="text-sm font-medium text-blue-900">
                  Server-to-server API
                </p>

                <p className="mt-1 text-xs leading-5 text-blue-800">
                  After creating the channel,
                  you can generate and revoke
                  secret API keys from the
                  channel management screen.
                </p>

              </div>
            )}


            {type === "SLACK" && (
              <div className="space-y-4">

                <div className="rounded-lg bg-violet-50 p-4">

                  <p className="text-sm font-medium text-violet-900">
                    Slack workspace
                  </p>

                  <p className="mt-1 text-xs leading-5 text-violet-800">
                    Create the Slack channel
                    first. Then use
                    Manage Slack to connect
                    the workspace, bot token,
                    signing secret, and
                    allowed Slack channels.
                  </p>

                </div>


                <label className="flex items-start gap-3 rounded-lg border p-4">

                  <input
                    type="checkbox"
                    checked={
                      slackRespondToMentions
                    }
                    onChange={(
                      event,
                    ) =>
                      setSlackRespondToMentions(
                        event
                          .currentTarget
                          .checked,
                      )
                    }
                    className="mt-1 h-4 w-4"
                  />


                  <div>

                    <p className="text-sm font-medium text-slate-900">
                      Respond to mentions
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Respond when a Slack
                      user mentions the
                      NXTGEN bot in a channel.
                    </p>

                  </div>

                </label>


                <label className="flex items-start gap-3 rounded-lg border p-4">

                  <input
                    type="checkbox"
                    checked={
                      slackRespondToDirectMessages
                    }
                    onChange={(
                      event,
                    ) =>
                      setSlackRespondToDirectMessages(
                        event
                          .currentTarget
                          .checked,
                      )
                    }
                    className="mt-1 h-4 w-4"
                  />


                  <div>

                    <p className="text-sm font-medium text-slate-900">
                      Respond to direct messages
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Allow users to ask
                      questions directly to
                      the NXTGEN Slack bot.
                    </p>

                  </div>

                </label>


                <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">

                  <p className="text-sm font-medium text-slate-900">
                    Next step after creation
                  </p>

                  <p className="mt-1 text-xs leading-5 text-slate-600">
                    Open the new Slack channel
                    card and select
                    Manage Slack to complete
                    the workspace connection.
                  </p>

                </div>

              </div>
            )}


            {error && (
              <p className="text-sm text-red-600">
                {
                  error
                }
              </p>
            )}


            <DialogFooter>

              <button
                type="button"
                onClick={() =>
                  setOpen(
                    false,
                  )
                }
                disabled={
                  submitting
                }
                className="rounded-lg border border-slate-200 bg-white px-5 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
              >
                Cancel
              </button>


              <button
                type="submit"
                disabled={
                  submitting
                }
                className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {
                  submitting
                    ? "Creating..."
                    : "Create Channel"
                }
              </button>

            </DialogFooter>

          </form>

        </DialogContent>
      </Dialog>
    </>
  );
}