// features/users/components/UserCard.tsx

import {
  User as UserIcon,
} from "lucide-react";

import type {
  User,
} from "../types";

import EditUserDialog from "./EditUserDialog";


type Props = {
  user: User;
};


export default function UserCard({
  user,
}: Props) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">

      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

        <div className="flex min-w-0 items-start gap-3">

          <div className="rounded-full bg-blue-100 p-3">
            <UserIcon className="h-5 w-5 text-blue-600" />
          </div>


          <div className="min-w-0">

            <h3 className="font-semibold text-slate-900">
              {user.first_name}{" "}
              {user.last_name}
            </h3>

            <p className="mt-1 truncate text-sm text-slate-500">
              {user.email}
            </p>

            <p className="mt-2 break-all text-xs text-slate-400">
              User ID:{" "}
              {user.id}
            </p>

          </div>

        </div>


        <div className="flex flex-wrap items-center gap-2">

          <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
            {user.role}
          </span>


          <span
            className={
              user.is_active
                ? "rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700"
                : "rounded-full bg-red-50 px-3 py-1 text-xs font-medium text-red-700"
            }
          >
            {user.is_active
              ? "ACTIVE"
              : "INACTIVE"}
          </span>


          {user.role ===
            "USER" && (
            <EditUserDialog
              user={
                user
              }
            />
          )}

        </div>

      </div>

    </div>
  );
}