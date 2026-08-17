"use client";

import {
  type FormEvent,
  useState,
} from "react";

import {
  CheckCircle2,
  KeyRound,
  UserRound,
} from "lucide-react";

import {
  Button,
} from "@/components/ui/button";

import {
  useAuth,
} from "@/hooks/useAuth";

import {
  useChangePassword,
} from "@/features/account/hooks";


export default function AccountPage() {
  const {
    user,
  } = useAuth();

  const [
    currentPassword,
    setCurrentPassword,
  ] = useState("");

  const [
    newPassword,
    setNewPassword,
  ] = useState("");

  const [
    confirmPassword,
    setConfirmPassword,
  ] = useState("");

  const [
    validationError,
    setValidationError,
  ] = useState<
    string | null
  >(null);

  const changePasswordMutation =
    useChangePassword();


  if (!user) {
    return null;
  }


  async function submit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setValidationError(
      null,
    );

    if (
      !currentPassword
      || !newPassword
      || !confirmPassword
    ) {
      setValidationError(
        "All password fields are required.",
      );

      return;
    }

    if (
      newPassword.length < 8
    ) {
      setValidationError(
        "New password must be at least 8 characters.",
      );

      return;
    }

    if (
      newPassword !==
      confirmPassword
    ) {
      setValidationError(
        "New password and confirmation do not match.",
      );

      return;
    }

    try {
      await changePasswordMutation
        .mutateAsync({
          current_password:
            currentPassword,

          new_password:
            newPassword,
        });

      setCurrentPassword(
        "",
      );

      setNewPassword(
        "",
      );

      setConfirmPassword(
        "",
      );

    } catch {
      // API error is rendered below.
    }
  }


  const tenantLabel =
    (
      user.role === "ADMIN"
      || user.role === "USER"
    )
    && user.tenant_name
      ? user.tenant_name
      : null;


  return (
    <div className="space-y-8">

      <div>

        <p className="text-sm font-medium text-slate-500">
          Account
        </p>

        <h1 className="mt-1 text-3xl font-bold text-slate-900">
          Settings
        </h1>

        <p className="mt-2 text-slate-500">
          Manage your profile context
          and account security.
        </p>

      </div>


      <div className="grid gap-6 xl:grid-cols-[1fr_1.2fr]">

        <section className="rounded-xl border bg-white shadow-sm">

          <div className="flex items-center gap-3 border-b px-6 py-5">

            <div className="rounded-xl bg-blue-50 p-3">
              <UserRound className="h-5 w-5 text-blue-600" />
            </div>

            <div>

              <h2 className="font-semibold text-slate-900">
                Profile
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Your current account context.
              </p>

            </div>

          </div>


          <div className="space-y-5 p-6">

            <ProfileField
              label="Name"
              value={`${user.first_name} ${user.last_name}`}
            />

            <ProfileField
              label="Email"
              value={
                user.email
              }
            />

            <ProfileField
              label="Role"
              value={
                user.role
              }
            />

            {tenantLabel && (
              <ProfileField
                label="Tenant"
                value={
                  tenantLabel
                }
              />
            )}

          </div>

        </section>


        <section className="rounded-xl border bg-white shadow-sm">

          <div className="flex items-center gap-3 border-b px-6 py-5">

            <div className="rounded-xl bg-violet-50 p-3">
              <KeyRound className="h-5 w-5 text-violet-600" />
            </div>

            <div>

              <h2 className="font-semibold text-slate-900">
                Security
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Change your account password.
              </p>

            </div>

          </div>


          <form
            onSubmit={
              submit
            }
            className="space-y-5 p-6"
          >

            <PasswordField
              label="Current Password"
              value={
                currentPassword
              }
              onChange={
                setCurrentPassword
              }
              autoComplete=
                "current-password"
            />


            <PasswordField
              label="New Password"
              value={
                newPassword
              }
              onChange={
                setNewPassword
              }
              autoComplete=
                "new-password"
            />


            <PasswordField
              label="Confirm New Password"
              value={
                confirmPassword
              }
              onChange={
                setConfirmPassword
              }
              autoComplete=
                "new-password"
            />


            {validationError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                {
                  validationError
                }
              </div>
            )}


            {changePasswordMutation.isError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                Unable to change password.
                Check your current password
                and try again.
              </div>
            )}


            {changePasswordMutation.isSuccess && (
              <div className="flex items-center gap-2 rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-700">

                <CheckCircle2 className="h-4 w-4" />

                {
                  changePasswordMutation
                    .data.message
                }

              </div>
            )}


            <Button
              type="submit"
              disabled={
                changePasswordMutation
                  .isPending
              }
            >
              {
                changePasswordMutation
                  .isPending
                  ? "Updating..."
                  : "Update Password"
              }
            </Button>

          </form>

        </section>

      </div>

    </div>
  );
}


type ProfileFieldProps = {
  label: string;
  value: string;
};


function ProfileField({
  label,
  value,
}: ProfileFieldProps) {
  return (
    <div>

      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="mt-1 break-words text-sm font-medium text-slate-800">
        {value}
      </p>

    </div>
  );
}


type PasswordFieldProps = {
  label: string;

  value: string;

  autoComplete:
    string;

  onChange: (
    value: string,
  ) => void;
};


function PasswordField({
  label,
  value,
  autoComplete,
  onChange,
}: PasswordFieldProps) {
  return (
    <div>

      <label className="text-sm font-medium text-slate-700">
        {label}
      </label>

      <input
        type="password"
        value={
          value
        }
        autoComplete={
          autoComplete
        }
        onChange={
          (
            event,
          ) =>
            onChange(
              event.target.value,
            )
        }
        className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm outline-none transition focus:border-blue-500"
      />

    </div>
  );
}