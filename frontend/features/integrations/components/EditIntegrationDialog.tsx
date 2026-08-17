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
  useUpdateIntegration,
} from "../hooks";

import {
  INTEGRATION_AUTH_TYPES,
} from "../types";

import type {
  Integration,
  IntegrationAuthType,
} from "../types";


type Props = {
  integration: Integration;
};


export default function EditIntegrationDialog({
  integration,
}: Props) {
  const mutation =
    useUpdateIntegration();

  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    name,
    setName,
  ] = useState(
    integration.name,
  );

  const [
    baseUrl,
    setBaseUrl,
  ] = useState(
    integration.base_url,
  );

  const [
    authType,
    setAuthType,
  ] = useState<IntegrationAuthType>(
    integration.auth_type,
  );

  const [
    authValue,
    setAuthValue,
  ] = useState("");

  const [
    active,
    setActive,
  ] = useState(
    integration.is_active,
  );


  function resetForm() {
    setName(
      integration.name,
    );

    setBaseUrl(
      integration.base_url,
    );

    setAuthType(
      integration.auth_type,
    );

    setAuthValue("");

    setActive(
      integration.is_active,
    );
  }


  function handleOpenChange(
    nextOpen: boolean,
  ) {
    setOpen(
      nextOpen,
    );

    if (nextOpen) {
      resetForm();
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
    ) {
      return null;
    }

    if (!authValue.trim()) {
      return undefined;
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

    const authConfig =
      buildAuthConfig();

    try {
      await mutation.mutateAsync({
        id:
          integration.id,

        data: {
          name:
            name.trim(),

          base_url:
            baseUrl.trim(),

          auth_type:
            authType,

          ...(authConfig !==
          undefined
            ? {
                auth_config:
                  authConfig,
              }
            : {}),

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
        <DialogContent className="sm:max-w-2xl">

          <DialogHeader>

            <DialogTitle>
              Edit Integration
            </DialogTitle>

            <DialogDescription>
              Update connection settings
              for this integration.
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
                Type
              </label>

              <input
                value={
                  integration.integration_type
                }
                disabled
                className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-slate-50 px-3 text-sm text-slate-500"
              />

            </div>


            <div>

              <label className="text-sm font-medium text-slate-700">
                {integration.integration_type ===
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
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              />

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


            {authType !== "NONE" && (
              <div>

                <label className="text-sm font-medium text-slate-700">
                  New Credential
                </label>

                <input
                  type="password"
                  value={authValue}
                  onChange={(event) =>
                    setAuthValue(
                      event.target.value,
                    )
                  }
                  placeholder="Leave blank to keep existing credential"
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
                Failed to update integration.
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