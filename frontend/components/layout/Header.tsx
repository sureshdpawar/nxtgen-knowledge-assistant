"use client";

import { LogOut, Settings } from "lucide-react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/hooks/useAuth";

import {
  Avatar,
  AvatarFallback,
} from "@/components/ui/avatar";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export default function Header() {
  const router = useRouter();

  const {
    user,
    logout,
  } = useAuth();

  function initials() {
    if (!user) return "NA";

    return (
      user.first_name[0] +
      user.last_name[0]
    ).toUpperCase();
  }

  function onLogout() {
    logout();

    router.replace("/login");
  }

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">
      <h1 className="text-xl font-semibold">
        NXTGEN Knowledge Assistant
      </h1>

      <DropdownMenu>
        <DropdownMenuTrigger>
          <Avatar className="cursor-pointer">
            <AvatarFallback>
              {initials()}
            </AvatarFallback>
          </Avatar>
        </DropdownMenuTrigger>

        <DropdownMenuContent
          align="end"
          className="w-64"
        >
          <div className="px-3 py-2">
            <p className="font-medium">
              {user?.first_name}{" "}
              {user?.last_name}
            </p>

            <p className="text-xs text-muted-foreground">
              {user?.email}
            </p>
          </div>

          <DropdownMenuSeparator />

          <DropdownMenuGroup>
            <DropdownMenuItem
              onClick={() =>
                router.push("/settings")
              }
            >
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </DropdownMenuItem>

            <DropdownMenuItem
              onClick={onLogout}
            >
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </DropdownMenuItem>
          </DropdownMenuGroup>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}