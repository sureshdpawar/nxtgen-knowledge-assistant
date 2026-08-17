"use client";

import {
  type FormEvent,
  useState,
} from "react";

import {
  Pencil,
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
  useUpdateTool,
} from "../hooks";

import {
  TOOL_RISK_LEVELS,
} from "../types";

import type {
  ToolDefinition,
  ToolRiskLevel,
} from "../types";


type Props = {
  tool: ToolDefinition;
};


export default function EditToolDialog({
  tool,
}: Props) {
  const mutation =
    useUpdateTool();

  const integrationsQuery =
    useIntegrations();

  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    name,
    setName,
  ] = useState(
    tool.name,
  );

  const [
    description,
    setDescription,
  ] = useState(
    tool.description,
  );

  const [
    integrationId,
    setIntegrationId,
  ] = useState(
    tool.integration_id
      ?? "",
  );

  const [
    riskLevel,
    setRiskLevel,
  ] = useState<ToolRiskLevel>(
    tool.risk_level,
  );

  const [
    inputSchemaText,
    setInputSchemaText,
  ] = useState(
    JSON.stringify(
      tool.input_schema,
      null,
      2,
    ),
  );

  const [
    configurationText,
    setConfigurationText,
  ] = useState(
    JSON.stringify(
      tool.configuration
        ?? {},
      null,
      2,
    ),
  );

  const [
    active,
    setActive,
  ] = useState(
    tool.is_active,
  );

  const [
    localError,
    setLocalError,
  ] = useState<
    string | null
  >(null);


  const availableIntegrations =
    integrationsQuery.data
      ?.filter(
        (integration) =>
          integration.is_active,
      )
      .filter(
        (integration) => {
          if (
            tool.tool_type ===
            "REST"
          ) {
            return (
              integration.integration_type ===
              "REST"
            );
          }

          if (
            tool.tool_type ===
            "MCP"
          ) {
            return (
              integration.integration_type ===
              "MCP"
            );
          }

          return false;
        },
      )
      ?? [];


  function resetForm() {
    setName(
      tool.name,
    );

    setDescription(
      tool.description,
    );

    setIntegrationId(
      tool.integration_id
        ?? "",
    );

    setRiskLevel(
      tool.risk_level,
    );

    setInputSchemaText(
      JSON.stringify(
        tool.input_schema,
        null,
        2,
      ),
    );

    setConfigurationText(
      JSON.stringify(
        tool.configuration
          ?? {},
        null,
        2,
      ),
    );

    setActive(
      tool.is_active,
    );

    setLocalError(null);
  }


  function handleOpenChange(
    nextOpen: boolean,
  ) {
    setOpen(nextOpen);

    if (nextOpen) {
      resetForm();
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
      tool.tool_type !==
      "NATIVE"
      && !integrationId
    ) {
      setLocalError(
        "Select an integration.",
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
        id:
          tool.id,

        data: {
          integration_id:
            tool.tool_type ===
            "NATIVE"
              ? null
              : integrationId,

          name:
            name.trim(),

          description:
            description.trim(),

          risk_level:
            riskLevel,

          input_schema:
            inputSchema,

          configuration,

          is_active:
            active,
        },
      });

      setOpen(false);

    } catch {
      // Mutation state renders error.
    }
  }


  return (
    <>
      <Button
        type="button"
        size="sm"
        variant="outline"
        onClick={() =>
          handleOpenChange(
            true,
          )
        }
      >
        <Pencil className="mr-2 h-4 w-4" />

        Edit
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
              Edit Tool
            </DialogTitle>

            <DialogDescription>
              Update this agent
              capability.
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
                className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              />

            </div>


            <div className="grid gap-4 md:grid-cols-2">

              <div>

                <label className="text-sm font-medium text-slate-700">
                  Tool Type
                </label>

                <input
                  value={
                    tool.tool_type
                  }
                  disabled
                  className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-slate-50 px-3 text-sm text-slate-500"
                />

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


            {tool.tool_type !==
              "NATIVE" && (
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
                Failed to update tool.
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
                  ? "Saving..."
                  : "Save Changes"}
              </Button>

            </DialogFooter>

          </form>

        </DialogContent>
      </Dialog>
    </>
  );
}