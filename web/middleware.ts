// import { NextResponse } from "next/server";
// import type { NextRequest } from "next/server";

// // 支持的语言
// const SUPPORTED_LOCALES = ["zh", "en"];
// const DEFAULT_LOCALE = "zh";

// /**
//  * Middleware: 处理 locale
//  * - 首次访问无 cookie → 设置默认中文
//  * - 已存在 cookie → 保持原值
//  * - 支持切换语言
//  */
// export function middleware(request: NextRequest) {
//   const response = NextResponse.next();

//   // 读取 NEXT_LOCALE cookie
//   const localeCookie = request.cookies.get("NEXT_LOCALE")?.value;

//   // 如果 cookie 不存在或非法 → 设置默认语言
//   if (!localeCookie || !SUPPORTED_LOCALES.includes(localeCookie)) {
//     response.cookies.set("NEXT_LOCALE", DEFAULT_LOCALE, {
//       path: "/",
//       sameSite: "lax",
//     });
//   }

//   return response;
// }

// // 配置 middleware 生效的路径
// export const config = {
//   matcher: [
//     // 匹配所有页面，但排除 _next 静态资源和 API
//     "/((?!_next|api|favicon.ico).*)",
//   ],
// };
