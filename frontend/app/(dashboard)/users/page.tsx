// app/(dashboard)/users/page.tsx

"use client";

import {
  useUsers,
} from "@/features/users/hooks";

import CreateUserDialog from "@/features/users/components/CreateUserDialog";
import UserList from "@/features/users/components/UserList";


export default function UsersPage() {
  const {
    data,
    isLoading,
    error,
  } =
    useUsers();


  return (
    <div className="space-y-8">

      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">

        <div>

          <p className="text-sm font-medium text-slate-500">
            Tenant Administration
          </p>

          <h1 className="mt-1 text-3xl font-bold text-slate-900">
            Users
          </h1>

          <p className="mt-2 text-slate-500">
            Manage users in your
            tenant.
          </p>

        </div>


        <CreateUserDialog />

      </div>


      {isLoading && (
        <p className="text-sm text-slate-500">
          Loading users...
        </p>
      )}


      {error && (
        <p className="text-sm text-red-600">
          Failed to load users.
        </p>
      )}


      {data && (
        <UserList
          users={
            data
          }
        />
      )}

    </div>
  );
}