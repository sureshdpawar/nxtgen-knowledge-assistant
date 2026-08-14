"use client";

import {
  useState,
} from "react";

import type {
  FormEvent,
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
  useCreateLLMProfile,
} from "../hooks";

import {
  LLM_PROVIDERS,
} from "../types";

import type {
  LLMProvider,
} from "../types";


export default function CreateLLMProfileDialog() {
  const mutation =
    useCreateLLMProfile();

  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    name,
    setName,
  ] = useState("");

  const [
    provider,
    setProvider,
  ] = useState<LLMProvider>(
    "OPENAI",
  );

  const [
    modelName,
    setModelName,
  ] = useState("");

  const [
    baseUrl,
    setBaseUrl,
  ] = useState(
    "https://api.openai.com/v1",
  );

  const [
    apiKey,
    setApiKey,
  ] = useState("");

  const [
    temperature,
    setTemperature,
  ] = useState("0");

  const [
    maxTokens,
    setMaxTokens,
  ] = useState("2048");

  const [
    isActive,
    setIsActive,
  ] = useState(true);

  const [
    isDefault,
    setIsDefault,
  ] = useState(false);


  function resetForm() {
    setName("");

    setProvider(
      "OPENAI",
    );

    setModelName("");

    setBaseUrl(
      "https://api.openai.com/v1",
    );

    setApiKey("");

    setTemperature(
      "0",
    );

    setMaxTokens(
      "2048",
    );

    setIsActive(
      true,
    );

    setIsDefault(
      false,
    );
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


  async function submit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    try {
      await mutation.mutateAsync({
        name:
          name.trim(),

        provider,

        model_name:
          modelName.trim(),

        base_url:
          baseUrl.trim(),

        api_key:
          apiKey.trim(),

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

        is_default:
          isDefault,
      });

      resetForm();

      setOpen(
        false,
      );
    } catch {
      // Error displayed below.
    }
  }


  function handleProviderChange(
    value: string,
  ) {
    const nextProvider =
      LLM_PROVIDERS.find(
        (
          item,
        ) =>
          item === value,
      );

    if (!nextProvider) {
      return;
    }

    setProvider(
      nextProvider,
    );

    if (
      nextProvider ===
      "OPENAI"
    ) {
      setBaseUrl(
        "https://api.openai.com/v1",
      );
    }
  }


  return (
    <>
      <Button
        type="button"
        onClick={() =>
          setOpen(
            true,
          )
        }
      >
        <Plus className="mr-2 h-4 w-4" />

        Add LLM Profile
      </Button>


      <Dialog
        open={
          open
        }
        onOpenChange={
          handleOpenChange
        }
      >
        <DialogContent className="sm:max-w-xl">

          <DialogHeader>

            <DialogTitle>
              Add LLM Profile
            </DialogTitle>

            <DialogDescription>
              Create a reusable LLM
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
                placeholder="General Assistant"
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
                  (
                    item,
                  ) => (
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
                placeholder="gpt-4.1-mini"
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
                placeholder="https://api.openai.com/v1"
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
                placeholder="Enter API key"
                autoComplete="new-password"
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                required
              />
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


            <label className="flex items-center gap-2 text-sm text-slate-700">

              <input
                type="checkbox"
                checked={
                  isDefault
                }
                onChange={(
                  event,
                ) =>
                  setIsDefault(
                    event.target.checked,
                  )
                }
              />

              Make tenant default

            </label>


            {mutation.isError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to create LLM
                profile.
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
                  mutation.isPending ||
                  !name.trim() ||
                  !modelName.trim() ||
                  !baseUrl.trim() ||
                  !apiKey.trim()
                }
              >
                {
                  mutation.isPending
                    ? "Creating..."
                    : "Create Profile"
                }
              </Button>

            </DialogFooter>

          </form>

        </DialogContent>
      </Dialog>
    </>
  );
}