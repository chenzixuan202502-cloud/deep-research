// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";

import { useAuthStore } from "~/core/store/auth-store";

// 不需要认证的公开路径
// const publicPaths = ["/login", "/"];
const publicPaths = ["/login", "/", "/chat"];
/**
 * AuthGuard - 认证保护组件
 * 用于保护需要登录才能访问的页面
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [isHydrated, setIsHydrated] = useState(false);

  // 等待 Zustand hydration 完成
  useEffect(() => {
    setIsHydrated(true);
  }, []);

  useEffect(() => {
    // 只有在 hydration 完成后再进行路由跳转判断
    if (!isHydrated) return;

    // 检查当前路径是否为公开路径
    const isPublicPath = publicPaths.some(
      (path) => pathname === path || pathname.startsWith(path + "/"),
    );

    if (!isAuthenticated && !isPublicPath) {
      // 未登录且访问非公开页面，跳转到登录页
      router.push("/login");
    } else if (isAuthenticated && pathname === "/login") {
      // 已登录且访问登录页，跳转到聊天页
      router.push("/chat");
    }
  }, [isHydrated, isAuthenticated, pathname, router]);

  // hydration 完成前不渲染，避免闪烁
  if (!isHydrated) {
    return null;
  }

  return <>{children}</>;
}


