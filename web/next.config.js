/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially useful
 * for Docker builds.
 */
// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import "./src/env.js";
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./src/i18n.ts');

/** @type {import("next").NextConfig} */

const config = {
  // 1. 跳过构建时的 ESLint 检查
  eslint: {
    ignoreDuringBuilds: true,
  },

  // 2. 💡 关键修改：禁用字体优化，防止在无法联网时请求 Google Fonts 导致超时
  optimizeFonts: false,

  // For development mode
  turbopack: {
    rules: {
      "*.md": {
        loaders: ["raw-loader"],
        as: "*.js",
      },
    },
  },

  // For production mode
  webpack: (config) => {
    config.module.rules.push({
      test: /\.md$/,
      use: "raw-loader",
    });
    return config;
  },

  // 输出模式
  output: "standalone",
};

export default withNextIntl(config);