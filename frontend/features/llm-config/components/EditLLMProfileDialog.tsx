"use client";

import {
  useEffect,
  useState,
} from "react";

import type {
  FormEvent,
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
  useUpdateLLMProfile,
} from "../hooks";

import {
  LLM_PROVIDERS,
} from "../types";

import type {
  LLMProfile,
  LLMProvider,
} from "../types";


type Props = {
  profile: LLMProfile;
};


export default function EditLLMProfileDialog({
  profile,
}: Props) {
  const mutation =
    useUpdateLLMProfile();

  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    name,
    setName,
  ] = useState(
    profile.name,
  );

  const [
    provider,
    setProvider,
  ] = useState<LLMProvider>(
    profile.provider,
  );

  const [
    modelName,
    setModelName,
  ] = useState(
    profile.model_name,
  );

  const [
    baseUrl,
    setBaseUrl,
  ] = useState(
    profile.base_url,
  );

  const [
    apiKey,
    setApiKey,
  ] = useState("");

  const [
    temperature,
    setTemperature,
  ] = useState(
    String(
      profile.temperature,
    ),
  );

  const [
    maxTokens,
    setMaxTokens,
  ] = useState(
    String(
      profile.max_tokens,
    ),
  );

  const [
    isActive,
    setIsActive,
  ] = useState(
    profile.is_active,
  );


  useEffect(() => {
    if (!open) {
      return;
    }

    setName(
      profile.name,
    );

    setProvider(
      profile.provider,
    );

    setModelName(
      profile.model_name,
    );

    setBaseUrl(
      profile.base_url,
    );

    setApiKey("");

    setTemperature(
      String(
        profile.temperature,
      ),
    );

    setMaxTokens(
      String(
        profile.max_tokens,
      ),
    );

    setIsActive(
      profile.is_active,
    );
  }, [
    open,
    profile,
  ]);


  function handleProviderChange(
    value: string,
  ) {
    const nextProvider =
      LLM_PROVIDERS.find(
        (item) =>
          item === value,
      );

    if (!nextProvider) {
      return;
    }

    setProvider(
      nextProvider,
    );
  }


  async function submit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const data: {
      name: string;
      provider: LLMProvider;
      model_name: string;
      base_url: string;
      temperature: number;
      max_tokens: number;
      is_active: boolean;
      api_key?: string;
    } = {
      name:
        name.trim(),

      provider,

      model_name:
        modelName.trim(),

      base_url:
        baseUrl.trim(),

      temperature:
        Number(
          temperature,
        ),

      max_tokens:
        Number(
          maxTokens,
        ),

      is_active:
        isActive,
    };

    if (
      apiKey.trim()
    ) {
      data.api_key =
        apiKey.trim();
    }

    try {
      await mutation.mutateAsync({
        id:
          profile.id,

        data,
      });

      setOpen(
        false,
      );
    } catch {
      // Error shown below.
    }
  }


  return (
    <>
      <Button
        type="button"
        variant="outline"
        onClick={() =>
          setOpen(
            true,
          )
        }
      >
        <Pencil className="mr-2 h-4 w-4" />

        Edit
      </Button>


      <Dialog
        open={
          open
        }
        onOpenChange={
          setOpen
        }
      >
        <DialogContent className="sm:max-w-xl">

          <DialogHeader>

            <DialogTitle>
              Edit LLM Profile
            </DialogTitle>

            <DialogDescription>
              Update the reusable LLM
              configuration for this
              tenant.
            </DialogDescription>

          </DialogHeader>


          <form
            onSubmit={
              submit
            }
            className="space-y-5"
          >

            <div>
              <label className="text-sm font-medium text-slate-700">
                Profile Name
              </label>

              <input
                value={
                  name
                }
                onChange={(
                  event,
                ) =>
                  setName(
                    event.target.value,
                  )
                }
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                required
              />
            </div>


            <div>
              <label className="text-sm font-medium text-slate-700">
                Provider
              </label>

              <select
                value={
                  provider
                }
                onChange={(
                  event,
                ) =>
                  handleProviderChange(
                    event.target.value,
                  )
                }
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              >
                {LLM_PROVIDERS.map(
                  (item) => (
                    <option
                      key={
                        item
                      }
                      value={
                        item
                      }
                    >
                      {
                        item === "OPENAI"
                          ? "OpenAI"
                          : item ===
                              "AZURE_OPENAI"
                            ? "Azure OpenAI"
                            : "vLLM"
                      }
                    </option>
                  ),
                )}
              </select>
            </div>


            <div>
              <label className="text-sm font-medium text-slate-700">
                Model Name
              </label>

              <input
                value={
                  modelName
                }
                onChange={(
                  event,
                ) =>
                  setModelName(
                    event.target.value,
                  )
                }
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                required
              />
            </div>


            <div>
              <label className="text-sm font-medium text-slate-700">
                Base URL
              </label>

              <input
                value={
                  baseUrl
                }
                onChange={(
                  event,
                ) =>
                  setBaseUrl(
                    event.target.value,
                  )
                }
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                required
              />
            </div>


            <div>
              <label className="text-sm font-medium text-slate-700">
                API Key
              </label>

              <input
                type="password"
                value={
                  apiKey
                }
                onChange={(
                  event,
                ) =>
                  setApiKey(
                    event.target.value,
                  )
                }
                placeholder="Leave blank to keep existing key"
                autoComplete="new-password"
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              />

              <p className="mt-1 text-xs text-slate-400">
                Leave blank to keep the
                current API key.
              </p>
            </div>


            <div className="grid gap-4 md:grid-cols-2">

              <div>
                <label className="text-sm font-medium text-slate-700">
                  Temperature
                </label>

                <input
                  type="number"
                  min="0"
                  max="2"
                  step="0.1"
                  value={
                    temperature
                  }
                  onChange={(
                    event,
                  ) =>
                    setTemperature(
                      event.target.value,
                    )
                  }
                  className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  required
                />
              </div>


              <div>
                <label className="text-sm font-medium text-slate-700">
                  Max Tokens
                </label>

                <input
                  type="number"
                  min="1"
                  value={
                    maxTokens
                  }
                  onChange={(
                    event,
                  ) =>
                    setMaxTokens(
                      event.target.value,
                    )
                  }
                  className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  required
                />
              </div>

            </div>


            <label className="flex items-center gap-2 text-sm text-slate-700">

              <input
                type="checkbox"
                checked={
                  isActive
                }
                onChange={(
                  event,
                ) =>
                  setIsActive(
                    event.target.checked,
                  )
                }
              />

              Active

            </label>


            {profile.is_default && (
              <div className="rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-blue-700">
                This is the tenant
                default profile.
              </div>
            )}


            {mutation.isError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to update LLM
                profile.
              </div>
            )}


            <DialogFooter>

              <Button
                type="button"
                variant="outline"
                disabled={
                  mutation.isPending
                }
                onClick={() =>
                  setOpen(
                    false,
                  )
                }
              >
                Cancel
              </Button>


              <Button
                type="submit"
                disabled={
                  mutation.isPending ||
                  !name.trim() ||
                  !modelName.trim() ||
                  !baseUrl.trim()
                }
              >
                {
                  mutation.isPending
                    ? "Saving..."
                    : "Save Changes"
                }
              </Button>

            </DialogFooter>

          </form>

        </DialogContent>
      </Dialog>
    </>
  );
}