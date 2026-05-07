// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { motion } from "framer-motion";
import { FastForward, Play } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { useCallback, useRef, useState } from "react";
import { nanoid } from "nanoid";

import { RainbowText } from "~/components/deer-flow/rainbow-text";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { fastForwardReplay } from "~/core/api";
import { useReplayMetadata } from "~/core/api/hooks";
import type { Option, Resource } from "~/core/messages";
import { useReplay } from "~/core/replay";
import { useSettingsStore } from "~/core/store";
import {
  exitHistoryMode,
  sendMessage,
  sendNormalAnswerMessage,
  useHistoryDetailMessages,
  useHistoryMode,
  useMessageIds,
  useStore,
} from "~/core/store";
import { env } from "~/env";
import { cn } from "~/lib/utils";

import { ConversationStarter } from "./conversation-starter";
import { HistoryMessageListView } from "./history-message-list-view";
import { InputBox } from "./input-box";
import { MessageListView } from "./message-list-view";
import { Welcome } from "./welcome";

export function MessagesBlock({ className }: { className?: string }) {
  const t = useTranslations("chat.messages");
  const locale = useLocale(); // Get current locale from next-intl
  const messageIds = useMessageIds();
  const messageCount = messageIds.length;
  const responding = useStore((state) => state.responding);
  const enableNormalAnswer = useSettingsStore((state) => state.general.enableNormalAnswer);
  const { isReplay } = useReplay();
  const { title: replayTitle, hasError: replayHasError } = useReplayMetadata();
  const [replayStarted, setReplayStarted] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const [feedback, setFeedback] = useState<{ option: Option } | null>(null);

  // 历史模式
  const historyMode = useHistoryMode();
  const historyDetailMessages = useHistoryDetailMessages();

  const handleSend = useCallback(
    async (
      message: string,
      options?: {
        interruptFeedback?: string;
        resources?: Array<Resource>;
      },
    ) => {
      // 如果在历史模式，先将历史消息转换为普通消息
      // 方案二：先保存 historyChatSeq，避免 exitHistoryMode 后状态丢失
      let preservedChatSeq: number | null = null;
      if (historyMode && historyDetailMessages.length > 0) {
        const state = useStore.getState();
        preservedChatSeq = state.historyChatSeq
          ? parseInt(state.historyChatSeq, 10)
          : state.chatSeq;
        const threadId = state.threadId;

        // 将历史消息逐个添加到普通消息列表
        for (const histMsg of historyDetailMessages) {
          // 添加用户问题
          if (histMsg.question) {
            state.appendMessage({
              id: nanoid(),
              threadId: threadId ?? "default",
              role: "user",
              content: histMsg.question,
              contentChunks: [histMsg.question],
            });
          }
          // 添加助手回答
          if (histMsg.answer) {
            state.appendMessage({
              id: nanoid(),
              threadId: threadId ?? "default",
              role: "assistant",
              agent: "coordinator",
              content: histMsg.answer,
              contentChunks: [histMsg.answer],
            });
          }
        }

        // 关键修复：立即退出历史模式，让界面切换到 MessageListView
        // 这样才能实时显示流式更新的消息
        exitHistoryMode();
      }

      const abortController = new AbortController();
      abortControllerRef.current = abortController;
      try {
        // 根据 enableNormalAnswer 状态选择发送方式
        if (enableNormalAnswer) {
          // 使用普通回答模式
          await sendNormalAnswerMessage(message, {
            abortSignal: abortController.signal,
            chatSeq: preservedChatSeq,
          });
        } else {
          // 使用正常的聊天流
          await sendMessage(
            message,
            {
              interruptFeedback:
                options?.interruptFeedback ?? feedback?.option.value,
              resources: options?.resources,
              locale,
            },
            {
              abortSignal: abortController.signal,
              chatSeq: preservedChatSeq,
            },
          );
        }
      } catch {}

      // 注意：历史模式已经在发送消息前退出了
    },
    [feedback, locale, historyMode, enableNormalAnswer],
  );
  const handleCancel = useCallback(() => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
  }, []);
  const handleFeedback = useCallback(
    (feedback: { option: Option }) => {
      setFeedback(feedback);
    },
    [setFeedback],
  );
  const handleRemoveFeedback = useCallback(() => {
    setFeedback(null);
  }, [setFeedback]);
  const handleStartReplay = useCallback(() => {
    setReplayStarted(true);
    void sendMessage(undefined, { locale });
  }, [setReplayStarted, locale]);
  const [fastForwarding, setFastForwarding] = useState(false);
  const handleFastForwardReplay = useCallback(() => {
    setFastForwarding(!fastForwarding);
    fastForwardReplay(!fastForwarding);
  }, [fastForwarding]);
  return (
    <div className={cn("flex h-full flex-col", className)}>
      {historyMode ? (
        <HistoryMessageListView
          className="flex-grow"
          messages={historyDetailMessages}
        />
      ) : responding || messageCount !== 0 || isReplay ? (
        <MessageListView
          className="flex flex-grow"
          onFeedback={handleFeedback}
          onSendMessage={handleSend}
        />
      ) : (
        <ConversationStarter onSend={handleSend} />
      )}
      {!isReplay ? (
        <div className="relative flex h-42 shrink-0 pb-4">
          <InputBox
            className="h-full w-full"
            responding={responding}
            feedback={feedback}
            onSend={handleSend}
            onCancel={handleCancel}
            onRemoveFeedback={handleRemoveFeedback}
          />
        </div>
      ) : (
        <>
          <div
            className={cn(
              "fixed bottom-[calc(50vh+80px)] left-0 transition-all duration-500 ease-out",
              replayStarted && "pointer-events-none scale-150 opacity-0",
            )}
          >
            <Welcome />
          </div>
          <motion.div
            className="mb-4 h-fit w-full items-center justify-center"
            initial={{ opacity: 0, y: "20vh" }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card
              className={cn(
                "w-full transition-all duration-300",
                !replayStarted && "translate-y-[-40vh]",
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex flex-grow items-center">
                  {responding && (
                    <motion.div
                      className="ml-3"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{ duration: 0.3 }}
                    >
                      <video
                        // Walking deer animation, designed by @liangzhaojun. Thank you for creating it!
                        src="/images/walking_deer.webm"
                        autoPlay
                        loop
                        muted
                        className="h-[42px] w-[42px] object-contain"
                      />
                    </motion.div>
                  )}
                  <CardHeader className={cn("flex-grow", responding && "pl-3")}>
                    <CardTitle>
                      <RainbowText animated={responding}>
                        {responding ? t("replaying") : `${replayTitle}`}
                      </RainbowText>
                    </CardTitle>
                    <CardDescription>
                      <RainbowText animated={responding}>
                        {responding
                          ? t("replayDescription")
                          : replayStarted
                            ? t("replayHasStopped")
                            : t("replayModeDescription")}
                      </RainbowText>
                    </CardDescription>
                  </CardHeader>
                </div>
                {!replayHasError && (
                  <div className="pr-4">
                    {responding && (
                      <Button
                        className={cn(fastForwarding && "animate-pulse")}
                        variant={fastForwarding ? "default" : "outline"}
                        onClick={handleFastForwardReplay}
                      >
                        <FastForward size={16} />
                        {t("fastForward")}
                      </Button>
                    )}
                    {!replayStarted && (
                      <Button className="w-24" onClick={handleStartReplay}>
                        <Play size={16} />
                        {t("play")}
                      </Button>
                    )}
                  </div>
                )}
              </div>
            </Card>
            {!replayStarted && env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY && (
              <div className="text-muted-foreground w-full text-center text-xs">
                {t("demoNotice")}{" "}
                <a
                  className="underline"
                  href="https://github.com/bytedance/deer-flow"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {t("clickHere")}
                </a>{" "}
                {t("cloneLocally")}
              </div>
            )}
          </motion.div>
        </>
      )}
    </div>
  );
}
