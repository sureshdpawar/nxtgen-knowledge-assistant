"use client";

import {
  type FormEvent,
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
  useCreateIntegration,
} from "../hooks";

import {
  INTEGRATION_AUTH_TYPES,
  INTEGRATION_TYPES,
} from "../types";

import type {
  IntegrationAuthType,
  IntegrationType,
} from "../types";


export default function CreateIntegrationDialog() {
  const mutation =
    useCreateIntegration();

  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    name,
    setName,
  ] = useState("");

  const [
    integrationType,
    setIntegrationType,
  ] = useState<IntegrationType>(
    "REST",
  );

  const [
    baseUrl,
    setBaseUrl,
  ] = useState("");

  const [
    authType,
    setAuthType,
  ] = useState<IntegrationAuthType>(
    "NONE",
  );

  const [
    authValue,
    setAuthValue,
  ] = useState("");

  const [
    active,
    setActive,
  ] = useState(true);


  function resetForm() {
    setName("");
    setIntegrationType(
      "REST",
    );
    setBaseUrl("");
    setAuthType(
      "NONE",
    );
    setAuthValue("");
    setActive(true);
  }


  function handleOpenChange(
    nextOpen: boolean,
  ) {
    setOpen(
      nextOpen,
    );

    if (!nextOpen) {
      resetForm();
    }
  }


  function handleIntegrationTypeChange(
    value: string,
  ) {
    if (
      INTEGRATION_TYPES.includes(
        value as IntegrationType,
      )
    ) {
      setIntegrationType(
        value as IntegrationType,
      );
    }
  }


  function handleAuthTypeChange(
    value: string,
  ) {
    if (
      INTEGRATION_AUTH_TYPES.includes(
        value as IntegrationAuthType,
      )
    ) {
      setAuthType(
        value as IntegrationAuthType,
      );
    }
  }


  function buildAuthConfig() {
    if (
      authType === "NONE"
      || !authValue.trim()
    ) {
      return null;
    }

    if (
      authType === "BEARER"
    ) {
      return {
        token:
          authValue.trim(),
      };
    }

    return {
      value:
        authValue.trim(),
    };
  }


  async function submit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (
      !name.trim()
      || !baseUrl.trim()
    ) {
      return;
    }

    try {
      await mutation.mutateAsync({
        name:
          name.trim(),

        integration_type:
          integrationType,

        base_url:
          baseUrl.trim(),

        auth_type:
          authType,

        auth_config:
          buildAuthConfig(),

        configuration:
          null,

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

        Add Integration
      </Button>


      <Dialog
        open={open}
        onOpenChange={
          handleOpenChange
        }
      >
        <DialogContent className="sm:max-w-2xl">

          <DialogHeader>

            <DialogTitle>
              Add Integration
            </DialogTitle>

            <DialogDescription>
              Connect a REST API or MCP
              server for use by agent tools.
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
                placeholder="Internal ERP"
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              />

            </div>


            <div className="grid gap-4 md:grid-cols-2">

              <div>

                <label className="text-sm font-medium text-slate-700">
                  Type
                </label>

                <select
                  value={
                    integrationType
                  }
                  onChange={(event) =>
                    handleIntegrationTypeChange(
                      event.target.value,
                    )
                  }
                  className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                >

                  <option value="REST">
                    REST API
                  </option>

                  <option value="MCP">
                    MCP Server
                  </option>

                </select>

              </div>


              <div>

                <label className="text-sm font-medium text-slate-700">
                  Authentication
                </label>

                <select
                  value={authType}
                  onChange={(event) =>
                    handleAuthTypeChange(
                      event.target.value,
                    )
                  }
                  className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                >

                  <option value="NONE">
                    None
                  </option>

                  <option value="BEARER">
                    Bearer Token
                  </option>

                  <option value="API_KEY">
                    API Key
                  </option>

                </select>

              </div>

            </div>


            <div>

              <label className="text-sm font-medium text-slate-700">
                {integrationType ===
                "MCP"
                  ? "MCP Endpoint"
                  : "Base URL"}
              </label>

              <input
                value={baseUrl}
                onChange={(event) =>
                  setBaseUrl(
                    event.target.value,
                  )
                }
                placeholder={
                  integrationType ===
                  "MCP"
                    ? "https://example.com/mcp"
                    : "https://api.example.com"
                }
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              />

            </div>


            {authType !== "NONE" && (
              <div>

                <label className="text-sm font-medium text-slate-700">
                  {authType ===
                  "BEARER"
                    ? "Bearer Token"
                    : "API Key"}
                </label>

                <input
                  type="password"
                  value={authValue}
                  onChange={(event) =>
                    setAuthValue(
                      event.target.value,
                    )
                  }
                  placeholder="••••••••••••••••"
                  className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                />

              </div>
            )}


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

              Integration is active

            </label>


            {mutation.isError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to create integration.
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
                  || !baseUrl.trim()
                }
              >
                {mutation.isPending
                  ? "Creating..."
                  : "Add Integration"}
              </Button>

            </DialogFooter>

          </form>

        </DialogContent>
      </Dialog>
    </>
  );
}