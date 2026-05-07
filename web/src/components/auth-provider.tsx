// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";

import { useAuthStore } from "~/core/store/auth-store";

// 不需要认证的公开路径
const publicPaths = ["/login", "/"];

/**
 * AuthProvider - 认证状态提供者
 * 处理全局认证状态和路由保护
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  useEffect(() => {
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
  }, [isAuthenticated, pathname, router]);

  return <>{children}</>;
}
