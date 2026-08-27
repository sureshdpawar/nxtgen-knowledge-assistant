"use client";

import { useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";

import {
  BrainCircuit,
  Database,
  ExternalLink,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import type { LoginRequest } from "@/types/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
  } = useForm<LoginRequest>();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  async function onSubmit(data: LoginRequest) {
    try {
      setLoading(true);
      setError("");

      await login(data);

      router.push("/dashboard");
    } catch {
      setError("Invalid email or password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      className="
        min-h-dvh
        bg-slate-100
      "
    >
      <div
        className="
          mx-auto
          flex
          min-h-dvh
          w-full
          max-w-[1600px]
          items-stretch

          lg:p-6
          xl:p-8
        "
      >
        <div
          className="
            grid
            min-h-dvh
            w-full
            overflow-hidden
            bg-white

            lg:min-h-[calc(100dvh-3rem)]
            lg:grid-cols-[1.05fr_0.95fr]
            lg:rounded-3xl
            lg:border
            lg:border-slate-200
            lg:shadow-2xl

            xl:min-h-[calc(100dvh-4rem)]
          "
        >
          {/*
           * =====================================================
           * LEFT BRAND PANEL
           * =====================================================
           */}
          <section
            className="
              relative
              overflow-hidden

              bg-gradient-to-br
              from-slate-800
              via-blue-900
              to-indigo-800

              px-6
              pb-10
              pt-7
              text-white

              sm:px-8

              lg:flex
              lg:min-h-full
              lg:flex-col
              lg:justify-between
              lg:px-12
              lg:py-12

              xl:px-16
              xl:py-14
            "
          >
            {/*
             * Cyan glow - upper left
             */}
            <div
              className="
                pointer-events-none
                absolute
                -left-24
                -top-20
                h-96
                w-96
                rounded-full
                bg-cyan-400/20
                blur-3xl
              "
            />

            {/*
             * Blue glow - center
             */}
            <div
              className="
                pointer-events-none
                absolute
                left-1/3
                top-1/3
                h-96
                w-96
                rounded-full
                bg-blue-500/15
                blur-3xl
              "
            />

            {/*
             * Violet glow - lower right
             */}
            <div
              className="
                pointer-events-none
                absolute
                -right-24
                bottom-10
                h-96
                w-96
                rounded-full
                bg-violet-500/25
                blur-3xl
              "
            />

            {/*
             * Soft color overlay
             */}
            <div
              className="
                pointer-events-none
                absolute
                inset-0

                bg-gradient-to-tr
                from-cyan-400/5
                via-transparent
                to-violet-500/10
              "
            />

            {/*
             * Very subtle light at top
             */}
            <div
              className="
                pointer-events-none
                absolute
                inset-x-0
                top-0
                h-40

                bg-gradient-to-b
                from-white/[0.04]
                to-transparent
              "
            />

            {/*
             * ===================================================
             * LOGO
             * ===================================================
             */}
            <div className="relative z-10">
              <div
                className="
                  mx-auto
                  max-w-[360px]

                  lg:mx-0
                  lg:max-w-[500px]
                "
              >
                <Image
                  src="/branding/knowgentiq-logo.png"
                  alt="Knowgentiq - AI in Perspective"
                  width={1400}
                  height={850}
                  priority
                  className="
                    h-auto
                    w-full
                    object-contain

                    brightness-[1.22]
                    contrast-[1.08]
                    saturate-[1.05]

                    drop-shadow-[0_0_14px_rgba(96,165,250,0.22)]
                  "
                />
              </div>

              {/*
               * Mobile product category
               */}
              <div
                className="
                  mx-auto
                  mt-1
                  max-w-md
                  text-center

                  lg:hidden
                "
              >
                <p
                  className="
                    text-sm
                    font-medium
                    leading-6
                    text-blue-100
                  "
                >
                  Enterprise Knowledge
                  &amp; AI Intelligence Platform
                </p>
              </div>
            </div>

            {/*
             * ===================================================
             * DESKTOP PRODUCT STORY
             * ===================================================
             */}
            <div
              className="
                relative
                z-10
                hidden
                max-w-xl

                lg:block
              "
            >
              <h1
                className="
                  text-3xl
                  font-semibold
                  leading-tight
                  tracking-tight
                  text-white

                  xl:text-4xl
                "
              >
                Enterprise{" "}
                <span className="text-cyan-300">
                  Knowledge
                </span>{" "}
                &amp; AI{" "}
                <span className="text-violet-300">
                  Intelligence
                </span>{" "}
                Platform
              </h1>

              <p
                className="
                  mt-5
                  max-w-lg
                  text-base
                  leading-7
                  text-blue-100/90
                "
              >
                Build, evaluate and operate trusted AI experiences
                grounded in enterprise knowledge.
              </p>

              <div
                className="
                  mt-10
                  space-y-6
                "
              >
                <Feature
                  icon={ShieldCheck}
                  title="Trusted AI"
                  description="Ground AI experiences in governed enterprise knowledge."
                  accent="blue"
                />

                <Feature
                  icon={Database}
                  title="Knowledge Driven"
                  description="Connect, manage and retrieve knowledge across enterprise sources."
                  accent="cyan"
                />

                <Feature
                  icon={BrainCircuit}
                  title="AI Intelligence"
                  description="Evaluate quality, understand performance and continuously improve AI outcomes."
                  accent="violet"
                />

                <Feature
                  icon={Sparkles}
                  title="Enterprise Ready"
                  description="Designed for secure, scalable and governed AI adoption."
                  accent="purple"
                />
              </div>
            </div>

            {/*
             * ===================================================
             * DECORATIVE DATA WAVES
             * ===================================================
             */}
            <div
              className="
                pointer-events-none
                absolute
                inset-x-0
                bottom-0
                hidden
                h-36
                opacity-80

                lg:block
              "
            >
              <svg
                viewBox="0 0 1200 180"
                preserveAspectRatio="none"
                className="
                  h-full
                  w-full
                "
                aria-hidden="true"
              >
                <path
                  d="
                    M0,100
                    C120,40 220,145 360,95
                    C500,45 570,135 720,90
                    C860,45 930,120 1200,45
                  "
                  fill="none"
                  stroke="rgba(34,211,238,0.55)"
                  strokeWidth="2"
                />

                <path
                  d="
                    M0,125
                    C130,75 250,155 390,110
                    C540,65 630,145 760,105
                    C910,60 1010,120 1200,80
                  "
                  fill="none"
                  stroke="rgba(96,165,250,0.65)"
                  strokeWidth="2"
                />

                <path
                  d="
                    M0,145
                    C160,105 260,165 440,130
                    C600,95 740,150 900,120
                    C1040,95 1110,115 1200,100
                  "
                  fill="none"
                  stroke="rgba(196,181,253,0.55)"
                  strokeWidth="1.5"
                />
              </svg>
            </div>
          </section>

          {/*
           * =====================================================
           * RIGHT SIGN-IN PANEL
           * =====================================================
           */}
          <section
            className="
              relative
              flex
              flex-1
              bg-white
              px-5
              pb-8
              pt-8

              sm:px-8
              sm:pt-10

              lg:min-h-full
              lg:px-12
              lg:py-12

              xl:px-20
            "
          >
            <div
              className="
                mx-auto
                flex
                w-full
                max-w-md
                flex-col
              "
            >
              {/*
               * =================================================
               * DESKTOP LOGO ON WHITE SIDE
               * =================================================
               */}
              <div
                className="
                  mb-8
                  hidden

                  lg:block
                "
              >
                <Image
                  src="/branding/knowgentiq-logo.png"
                  alt="Knowgentiq - AI in Perspective"
                  width={700}
                  height={400}
                  className="
                    h-auto
                    w-64
                    object-contain
                    object-left
                  "
                />
              </div>

              {/*
               * =================================================
               * LOGIN CONTENT
               * =================================================
               */}
              <div
                className="
                  flex
                  flex-1
                  flex-col
                  justify-center
                "
              >
                <div>
                  <h2
                    className="
                      text-2xl
                      font-semibold
                      tracking-tight
                      text-slate-950

                      sm:text-3xl
                    "
                  >
                    Welcome back
                  </h2>

                  <p
                    className="
                      mt-2
                      text-sm
                      text-slate-500
                    "
                  >
                    Sign in to your Knowgentiq account.
                  </p>
                </div>

                <form
                  onSubmit={handleSubmit(onSubmit)}
                  className="
                    mt-8
                    space-y-5
                  "
                >
                  {/*
                   * EMAIL
                   */}
                  <div>
                    <label
                      htmlFor="email"
                      className="
                        mb-2
                        block
                        text-sm
                        font-medium
                        text-slate-700
                      "
                    >
                      Email address
                    </label>

                    <div className="relative">
                      <Mail
                        className="
                          pointer-events-none
                          absolute
                          left-3.5
                          top-1/2
                          h-4
                          w-4
                          -translate-y-1/2
                          text-slate-400
                        "
                      />

                      <input
                        id="email"
                        type="email"
                        autoComplete="email"
                        placeholder="Enter your email"
                        {...register("email", {
                          required: true,
                        })}
                        className="
                          h-12
                          w-full
                          rounded-xl
                          border
                          border-slate-300
                          bg-white
                          pl-10
                          pr-4
                          text-sm
                          text-slate-900
                          outline-none
                          transition

                          placeholder:text-slate-400

                          hover:border-slate-400

                          focus:border-blue-500
                          focus:ring-4
                          focus:ring-blue-500/10
                        "
                      />
                    </div>
                  </div>

                  {/*
                   * PASSWORD
                   */}
                  <div>
                    <label
                      htmlFor="password"
                      className="
                        mb-2
                        block
                        text-sm
                        font-medium
                        text-slate-700
                      "
                    >
                      Password
                    </label>

                    <div className="relative">
                      <LockKeyhole
                        className="
                          pointer-events-none
                          absolute
                          left-3.5
                          top-1/2
                          h-4
                          w-4
                          -translate-y-1/2
                          text-slate-400
                        "
                      />

                      <input
                        id="password"
                        type={
                          showPassword
                            ? "text"
                            : "password"
                        }
                        autoComplete="current-password"
                        placeholder="Enter your password"
                        {...register("password", {
                          required: true,
                        })}
                        className="
                          h-12
                          w-full
                          rounded-xl
                          border
                          border-slate-300
                          bg-white
                          pl-10
                          pr-11
                          text-sm
                          text-slate-900
                          outline-none
                          transition

                          placeholder:text-slate-400

                          hover:border-slate-400

                          focus:border-blue-500
                          focus:ring-4
                          focus:ring-blue-500/10
                        "
                      />

                      <button
                        type="button"
                        onClick={() =>
                          setShowPassword(
                            (current) => !current,
                          )
                        }
                        aria-label={
                          showPassword
                            ? "Hide password"
                            : "Show password"
                        }
                        className="
                          absolute
                          right-3
                          top-1/2
                          inline-flex
                          h-8
                          w-8
                          -translate-y-1/2
                          items-center
                          justify-center
                          rounded-lg
                          text-slate-400
                          transition

                          hover:bg-slate-100
                          hover:text-slate-700
                        "
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/*
                   * LOGIN ERROR
                   */}
                  {error && (
                    <div
                      role="alert"
                      className="
                        rounded-xl
                        border
                        border-red-200
                        bg-red-50
                        px-4
                        py-3
                        text-sm
                        text-red-700
                      "
                    >
                      {error}
                    </div>
                  )}

                  {/*
                   * SIGN IN
                   */}
                  <button
                    type="submit"
                    disabled={loading}
                    className="
                      flex
                      h-12
                      w-full
                      items-center
                      justify-center
                      rounded-xl

                      bg-gradient-to-r
                      from-blue-600
                      via-indigo-600
                      to-violet-600

                      px-5
                      text-sm
                      font-semibold
                      text-white

                      shadow-lg
                      shadow-blue-600/15

                      transition

                      hover:brightness-110

                      focus:outline-none
                      focus:ring-4
                      focus:ring-blue-500/20

                      disabled:cursor-not-allowed
                      disabled:opacity-60
                    "
                  >
                    {loading
                      ? "Signing in..."
                      : "Sign In"}
                  </button>
                </form>

                {/*
                 * =================================================
                 * SECURE ACCESS
                 * =================================================
                 */}
                <div
                  className="
                    mt-9
                    border-t
                    border-slate-200
                    pt-6
                    text-center
                  "
                >
                  <div
                    className="
                      mx-auto
                      mb-3
                      flex
                      h-8
                      w-8
                      items-center
                      justify-center
                      rounded-full
                      bg-blue-50
                      text-blue-600
                    "
                  >
                    <LockKeyhole className="h-4 w-4" />
                  </div>

                  <p
                    className="
                      text-xs
                      leading-5
                      text-slate-400
                    "
                  >
                    Secure access to enterprise knowledge
                    and AI services.
                  </p>
                </div>
              </div>

              {/*
               * =================================================
               * NXTGEN PRODUCT ATTRIBUTION
               * =================================================
               */}
              <div
                className="
                  mt-8
                  shrink-0
                  border-t
                  border-slate-100
                  pt-5
                  text-center

                  lg:mt-10
                "
              >
                <p
                  className="
                    text-xs
                    font-medium
                    uppercase
                    tracking-[0.14em]
                    text-slate-400
                  "
                >
                  A product of
                </p>

                <p
                  className="
                    mt-1.5
                    text-sm
                    font-semibold
                    text-slate-800
                  "
                >
                  NXTGEN Innovate Technologies
                </p>

                <a
                  href="https://www.nxtgeninnovate.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="
                    mt-2
                    inline-flex
                    items-center
                    gap-1.5

                    rounded-md

                    text-sm
                    font-medium
                    text-blue-600

                    transition

                    hover:text-blue-700
                    hover:underline

                    focus:outline-none
                    focus:ring-2
                    focus:ring-blue-500
                    focus:ring-offset-2
                  "
                >
                  www.nxtgeninnovate.com

                  <ExternalLink
                    className="
                      h-3.5
                      w-3.5
                    "
                  />
                </a>
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}

type FeatureProps = {
  icon: React.ComponentType<{
    className?: string;
  }>;

  title: string;
  description: string;

  accent:
    | "blue"
    | "cyan"
    | "violet"
    | "purple";
};

function Feature({
  icon: Icon,
  title,
  description,
  accent,
}: FeatureProps) {
  const accentClasses = {
    blue:
      "border-blue-300/40 text-blue-200 bg-blue-400/10",

    cyan:
      "border-cyan-300/40 text-cyan-200 bg-cyan-400/10",

    violet:
      "border-violet-300/40 text-violet-200 bg-violet-400/10",

    purple:
      "border-purple-300/40 text-purple-200 bg-purple-400/10",
  };

  return (
    <div
      className="
        flex
        items-start
        gap-4
      "
    >
      <div
        className={`
          flex
          h-11
          w-11
          shrink-0
          items-center
          justify-center
          rounded-xl
          border
          backdrop-blur-sm

          ${accentClasses[accent]}
        `}
      >
        <Icon className="h-5 w-5" />
      </div>

      <div>
        <h3
          className="
            text-sm
            font-semibold
            text-white
          "
        >
          {title}
        </h3>

        <p
          className="
            mt-1
            max-w-sm
            text-sm
            leading-5
            text-blue-100/75
          "
        >
          {description}
        </p>
      </div>
    </div>
  );
}