// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { GitHubLogoIcon } from "@radix-ui/react-icons";
import Link from "next/link";

import { useAuthStore } from "~/core/store/auth-store";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { LanguageSwitcher } from "~/components/deer-flow/language-switcher";

export default function LoginPage() {
  const router = useRouter();
  const { isAuthenticated, login, isLoading } = useAuthStore();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [isHydrated, setIsHydrated] = useState(false);

  // 等待 Zustand hydration 完成
  useEffect(() => {
    setIsHydrated(true);
  }, []);

  // useEffect(() => {
  //   if (isHydrated) {
  //     router.push("/chat");
  //   }
  // }, [isHydrated, router]);

  // 检查是否已登录（hydration 完成后才检查）
  useEffect(() => {
    if (isHydrated && isAuthenticated) {
      router.push("/chat");
    }
  }, [isHydrated, isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoggingIn(true);

    try {
      const success = await login(username, password);
      if (success) {
        router.push("/chat");
      } else {
        setError("Invalid username or password");
      }
    } catch {
      setError("Login failed, please try again");
    } finally {
      setIsLoggingIn(false);
    }
  };

  // 在 hydration 完成前不显示内容，避免闪烁
  if (!isHydrated) {
    return null;
  }

  return (
    <div className="relative flex min-h-screen flex-col">
      {/* Header */}
      <header className="supports-backdrop-blur:bg-background/80 bg-background/40 sticky top-0 left-0 z-40 flex h-15 w-full flex-col items-center backdrop-blur-lg">
        <div className="container flex h-15 items-center justify-between px-3">
          <div className="text-xl font-medium">
            <Link href="/" className="flex items-center hover:opacity-80 transition-opacity">
              <span className="mr-1 text-2xl">🦌</span>
              <span>DeerFlow</span>
            </Link>
          </div>
          <div className="relative flex items-center gap-2">
            <LanguageSwitcher />
          </div>
        </div>
        <hr className="from-border/0 via-border/70 to-border-0 m-0 h-px w-full border-none bg-gradient-to-r" />
      </header>

      {/* Login Form */}
      <main className="flex flex-1 items-center justify-center">
        <div className="w-full max-w-md px-4">
          <div className="rounded-lg border bg-card p-8 shadow-sm">
            <div className="text-center mb-8">
              <h1 className="text-2xl font-semibold">Welcome Back</h1>
              <p className="text-sm text-muted-foreground mt-2">
                Sign in to continue to DeerFlow
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="username" className="text-sm font-medium">
                  Username
                </label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Enter your username (work_id)"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  disabled={isLoggingIn}
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium">
                  Password
                </label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={isLoggingIn}
                />
              </div>

              {error && (
                <p className="text-sm text-destructive">{error}</p>
              )}

              <Button
                type="submit"
                className="w-full"
                disabled={isLoggingIn}
              >
                {isLoggingIn ? "Signing in..." : "Sign In"}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm text-muted-foreground">
              <p>
                Use your database account to login
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="container py-6">
        <div className="flex flex-col items-center justify-center gap-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <span>&copy; 2025 DeerFlow</span>
            <span>•</span>
            <a
              href="https://github.com/bytedance/deer-flow"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1 hover:text-foreground transition-colors"
            >
              <GitHubLogoIcon className="size-3.5" />
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
