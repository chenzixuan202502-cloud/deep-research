// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { nanoid } from "nanoid";
import { toast } from "sonner";
import { create } from "zustand";
import { useShallow } from "zustand/react/shallow";

import { chatStream, generatePodcast, mapLocaleToBackend, callNormalAnswerStream } from "../api";
import type { Message, Resource } from "../messages";
import { mergeMessage } from "../messages";
import { parseJSON } from "../utils";

import { getChatStreamSettings, setEnableWebSearch, useSettingsStore } from "./settings-store";

const THREAD_ID = nanoid();

export interface HistoryDetailMessage {
  question_seq: string;
  question: string;
  answer?: string | null;
}

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
).replace(/\/api$/, "");

export const useStore = create<{
  responding: boolean;
  threadId: string | undefined;
  messageIds: string[];
  messages: Map<string, Message>;
  researchIds: string[];
  researchPlanIds: Map<string, string>;
  researchReportIds: Map<string, string>;
  researchActivityIds: Map<string, string[]>;
  ongoingResearchId: string | null;
  openResearchId: string | null;

  // 当前会话的 chat_seq（新对话时从后端获取）
  chatSeq: number | null;

  // 历史模式
  historyMode: boolean;
  historyChatSeq: string | null;
  historyDetailMessages: HistoryDetailMessage[];

  appendMessage: (message: Message) => void;
  updateMessage: (message: Message) => void;
  updateMessages: (messages: Message[]) => void;
  openResearch: (researchId: string | null) => void;
  closeResearch: () => void;
  setOngoingResearch: (researchId: string | null) => void;
  loadHistoryMessages: (chatSeq: string, messages: HistoryDetailMessage[]) => void;
  exitHistoryMode: () => void;
  clearMessages: () => void;
  createNewChat: (userId: string) => Promise<number | null>;
}>((set, get) => ({
  responding: false,
  threadId: THREAD_ID,
  messageIds: [],
  messages: new Map<string, Message>(),
  researchIds: [],
  researchPlanIds: new Map<string, string>(),
  researchReportIds: new Map<string, string>(),
  researchActivityIds: new Map<string, string[]>(),
  ongoingResearchId: null,
  openResearchId: null,

  chatSeq: null,

  historyMode: false,
  historyChatSeq: null,
  historyDetailMessages: [],

  appendMessage(message: Message) {
    set((state) => {
      // Prevent duplicate message IDs in the array to avoid React key warnings
      const newMessageIds = state.messageIds.includes(message.id)
        ? state.messageIds
        : [...state.messageIds, message.id];
      return {
        messageIds: newMessageIds,
        messages: new Map(state.messages).set(message.id, message),
      };
    });
  },
  updateMessage(message: Message) {
    set((state) => ({
      messages: new Map(state.messages).set(message.id, message),
    }));
  },
  updateMessages(messages: Message[]) {
    set((state) => {
      const newMessages = new Map(state.messages);
      messages.forEach((m) =>newMessages.set(m.id,m));
      return { messages: newMessages };

    });
  },
  openResearch(researchId: string | null) {
    set({ openResearchId: researchId });
  },
  closeResearch() {
    set({ openResearchId: null });
  },
  setOngoingResearch(researchId: string | null) {
    set({ ongoingResearchId: researchId });
  },
  loadHistoryMessages(chatSeq: string, messages: HistoryDetailMessage[]) {
    set({ historyMode: true, historyChatSeq: chatSeq, historyDetailMessages: messages });
  },
  exitHistoryMode() {
    set({ historyMode: false, historyChatSeq: null, historyDetailMessages: [] });
  },
  clearMessages() {
    // 生成新的 threadId，确保后端认为是新会话
    const newThreadId = nanoid();
    set({
      messageIds: [],
      messages: new Map<string, Message>(),
      researchIds: [],
      researchPlanIds: new Map<string, string>(),
      researchReportIds: new Map<string, string>(),
      researchActivityIds: new Map<string, string[]>(),
      ongoingResearchId: null,
      openResearchId: null,
      responding: false,
      historyMode: false,
      historyChatSeq: null,
      historyDetailMessages: [],
      threadId: newThreadId,
      chatSeq: null,
    });
  },
  
  async createNewChat(userId: string) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/history/new?user_id=${encodeURIComponent(userId)}`,
        { method: "POST" }
      );
      const data = await response.json();
      if (data.success && data.chat_seq) {
        // 生成新的 threadId
        const newThreadId = nanoid();
        set({
          chatSeq: data.chat_seq,
          threadId: newThreadId,
          messageIds: [],
          messages: new Map<string, Message>(),
          historyMode: false,
          historyChatSeq: null,
          historyDetailMessages: [],
        });
        return data.chat_seq;
      }
      console.error("Failed to create new chat:", data.message);
      return null;
    } catch (err) {
      console.error("Error creating new chat:", err);
      return null;
    }
  },
}));

export async function sendMessage(
  content?: string,
  {
    interruptFeedback,
    resources,
    locale,
  }: {
    interruptFeedback?: string;
    resources?: Array<Resource>;
    locale?: string; // Accept locale from caller
  } = {},
  options: { abortSignal?: AbortSignal; chatSeq?: number | null } = {},
) {
  // 获取 user_id 和 chat_seq
  const { user } = await import("./auth-store").then(m => m.useAuthStore.getState());
  const state = useStore.getState();
  const passedChatSeq = options.chatSeq;

  // 优先使用 options 中传入的 chatSeq，其次根据历史模式判断；
  // 若仍为空且用户已登录，则自动创建一次新会话并持久化到 store，避免每次请求都被后端当成新对话。
  let chatSeq =
    passedChatSeq !== undefined && passedChatSeq !== null
      ? passedChatSeq
      : state.historyMode && state.historyChatSeq
        ? parseInt(state.historyChatSeq, 10)
        : state.chatSeq;

  if ((chatSeq === null || chatSeq === undefined) && user?.id) {
    chatSeq = await useStore.getState().createNewChat(user.id);
  }

  // threadId 也需要随新对话变化（clearMessages/createNewChat 会更新它）
  const threadId = useStore.getState().threadId ?? THREAD_ID;
        
  if (content != null) {
    appendMessage({
      id: nanoid(),
      threadId,
      role: "user",
      content: content,
      contentChunks: [content],
      resources,
    });
  }

  const settings = getChatStreamSettings();
  
  // Map frontend locale to backend format
  // If locale is not provided, fallback to "en-US"
  const backendLocale = locale ? mapLocaleToBackend(locale) : "zh-CN";

  const stream = chatStream(
    content ?? "[REPLAY]",
    {
      thread_id: threadId,
      locale: backendLocale, // Pass mapped locale
      user_id: user?.id,
      chat_seq: chatSeq ?? undefined,
      interrupt_feedback: interruptFeedback,
      resources,
      auto_accepted_plan: settings.autoAcceptedPlan,
      enable_clarification: settings.enableClarification ?? false,
      max_clarification_rounds: settings.maxClarificationRounds ?? 3,
      enable_deep_thinking: settings.enableDeepThinking ?? false,
      enable_background_investigation:
        settings.enableBackgroundInvestigation ?? true,
      max_plan_iterations: settings.maxPlanIterations,
      max_step_num: settings.maxStepNum,
      max_search_results: settings.maxSearchResults,
      search_provider: settings.searchProvider,
      report_style: settings.reportStyle,
      mcp_settings: settings.mcpSettings,
      answer_mode: settings.enableNormalAnswer ? "normal" : "deep_research",
    },
    options,
  );

  setResponding(true);
  let messageId: string | undefined;
  const pendingUpdates = new Map<string, Message>();
  let updateTimer: NodeJS.Timeout | undefined;

  const scheduleUpdate = () => {
    if (updateTimer) clearTimeout(updateTimer);
    updateTimer = setTimeout(() => {
      // Batch update message status
      if (pendingUpdates.size > 0) {
        useStore.getState().updateMessages(Array.from(pendingUpdates.values()));
        pendingUpdates.clear();
      }
    }, 16); // ~60fps
  };

  try {
    for await (const event of stream) {
      const { type, data } = event;
      let message: Message | undefined;
      
      // Handle tool_call_result specially: use the message that contains the tool call
      if (type === "tool_call_result") {
        message = findMessageByToolCallId(data.tool_call_id);
        if (message) {
          // Use the found message's ID, not data.id
          messageId = message.id;
        } else {
          // Shouldn't happen, but handle gracefully
          if (process.env.NODE_ENV === "development") {
            console.warn(`Tool call result without matching message: ${data.tool_call_id}`);
          }
          continue; // Skip this event
        }
      } else {
        // For other event types, use data.id
        messageId = data.id;
        
        if (!existsMessage(messageId)) {
          message = {
            id: messageId,
            threadId: data.thread_id,
            agent: data.agent,
            role: data.role,
            content: "",
            contentChunks: [],
            reasoningContent: "",
            reasoningContentChunks: [],
            isStreaming: true,
            interruptFeedback,
          };
          appendMessage(message);
        }
      }
      
      message ??= getMessage(messageId);
      if (message) {
        message = mergeMessage(message, event);
        // Collect pending messages for update, instead of updating immediately.
        pendingUpdates.set(message.id, message);
        scheduleUpdate();
      }
    }
  } catch {
    toast("An error occurred while generating the response. Please try again.");
    // Update message status.
    // TODO: const isAborted = (error as Error).name === "AbortError";
    if (messageId != null) {
      const message = getMessage(messageId);
      if (message?.isStreaming) {
        message.isStreaming = false;
        useStore.getState().updateMessage(message);
      }
    }
    useStore.getState().setOngoingResearch(null);
  } finally {
    setResponding(false);
    // Ensure all pending updates are processed.
    if (updateTimer) clearTimeout(updateTimer);
    if (pendingUpdates.size > 0) {
      useStore.getState().updateMessages(Array.from(pendingUpdates.values()));
    }
    
  }
}

function setResponding(value: boolean) {
  useStore.setState({ responding: value });
}

function existsMessage(id: string) {
  return useStore.getState().messageIds.includes(id);
}

function getMessage(id: string) {
  return useStore.getState().messages.get(id);
}

function findMessageByToolCallId(toolCallId: string) {
  return Array.from(useStore.getState().messages.values())
    .reverse()
    .find((message) => {
      if (message.toolCalls) {
        return message.toolCalls.some((toolCall) => toolCall.id === toolCallId);
      }
      return false;
    });
}

function appendMessage(message: Message) {
  if (
    message.agent === "coder" ||
    message.agent === "reporter" ||
    message.agent === "researcher"
  ) {
    if (!getOngoingResearchId()) {
      const id = message.id;
      appendResearch(id);
      openResearch(id);
    }
    appendResearchActivity(message);
  }
  useStore.getState().appendMessage(message);
}

function updateMessage(message: Message) {
  if (
    getOngoingResearchId() &&
    message.agent === "reporter" &&
    !message.isStreaming
  ) {
    useStore.getState().setOngoingResearch(null);
  }
  useStore.getState().updateMessage(message);
}

function getOngoingResearchId() {
  return useStore.getState().ongoingResearchId;
}

function appendResearch(researchId: string) {
  let planMessage: Message | undefined;
  const reversedMessageIds = [...useStore.getState().messageIds].reverse();
  for (const messageId of reversedMessageIds) {
    const message = getMessage(messageId);
    if (message?.agent === "planner") {
      planMessage = message;
      break;
    }
  }
  const messageIds = [researchId];
  messageIds.unshift(planMessage!.id);
  useStore.setState({
    ongoingResearchId: researchId,
    researchIds: [...useStore.getState().researchIds, researchId],
    researchPlanIds: new Map(useStore.getState().researchPlanIds).set(
      researchId,
      planMessage!.id,
    ),
    researchActivityIds: new Map(useStore.getState().researchActivityIds).set(
      researchId,
      messageIds,
    ),
  });
}

function appendResearchActivity(message: Message) {
  const researchId = getOngoingResearchId();
  if (researchId) {
    const researchActivityIds = useStore.getState().researchActivityIds;
    const current = researchActivityIds.get(researchId)!;
    if (!current.includes(message.id)) {
      useStore.setState({
        researchActivityIds: new Map(researchActivityIds).set(researchId, [
          ...current,
          message.id,
        ]),
      });
    }
    if (message.agent === "reporter") {
      useStore.setState({
        researchReportIds: new Map(useStore.getState().researchReportIds).set(
          researchId,
          message.id,
        ),
      });
    }
  }
}

export function openResearch(researchId: string | null) {
  useStore.getState().openResearch(researchId);
}

export function closeResearch() {
  useStore.getState().closeResearch();
}

export async function listenToPodcast(researchId: string) {
  const planMessageId = useStore.getState().researchPlanIds.get(researchId);
  const reportMessageId = useStore.getState().researchReportIds.get(researchId);
  if (planMessageId && reportMessageId) {
    const planMessage = getMessage(planMessageId)!;
    const title = parseJSON(planMessage.content, { title: "Untitled" }).title;
    const reportMessage = getMessage(reportMessageId);
    if (reportMessage?.content) {
      appendMessage({
        id: nanoid(),
        threadId: THREAD_ID,
        role: "user",
        content: "Please generate a podcast for the above research.",
        contentChunks: [],
      });
      const podCastMessageId = nanoid();
      const podcastObject = { title, researchId };
      const podcastMessage: Message = {
        id: podCastMessageId,
        threadId: THREAD_ID,
        role: "assistant",
        agent: "podcast",
        content: JSON.stringify(podcastObject),
        contentChunks: [],
        reasoningContent: "",
        reasoningContentChunks: [],
        isStreaming: true,
      };
      appendMessage(podcastMessage);
      // Generating podcast...
      let audioUrl: string | undefined;
      try {
        audioUrl = await generatePodcast(reportMessage.content);
      } catch (e) {
        console.error(e);
        useStore.setState((state) => ({
          messages: new Map(useStore.getState().messages).set(
            podCastMessageId,
            {
              ...state.messages.get(podCastMessageId)!,
              content: JSON.stringify({
                ...podcastObject,
                error: e instanceof Error ? e.message : "Unknown error",
              }),
              isStreaming: false,
            },
          ),
        }));
        toast("An error occurred while generating podcast. Please try again.");
        return;
      }
      useStore.setState((state) => ({
        messages: new Map(useStore.getState().messages).set(podCastMessageId, {
          ...state.messages.get(podCastMessageId)!,
          content: JSON.stringify({ ...podcastObject, audioUrl }),
          isStreaming: false,
        }),
      }));
    }
  }
}

export function useResearchMessage(researchId: string) {
  return useStore(
    useShallow((state) => {
      const messageId = state.researchPlanIds.get(researchId);
      return messageId ? state.messages.get(messageId) : undefined;
    }),
  );
}

export function useMessage(messageId: string | null | undefined) {
  return useStore(
    useShallow((state) =>
      messageId ? state.messages.get(messageId) : undefined,
    ),
  );
}

export function useMessageIds() {
  return useStore(useShallow((state) => state.messageIds));
}

export function useRenderableMessageIds() {
  return useStore(
    useShallow((state) => {
      // Filter to only messages that will actually render in MessageListView
      // This prevents duplicate keys and React warnings when messages change state
      return state.messageIds.filter((messageId) => {
        const message = state.messages.get(messageId);
        if (!message) return false;
        
        // Only include messages that match MessageListItem rendering conditions
        // These are the same conditions checked in MessageListItem component
        return (
          message.role === "user" ||
          message.agent === "coordinator" ||
          message.agent === "planner" ||
          message.agent === "podcast" ||
          state.researchIds.includes(messageId) // startOfResearch condition
        );
      });
    }),
  );
}

export function useLastInterruptMessage() {
  return useStore(
    useShallow((state) => {
      if (state.messageIds.length >= 2) {
        const lastMessage = state.messages.get(
          state.messageIds[state.messageIds.length - 1]!,
        );
        return lastMessage?.finishReason === "interrupt" ? lastMessage : null;
      }
      return null;
    }),
  );
}

export function useLastFeedbackMessageId() {
  const waitingForFeedbackMessageId = useStore(
    useShallow((state) => {
      if (state.messageIds.length >= 2) {
        const lastMessage = state.messages.get(
          state.messageIds[state.messageIds.length - 1]!,
        );
        if (lastMessage && lastMessage.finishReason === "interrupt") {
          return state.messageIds[state.messageIds.length - 2];
        }
      }
      return null;
    }),
  );
  return waitingForFeedbackMessageId;
}

export function useToolCalls() {
  return useStore(
    useShallow((state) => {
      return state.messageIds
        ?.map((id) => getMessage(id)?.toolCalls)
        .filter((toolCalls) => toolCalls != null)
        .flat();
    }),
  );
}

// 历史模式辅助函数
export function loadHistoryMessages(
  chatSeq: string,
  messages: HistoryDetailMessage[],
) {
  useStore.getState().loadHistoryMessages(chatSeq, messages);
}

export function exitHistoryMode() {
  useStore.getState().exitHistoryMode();
}

export function useHistoryMode() {
  return useStore((state) => state.historyMode);
}

export function useHistoryDetailMessages() {
  return useStore(useShallow((state) => state.historyDetailMessages));
}

export function useChatSeq() {
  return useStore((state) => state.chatSeq);
}

export function clearMessages() {
  useStore.getState().clearMessages();
}

export function createNewChat(userId: string) {
  return useStore.getState().createNewChat(userId);
}

/**
 * 发送普通回答消息
 * 调用 /api/chat/stream 接口（answer_mode: "normal"）
 */
export async function sendNormalAnswerMessage(
  content?: string,
  options: { abortSignal?: AbortSignal; chatSeq?: number | null } = {},
) {
  if (!content || content.trim() === "") {
    return;
  }

  // 获取 user_id 和 chat_seq
  const { user } = await import("./auth-store").then(m => m.useAuthStore.getState());
  const state = useStore.getState();
  const passedChatSeq = options.chatSeq;

  // 优先使用 options 中传入的 chatSeq，其次根据历史模式判断；
  // 若仍为空且用户已登录，则自动创建一次新会话并持久化到 store，避免每次请求都被后端当成新对话。
  let chatSeq =
    passedChatSeq !== undefined && passedChatSeq !== null
      ? passedChatSeq
      : state.historyMode && state.historyChatSeq
        ? parseInt(state.historyChatSeq, 10)
        : state.chatSeq;

  if ((chatSeq === null || chatSeq === undefined) && user?.id) {
    chatSeq = await useStore.getState().createNewChat(user.id);
  }

  const threadId = useStore.getState().threadId;

  // 添加用户消息
  const messageId = nanoid();
  appendMessage({
    id: messageId,
    threadId: threadId ?? THREAD_ID,
    role: "user",
    content: content,
    contentChunks: [content],
  });

  // 添加 AI 消息占位
  const aiMessageId = nanoid();
  const aiMessage: Message = {
    id: aiMessageId,
    threadId: threadId ?? THREAD_ID,
    role: "assistant",
    agent: "coordinator", // 添加 agent 属性以便渲染
    content: "",
    contentChunks: [],
    reasoningContent: "",
    reasoningContentChunks: [],
    isStreaming: true,
  };
  appendMessage(aiMessage);

  setResponding(true);
  let fullContent = "";
  let chunkCount = 0;

  // 批量更新消息，参考深度检索的实现
  const pendingUpdates = new Map<string, Message>();
  let updateTimer: NodeJS.Timeout | undefined;
  let lastUpdateTime = 0;

  // 节流更新 ：每 100ms 最多更新一次，减少 React 重渲染频率
  const scheduleUpdate = () => {
    const now = Date.now();
    // 距离上次更新不足 100ms 时，只更新 pendingUpdates，不触发 React 重渲染
    if (now - lastUpdateTime < 100) {
      return;
    }
    lastUpdateTime = now;
    if (updateTimer) clearTimeout(updateTimer);
    updateTimer = setTimeout(() => {
      if (pendingUpdates.size > 0) {
        useStore.getState().updateMessages(Array.from(pendingUpdates.values()));
        pendingUpdates.clear();
      }
    }, 100);
  };

  try {
    // 获取联网检索状态
    const webSearch = useSettingsStore.getState().general.enableWebSearch;

    // 调用流式 API
    const stream = callNormalAnswerStream(content, {
      user_id: user?.id,
      chat_seq: chatSeq ?? undefined,
      enable_web_search: webSearch,
    });

    for await (const event of stream) {
      if (options.abortSignal?.aborted) {
        break;
      }

      if (event.status === "streaming" && event.chunk) {
        chunkCount++;
        fullContent += event.chunk;
        // 修复：使用新对象而不是直接修改，确保 React 检测到变化
        const existingMessage = getMessage(aiMessageId);
        if (existingMessage) {
          const updatedMessage: Message = {
            ...existingMessage,
            content: fullContent,
            contentChunks: [fullContent],
            isStreaming: true,
          };
          pendingUpdates.set(updatedMessage.id, updatedMessage);
          scheduleUpdate();
        }
      } else if (event.status === "completed") {
        fullContent = event.full_content || fullContent;
        // 修复：使用新对象而不是直接修改
        const existingMessage = getMessage(aiMessageId);
        if (existingMessage) {
          const updatedMessage: Message = {
            ...existingMessage,
            content: fullContent,
            contentChunks: [fullContent],
            isStreaming: false,
          };
          pendingUpdates.set(updatedMessage.id, updatedMessage);
          scheduleUpdate();
        }
      } else if (event.status === "error") {
        toast(event.error || "普通回答生成出错，请重试");
        const existingMessage = getMessage(aiMessageId);
        if (existingMessage) {
          const updatedMessage: Message = {
            ...existingMessage,
            content: `错误: ${event.error}`,
            isStreaming: false,
          };
          pendingUpdates.set(updatedMessage.id, updatedMessage);
          scheduleUpdate();
        }
      }
    }
  } catch (error) {
    console.error("Error in sendNormalAnswerMessage:", error);
    toast("普通回答生成出错，请重试");
    const existingMessage = getMessage(aiMessageId);
    if (existingMessage) {
      // 修复：使用新对象而不是直接修改
      const updatedMessage: Message = {
        ...existingMessage,
        content: "生成回答时出错，请重试",
        isStreaming: false,
      };
      useStore.getState().updateMessage(updatedMessage);
    }
  } finally {
    setResponding(false);
  }
}
