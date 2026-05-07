// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { resolveServiceURL } from "./resolve-service-url";

/**
 * 调用普通回答接口（非流式）
 * 后端调用 /api/chat/stream 接口 (answer_mode: "normal")
 */
export async function callNormalAnswer(
  message: string,
  options: {
    model?: string;
    user_id?: string;
    chat_seq?: number;
  } = {},
): Promise<{
  status: number;
  msg: string;
  answer?: string;
}> {
  const { model = "Qwen3-30B-abliterated", user_id, chat_seq } = options;

  const response = await fetch(resolveServiceURL("chat/stream"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      messages: [{ role: "user", content: message }],
      model,
      answer_mode: "normal",
      user_id,
      chat_seq,
    }),
  });

  return response.json();
}

/**
 * 调用普通回答接口（流式）
 * 后端调用 /api/chat/stream 接口 (answer_mode: "normal")
 */
export async function* callNormalAnswerStream(
  message: string,
  options: {
    model?: string;
    user_id?: string;
    chat_seq?: number;
    enable_web_search?: boolean;
  } = {},
): AsyncGenerator<{
  chunk?: string;
  full_content?: string;
  status?: string;
  chunk_count?: number;
  elapsed_time?: number;
  error?: string;
  total_chunks?: number;
  total_time?: number;
}> {
  const { model = "Qwen3-30B-abliterated", user_id, chat_seq, enable_web_search } = options;

  const response = await fetch(resolveServiceURL("chat/stream"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      messages: [{ role: "user", content: message }],
      model,
      answer_mode: "normal",
      user_id,
      chat_seq,
      enable_web_search: enable_web_search ?? false,
    }),
  });

  if (!response.ok) {
    yield {
      status: "error",
      error: `Request failed: ${response.statusText}`,
    };
    return;
  }

  if (!response.body) {
    yield {
      status: "error",
      error: "No response body",
    };
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        try {
          yield JSON.parse(data);
        } catch (e) {
          console.error("Failed to parse SSE data:", e);
        }
      }
    }
  }
}
