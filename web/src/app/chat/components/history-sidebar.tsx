// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

import { Button } from "~/components/ui/button";
import { cn } from "~/lib/utils";
import { useAuthStore } from "~/core/store/auth-store";
import { clearMessages, createNewChat, loadHistoryMessages } from "~/core/store";

interface HistoryItem {
  chat_seq: string;
  question: string;
  time: string | null;
}

interface HistoryDetailMessage {
  question_seq: string;
  question: string;
  answer?: string | null;
}

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
).replace(/\/api$/, "");

export function HistorySidebar({
  className,
  isOpen = true,
  onToggle,
}: {
  className?: string;
  isOpen?: boolean;
  onToggle?: () => void;
}) {
  const t = useTranslations("chat.history");
  const { user } = useAuthStore();

  const [histories, setHistories] = useState<HistoryItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 加载历史列表
  useEffect(() => {
    if (!isOpen || !user?.id) return;

    const fetchHistory = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/history?user_id=${encodeURIComponent(user.id)}`,
        );
        const data = await response.json();
        if (data.success) {
          setHistories(data.items);
        } else {
          setError(data.message || "Failed to load history");
        }
      } catch (err) {
        console.error("Failed to fetch history:", err);
        setError("Failed to load history");
      } finally {
        setIsLoading(false);
      }
    };

    void fetchHistory();
  }, [isOpen, user?.id]);

  // 点击历史记录 - 加载对话详情
  const handleSelectHistory = async (chatSeq: string) => {
    if (selectedId === chatSeq) return;
    setSelectedId(chatSeq);
    setIsDetailLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/history/detail?chat_seq=${encodeURIComponent(chatSeq)}`,
      );
      const data = await response.json();
      if (data.success) {
        const messages: HistoryDetailMessage[] = data.messages;
        loadHistoryMessages(chatSeq, messages);
      } else {
        console.error("Failed to load history detail:", data.message);
      }
    } catch (err) {
      console.error("Failed to fetch history detail:", err);
    } finally {
      setIsDetailLoading(false);
    }
  };

  // 新建对话：调用 API 创建新会话，获取 chat_seq
  const handleNewChat = async () => {
    if (!user?.id) return;
    setSelectedId(null);
    // 调用后端 API 创建新会话，获取新的 chat_seq
    await createNewChat(user.id);
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div
      className={cn(
        "flex h-full w-64 shrink-0 flex-col border-r bg-card",
        className,
      )}
    >
      {/* 侧边栏标题 */}
      <div className="flex h-12 items-center justify-between border-b px-4">
        <h2 className="text-sm font-semibold">{t("title")}</h2>
        <Button variant="ghost" size="sm" onClick={onToggle}>
          {t("collapse")}
        </Button>
      </div>

      {/* 历史记录列表 */}
      <div className="min-h-0 flex-1 overflow-y-auto">
        <div className="flex flex-col gap-1 p-2">
          {isLoading && (
            <div className="flex items-center justify-center py-8">
              <span className="text-sm text-muted-foreground">
                {t("loading")}
              </span>
            </div>
          )}

          {!isLoading && error && (
            <div className="flex items-center justify-center py-8">
              <span className="text-sm text-destructive">{error}</span>
            </div>
          )}

          {!isLoading && !error && histories.length === 0 && (
            <div className="flex items-center justify-center py-8">
              <span className="text-sm text-muted-foreground">
                {t("empty")}
              </span>
            </div>
          )}

          {!isLoading &&
            !error &&
            histories.map((item) => (
              <button
                key={item.chat_seq}
                className={cn(
                  "flex flex-col items-start gap-1 rounded-lg p-3 text-left transition-colors hover:bg-accent",
                  selectedId === item.chat_seq && "bg-accent",
                  isDetailLoading &&
                    selectedId === item.chat_seq &&
                    "opacity-60",
                )}
                onClick={() => void handleSelectHistory(item.chat_seq)}
                disabled={isDetailLoading}
              >
                <span className="line-clamp-2 text-sm font-medium">
                  {item.question}
                </span>
                {item.time && (
                  <span className="text-xs text-muted-foreground">
                    {item.time}
                  </span>
                )}
              </button>
            ))}
        </div>
      </div>

      {/* 底部操作按钮 */}
      <div className="border-t p-2">
        <Button
          variant="outline"
          className="w-full"
          size="sm"
          onClick={handleNewChat}
        >
          {t("newChat")}
        </Button>
      </div>
    </div>
  );
}
