// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface User {
  id: string;
  username: string;
  email?: string;
  avatar?: string;
  edit_permission?: boolean;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

// FastAPI 后端地址
// 生产环境应该设置为实际的后端地址（不含 /api 前缀）
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/api$/, "");

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      user: null,
      isLoading: false,

      login: async (username: string, password: string) => {
        set({ isLoading: true });

        try {
          const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              work_id: username,
              password: password,
            }),
          });

          const data = await response.json();

          if (data.success && data.user) {
            set({
              isAuthenticated: true,
              user: {
                id: data.user.work_id,
                username: data.user.name || data.user.work_id,
                email: data.user.email,
                edit_permission: data.user.edit_permission,
              },
            });
            return true;
          }

          return false;
        } catch (error) {
          console.error("Login error:", error);
          return false;
        } finally {
          set({ isLoading: false });
        }
      },

      logout: async () => {
        try {
          await fetch(`${API_BASE_URL}/api/auth/logout`, {
            method: "POST",
          });
        } catch (error) {
          console.error("Logout error:", error);
        } finally {
          set({
            isAuthenticated: false,
            user: null,
          });
        }
      },

      checkAuth: async () => {
        // 当前使用 zustand persist，登录状态保存在 localStorage
        // 如果需要更严格的验证，可以调用 /api/auth/me 接口
        // 由于没有使用 JWT，当前只需要检查 localStorage 中的状态
      },
      // checkAuth: async () => {
      //   set({
      //     isAuthenticated: true,
      //     user: { id: "admin", username: "Admin", edit_permission: true },
      //   });
      // },

    }),
    {
      name: "deer-flow-auth",
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        user: state.user,
      }),
    },
  ),
);

