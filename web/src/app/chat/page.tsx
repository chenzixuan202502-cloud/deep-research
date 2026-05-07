// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { GithubOutlined } from "@ant-design/icons";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { Suspense, useState } from "react";

import { Button } from "~/components/ui/button";

import { ThemeToggle } from "../../components/deer-flow/theme-toggle";
import { Tooltip } from "../../components/deer-flow/tooltip";
import { SettingsDialog } from "../settings/dialogs/settings-dialog";
import { HistorySidebar } from "./components/history-sidebar";

const Main = dynamic(() => import("./main"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center">
      Loading DeerFlow...
    </div>
  ),
});

export default function HomePage() {
  const t = useTranslations("chat.page");
  const [historyOpen, setHistoryOpen] = useState(true);

  return (
    <div className="flex h-screen w-screen overflow-hidden overscroll-none">
      <header className="fixed top-0 left-0 flex h-12 w-full items-center justify-between px-4 z-50">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setHistoryOpen(!historyOpen)}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </Button>
        </div>
        <div className="flex items-center">
          <Tooltip title={t("starOnGitHub")}>
            <Button variant="ghost" size="icon" asChild>
              <Link
                href="https://github.com/bytedance/deer-flow"
                target="_blank"
              >
                <GithubOutlined />
              </Link>
            </Button>
          </Tooltip>
          <ThemeToggle />
          <Suspense>
            <SettingsDialog />
          </Suspense>
        </div>
      </header>
      <HistorySidebar
        isOpen={historyOpen}
        onToggle={() => setHistoryOpen(!historyOpen)}
      />
      <div className="flex-1 pt-12">
        <Main />
      </div>
    </div>
  );
}
