"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";

import {
  LogOut,
  Menu,
  Settings,
} from "lucide-react";

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


type HeaderProps = {
  onMenuClick?: () => void;
};


export default function Header({
  onMenuClick,
}: HeaderProps) {
  const router = useRouter();

  const {
    user,
    logout,
  } = useAuth();


  function initials() {
    if (!user) {
      return "NA";
    }

    const firstInitial =
      user.first_name
        ?.charAt(0)
        .toUpperCase() ?? "";

    const lastInitial =
      user.last_name
        ?.charAt(0)
        .toUpperCase() ?? "";

    return (
      `${firstInitial}${lastInitial}` ||
      "NA"
    );
  }


  function onLogout() {
    logout();

    router.replace("/login");
  }


  function openAccountSettings() {
    router.push("/account");
  }


  function goToDashboard() {
    router.push("/dashboard");
  }


  return (
    <header
      className="
        relative
        z-40

        flex
        h-[72px]
        shrink-0
        items-center
        justify-between

        border-b
        border-slate-200

        bg-white

        px-3

        shadow-sm

        sm:px-5
        md:px-6
      "
    >

      {/*
       * =====================================================
       * LEFT SIDE
       * Mobile Menu + Knowgentiq Branding
       * =====================================================
       */}
      <div
        className="
          flex
          min-w-0
          items-center

          gap-2

          sm:gap-3
        "
      >

        {/*
         * ===================================================
         * MOBILE MENU BUTTON
         * ===================================================
         */}
        <button
          type="button"
          onClick={onMenuClick}
          aria-label="Open navigation menu"
          className="
            dashboard-mobile-menu-button

            h-10
            w-10

            shrink-0

            items-center
            justify-center

            rounded-lg

            border
            border-slate-200

            bg-white

            text-slate-700

            transition

            hover:border-slate-300
            hover:bg-slate-50
            hover:text-slate-950

            focus:outline-none
            focus:ring-2
            focus:ring-blue-500/30
          "
        >
          <Menu
            className="
              h-5
              w-5
            "
          />
        </button>


        {/*
         * ===================================================
         * BRAND + PRODUCT POSITIONING
         * ===================================================
         */}
        <button
          type="button"
          onClick={goToDashboard}
          aria-label="Go to Knowgentiq dashboard"
          className="
            flex
            min-w-0
            items-center

            gap-3

            rounded-lg

            text-left

            focus:outline-none
            focus:ring-2
            focus:ring-blue-500/30
          "
        >

          {/*
           * =================================================
           * KNOWGENTIQ LOGO
           *
           * Full logo gets enough horizontal room.
           * =================================================
           */}
          <div
            className="
              flex

              h-[52px]

              w-[115px]
              shrink-0

              items-center
              justify-start

              overflow-hidden

              sm:w-[145px]
              md:w-[165px]
              lg:w-[180px]
            "
          >
            <Image
              src="/branding/knowgentiq-logo.png"
              alt="Knowgentiq"
              width={700}
              height={420}
              priority
              className="
                block

                h-auto
                w-full

                object-contain
                object-left
              "
            />
          </div>


          {/*
           * =================================================
           * PRODUCT POSITIONING
           *
           * Logo already contains the Knowgentiq brand,
           * so we don't repeat the product name here.
           * =================================================
           */}
          <div
            className="
              hidden
              min-w-0

              border-l
              border-slate-200

              pl-4

              sm:block
            "
          >

            <div
              className="
                truncate

                text-[15px]
                font-semibold

                leading-tight

                tracking-tight

                text-slate-800

                md:text-base
              "
            >
              Enterprise AI Intelligence Platform
            </div>


            <div
              className="
                mt-1

                truncate

                text-[9px]
                font-medium

                uppercase

                tracking-[0.16em]

                text-slate-400

                md:text-[10px]
              "
            >
              KNOWLEDGE • AGENTS • EVALUATION • GOVERNANCE
            </div>

          </div>

        </button>

      </div>


      {/*
       * =====================================================
       * RIGHT SIDE
       * User Account
       * =====================================================
       */}
      <div
        className="
          ml-3

          flex
          shrink-0
          items-center
        "
      >

        <DropdownMenu>

          {/*
           * =================================================
           * USER AVATAR
           * =================================================
           */}
          <DropdownMenuTrigger
            className="
              rounded-full

              outline-none

              focus-visible:ring-2
              focus-visible:ring-blue-500
              focus-visible:ring-offset-2
            "
          >

            <Avatar
              className="
                h-9
                w-9

                cursor-pointer

                border
                border-blue-100

                shadow-sm

                sm:h-10
                sm:w-10
              "
            >

              <AvatarFallback
                className="
                  bg-gradient-to-br
                  from-blue-50
                  via-indigo-50
                  to-violet-50

                  font-semibold

                  text-blue-700
                "
              >
                {initials()}
              </AvatarFallback>

            </Avatar>

          </DropdownMenuTrigger>


          {/*
           * =================================================
           * ACCOUNT DROPDOWN
           * =================================================
           */}
          <DropdownMenuContent
            align="end"
            className="w-64"
          >

            {/*
             * User Information
             */}
            <div
              className="
                px-3
                py-3
              "
            >

              <p
                className="
                  truncate

                  text-sm
                  font-semibold

                  text-slate-900
                "
              >
                {user?.first_name}{" "}
                {user?.last_name}
              </p>


              <p
                className="
                  mt-1

                  truncate

                  text-xs
                  text-muted-foreground
                "
              >
                {user?.email}
              </p>


              {user && (
                <div
                  className="
                    mt-2

                    flex
                    min-w-0
                    items-center

                    gap-1.5

                    text-xs
                    text-slate-500
                  "
                >

                  <span className="font-medium">
                    {user.role}
                  </span>


                  {(
                    user.role === "ADMIN" ||
                    user.role === "USER"
                  ) &&
                    user.tenant_name && (
                      <>

                        <span className="text-slate-300">
                          ·
                        </span>


                        <span className="truncate">
                          {user.tenant_name}
                        </span>

                      </>
                    )}

                </div>
              )}

            </div>


            <DropdownMenuSeparator />


            <DropdownMenuGroup>

              {/*
               * Account Settings
               */}
              <DropdownMenuItem
                onClick={openAccountSettings}
                className="cursor-pointer"
              >

                <Settings
                  className="
                    mr-2
                    h-4
                    w-4
                  "
                />

                Account Settings

              </DropdownMenuItem>


              {/*
               * Logout
               */}
              <DropdownMenuItem
                onClick={onLogout}
                className="
                  cursor-pointer

                  text-red-600

                  focus:text-red-600
                "
              >

                <LogOut
                  className="
                    mr-2
                    h-4
                    w-4
                  "
                />

                Logout

              </DropdownMenuItem>

            </DropdownMenuGroup>

          </DropdownMenuContent>

        </DropdownMenu>

      </div>

    </header>
  );
}