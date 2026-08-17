"use client";

import {
  LogOut,
  Settings,
} from "lucide-react";

import {
  useRouter,
} from "next/navigation";

import {
  useAuth,
} from "@/hooks/useAuth";

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
  const router =
    useRouter();

  const {
    user,
    logout,
  } =
    useAuth();


  function initials() {
    if (!user) {
      return "NA";
    }

    const firstInitial =
      user.first_name
        ?.charAt(0)
        .toUpperCase()
      ?? "";

    const lastInitial =
      user.last_name
        ?.charAt(0)
        .toUpperCase()
      ?? "";

    return (
      `${firstInitial}${lastInitial}`
      || "NA"
    );
  }


  function onLogout() {
    logout();

    router.replace(
      "/login",
    );
  }


  function openAccountSettings() {
    router.push(
      "/account",
    );
  }


  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">

      <h1 className="text-xl font-semibold text-slate-900">
        NXTGEN Knowledge Assistant
      </h1>


      <DropdownMenu>

        <DropdownMenuTrigger
          className="rounded-full outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
        >
          <Avatar className="cursor-pointer">

            <AvatarFallback className="bg-blue-50 font-semibold text-blue-700">
              {initials()}
            </AvatarFallback>

          </Avatar>
        </DropdownMenuTrigger>


        <DropdownMenuContent
          align="end"
          className="w-64"
        >

          <div className="px-3 py-3">

            <p className="truncate text-sm font-semibold text-slate-900">
              {user?.first_name}{" "}
              {user?.last_name}
            </p>

            <p className="mt-1 truncate text-xs text-muted-foreground">
              {user?.email}
            </p>


            {user && (
              <div className="mt-2 flex min-w-0 items-center gap-1.5 text-xs text-slate-500">

                <span className="font-medium">
                  {user.role}
                </span>


                {(
                  user.role ===
                    "ADMIN"
                  || user.role ===
                    "USER"
                )
                  && user.tenant_name && (
                  <>
                    <span className="text-slate-300">
                      ·
                    </span>

                    <span className="truncate">
                      {
                        user.tenant_name
                      }
                    </span>
                  </>
                )}

              </div>
            )}

          </div>


          <DropdownMenuSeparator />


          <DropdownMenuGroup>

            <DropdownMenuItem
              onClick={
                openAccountSettings
              }
              className="cursor-pointer"
            >
              <Settings className="mr-2 h-4 w-4" />

              Account Settings
            </DropdownMenuItem>


            <DropdownMenuItem
              onClick={
                onLogout
              }
              className="cursor-pointer text-red-600 focus:text-red-600"
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