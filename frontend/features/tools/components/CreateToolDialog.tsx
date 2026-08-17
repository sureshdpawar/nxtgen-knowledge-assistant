"use client";

import {
  type FormEvent,
  useMemo,
  useState,
} from "react";

import {
  Plus,
} from "lucide-react";

import {
  Button,
} from "@/components/ui/button";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import {
  useIntegrations,
} from "@/features/integrations/hooks";

import {
  useCreateTool,
} from "../hooks";

import {
  TOOL_RISK_LEVELS,
  TOOL_TYPES,
} from "../types";

import type {
  ToolRiskLevel,
  ToolType,
} from "../types";


export default function CreateToolDialog() {
  const mutation =
    useCreateTool();

  const integrationsQuery =
    useIntegrations();

  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    name,
    setName,
  ] = useState("");

  const [
    description,
    setDescription,
  ] = useState("");

  const [
    toolType,
    setToolType,
  ] = useState<ToolType>(
    "REST",
  );

  const [
    integrationId,
    setIntegrationId,
  ] = useState("");

  const [
    riskLevel,
    setRiskLevel,
  ] = useState<ToolRiskLevel>(
    "READ",
  );

  const [
    inputSchemaText,
    setInputSchemaText,
  ] = useState(
    JSON.stringify(
      {
        type: "object",
        properties: {},
        required: [],
      },
      null,
      2,
    ),
  );

  const [
    configurationText,
    setConfigurationText,
  ] = useState(
    JSON.stringify(
      {},
      null,
      2,
    ),
  );

  const [
    active,
    setActive,
  ] = useState(true);

  const [
    localError,
    setLocalError,
  ] = useState<
    string | null
  >(null);


  const availableIntegrations =
    useMemo(
      () =>
        integrationsQuery.data
          ?.filter(
            (integration) =>
              integration.is_active,
          )
          .filter(
            (integration) => {
              if (
                toolType === "REST"
              ) {
                return (
                  integration.integration_type ===
                  "REST"
                );
              }

              if (
                toolType === "MCP"
              ) {
                return (
                  integration.integration_type ===
                  "MCP"
                );
              }

              return false;
            },
          )
          ?? [],
      [
        integrationsQuery.data,
        toolType,
      ],
    );


  function resetForm() {
    setName("");
    setDescription("");
    setToolType("REST");
    setIntegrationId("");
    setRiskLevel("READ");

    setInputSchemaText(
      JSON.stringify(
        {
          type: "object",
          properties: {},
          required: [],
        },
        null,
        2,
      ),
    );

    setConfigurationText(
      JSON.stringify(
        {},
        null,
        2,
      ),
    );

    setActive(true);
    setLocalError(null);
  }


  function handleOpenChange(
    nextOpen: boolean,
  ) {
    setOpen(nextOpen);

    if (!nextOpen) {
      resetForm();
    }
  }


  function handleToolTypeChange(
    value: string,
  ) {
    if (
      TOOL_TYPES.includes(
        value as ToolType,
      )
    ) {
      const nextType =
        value as ToolType;

      setToolType(
        nextType,
      );

      setIntegrationId("");
    }
  }


  function handleRiskLevelChange(
    value: string,
  ) {
    if (
      TOOL_RISK_LEVELS.includes(
        value as ToolRiskLevel,
      )
    ) {
      setRiskLevel(
        value as ToolRiskLevel,
      );
    }
  }


  async function submit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setLocalError(null);

    if (
      !name.trim()
      || !description.trim()
    ) {
      return;
    }

    if (
      toolType !== "NATIVE"
      && !integrationId
    ) {
      setLocalError(
        "Select an integration for REST or MCP tools.",
      );

      return;
    }

    let inputSchema:
      Record<string, unknown>;

    let configuration:
      Record<string, unknown>
      | null;


    try {
      inputSchema =
        JSON.parse(
          inputSchemaText,
        ) as Record<
          string,
          unknown
        >;
    } catch {
      setLocalError(
        "Input schema must be valid JSON.",
      );

      return;
    }


    try {
      const parsed =
        JSON.parse(
          configurationText,
        ) as Record<
          string,
          unknown
        >;

      configuration =
        Object.keys(
          parsed,
        ).length > 0
          ? parsed
          : null;

    } catch {
      setLocalError(
        "Configuration must be valid JSON.",
      );

      return;
    }


    try {
      await mutation.mutateAsync({
        integration_id:
          toolType === "NATIVE"
            ? null
            : integrationId,

        name:
          name.trim(),

        description:
          description.trim(),

        tool_type:
          toolType,

        risk_level:
          riskLevel,

        input_schema:
          inputSchema,

        configuration,

        is_active:
          active,
      });

      resetForm();
      setOpen(false);

    } catch {
      // Mutation state renders error.
    }
  }


  return (
    <>
      <Button
        type="button"
        onClick={() =>
          setOpen(true)
        }
      >
        <Plus className="mr-2 h-4 w-4" />

        Create Tool
      </Button>


      <Dialog
        open={open}
        onOpenChange={
          handleOpenChange
        }
      >
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-3xl">

          <DialogHeader>

            <DialogTitle>
              Create Tool
            </DialogTitle>

            <DialogDescription>
              Define a capability that
              can later be assigned to
              an agent.
            </DialogDescription>

          </DialogHeader>


          <form
            onSubmit={submit}
            className="space-y-5"
          >

            <div>

              <label className="text-sm font-medium text-slate-700">
                Name
              </label>

              <input
                value={name}
                onChange={(event) =>
                  setName(
                    event.target.value,
                  )
                }
                placeholder="get_purchase_order"
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              />

            </div>


            <div>

              <label className="text-sm font-medium text-slate-700">
                Description
              </label>

              <textarea
                value={description}
                onChange={(event) =>
                  setDescription(
                    event.target.value,
                  )
                }
                rows={3}
                placeholder="Retrieve purchase order details by purchase order ID."
                className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              />

            </div>


            <div className="grid gap-4 md:grid-cols-2">

              <div>

                <label className="text-sm font-medium text-slate-700">
                  Tool Type
                </label>

                <select
                  value={toolType}
                  onChange={(event) =>
                    handleToolTypeChange(
                      event.target.value,
                    )
                  }
                  className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                >

                  <option value="NATIVE">
                    Native
                  </option>

                  <option value="REST">
                    REST
                  </option>

                  <option value="MCP">
                    MCP
                  </option>

                </select>

              </div>


              <div>

                <label className="text-sm font-medium text-slate-700">
                  Risk Level
                </label>

                <select
                  value={riskLevel}
                  onChange={(event) =>
                    handleRiskLevelChange(
                      event.target.value,
                    )
                  }
                  className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                >

                  <option value="READ">
                    Read
                  </option>

                  <option value="WRITE">
                    Write
                  </option>

                </select>

              </div>

            </div>


            {toolType !== "NATIVE" && (
              <div>

                <label className="text-sm font-medium text-slate-700">
                  Integration
                </label>

                <select
                  value={integrationId}
                  onChange={(event) =>
                    setIntegrationId(
                      event.target.value,
                    )
                  }
                  className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                >

                  <option value="">
                    Select integration
                  </option>


                  {availableIntegrations.map(
                    (
                      integration,
                    ) => (
                      <option
                        key={
                          integration.id
                        }
                        value={
                          integration.id
                        }
                      >
                        {
                          integration.name
                        }
                      </option>
                    ),
                  )}

                </select>

              </div>
            )}


            <div>

              <label className="text-sm font-medium text-slate-700">
                Input Schema
              </label>

              <p className="mt-1 text-xs text-slate-500">
                JSON Schema describing
                the arguments the agent
                can provide to this tool.
              </p>

              <textarea
                value={
                  inputSchemaText
                }
                onChange={(event) =>
                  setInputSchemaText(
                    event.target.value,
                  )
                }
                rows={10}
                spellCheck={false}
                className="mt-2 w-full rounded-md border border-slate-200 bg-slate-950 px-3 py-3 font-mono text-xs text-slate-100"
              />

            </div>


            <div>

              <label className="text-sm font-medium text-slate-700">
                Configuration
              </label>

              <p className="mt-1 text-xs text-slate-500">
                Adapter-specific
                configuration. We will
                use this later for REST
                method/path or MCP
                metadata.
              </p>

              <textarea
                value={
                  configurationText
                }
                onChange={(event) =>
                  setConfigurationText(
                    event.target.value,
                  )
                }
                rows={7}
                spellCheck={false}
                className="mt-2 w-full rounded-md border border-slate-200 bg-slate-950 px-3 py-3 font-mono text-xs text-slate-100"
              />

            </div>


            <label className="flex items-center gap-3 text-sm text-slate-700">

              <input
                type="checkbox"
                checked={active}
                onChange={(event) =>
                  setActive(
                    event.target.checked,
                  )
                }
              />

              Tool is active

            </label>


            {localError && (
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
                {localError}
              </div>
            )}


            {mutation.isError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to create tool.
              </div>
            )}


            <DialogFooter>

              <Button
                type="button"
                variant="outline"
                onClick={() =>
                  handleOpenChange(
                    false,
                  )
                }
                disabled={
                  mutation.isPending
                }
              >
                Cancel
              </Button>


              <Button
                type="submit"
                disabled={
                  mutation.isPending
                  || !name.trim()
                  || !description.trim()
                }
              >
                {mutation.isPending
                  ? "Creating..."
                  : "Create Tool"}
              </Button>

            </DialogFooter>

          </form>

        </DialogContent>
      </Dialog>
    </>
  );
}