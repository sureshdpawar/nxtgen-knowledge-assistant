// features/users/components/UserList.tsx

import type {
  User,
} from "../types";

import UserCard from "./UserCard";


type Props = {
  users: User[];
};


export default function UserList({
  users,
}: Props) {
  if (
    users.length === 0
  ) {
    return (
      <div className="rounded-xl border border-dashed bg-white p-8 text-center">

        <h3 className="font-semibold text-slate-900">
          No users
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          Create a user for this
          tenant.
        </p>

      </div>
    );
  }


  return (
    <div className="space-y-3">

      {users.map(
        (user) => (
          <UserCard
            key={
              user.id
            }
            user={
              user
            }
          />
        ),
      )}

    </div>
  );
}