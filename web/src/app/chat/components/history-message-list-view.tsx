// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { motion } from "framer-motion";

import { Markdown } from "~/components/deer-flow/markdown";
import { cn } from "~/lib/utils";
import type { HistoryDetailMessage } from "~/core/store";

export function HistoryMessageListView({
  className,
  messages,
}: {
  className?: string;
  messages: HistoryDetailMessage[];
}) {
  return (
    <div
      className={cn(
        "min-h-0 flex-1 overflow-y-auto px-4",
        className,
      )}
    >
      <ul className="flex flex-col pb-8">
        {messages.map((msg, index) => (
          <motion.li
            key={msg.question_seq}
            className="mt-10 flex flex-col gap-4"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, ease: "easeOut", delay: index * 0.04 }}
          >
            {/* 用户问题气泡 */}
            {msg.question && (
              <div className="flex w-full justify-end">
                <div
                  className="bg-brand rounded-2xl rounded-ee-none px-4 py-3 break-words"
                  style={{ maxWidth: "90%", wordBreak: "break-all" }}
                >
                  <Markdown className="prose-invert not-dark:text-secondary dark:text-inherit">
                    {msg.question}
                  </Markdown>
                </div>
              </div>
            )}

            {/* AI 回复气泡 */}
            {msg.answer && (
              <div className="flex w-full justify-start">
                <div
                  className="bg-card rounded-2xl rounded-es-none px-4 py-3 break-words"
                  style={{ maxWidth: "90%", wordBreak: "break-all" }}
                >
                  <Markdown>{msg.answer}</Markdown>
                </div>
              </div>
            )}
          </motion.li>
        ))}
        <div className="h-8 w-full shrink-0" />
      </ul>
    </div>
  );
}
