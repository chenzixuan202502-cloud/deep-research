// import { parse } from "best-effort-json-parser";
//
// /**
//  * Extract valid JSON from content that may have extra tokens.
//  * Finds the last closing brace/bracket that could be valid JSON.
//  */
// function extractValidJSON(content: string): string {
//   let braceCount = 0;
//   let bracketCount = 0;
//   let inString = false;
//   let escapeNext = false;
//   let lastValidEnd = -1;
//
//   for (let i = 0; i < content.length; i++) {
//     const char = content[i];
//
//     if (escapeNext) {
//       escapeNext = false;
//       continue;
//     }
//
//     if (char === "\\") {
//       escapeNext = true;
//       continue;
//     }
//
//     if (char === '"') {
//       inString = !inString;
//       continue;
//     }
//
//     if (inString) {
//       continue;
//     }
//
//     if (char === "{") {
//       braceCount++;
//     } else if (char === "}") {
//       if (braceCount > 0) {
//         braceCount--;
//         if (braceCount === 0) {
//           lastValidEnd = i;
//         }
//       }
//     } else if (char === "[") {
//       bracketCount++;
//     } else if (char === "]") {
//       if (bracketCount > 0) {
//         bracketCount--;
//         if (bracketCount === 0) {
//           lastValidEnd = i;
//         }
//       }
//     }
//   }
//
//   if (lastValidEnd > 0) {
//     return content.substring(0, lastValidEnd + 1);
//   }
//
//   return content;
// }
//
// export function parseJSON<T>(json: string | null | undefined, fallback: T) {
//   if (!json) {
//     return fallback;
//   }
//   try {
//     let raw = json
//       .trim()
//       .replace(/^```json\s*/, "")
//       .replace(/^```js\s*/, "")
//       .replace(/^```ts\s*/, "")
//       .replace(/^```plaintext\s*/, "")
//       .replace(/^```\s*/, "")
//       .replace(/\s*```$/, "");
//
//     // First attempt: try to extract valid JSON to remove extra tokens
//     if (raw.startsWith("{") || raw.startsWith("[")) {
//       raw = extractValidJSON(raw);
//     }
//
//     // Parse the cleaned content
//     // console.error("RAW JSON STRING >>>", raw)  /////////////////////////
//
//     return parse(raw) as T;
//   } catch {
//     // Fallback: try to extract meaningful content from malformed JSON
//     // This is a last-resort attempt to salvage partial data
//     return fallback;
//   }
// }
import { parse } from "best-effort-json-parser";

/**
 * Extract valid JSON from content that may have extra tokens.
 * Finds the last closing brace/bracket that could be valid JSON.
 */
function extractValidJSON(content: string): string {
  let braceCount = 0;
  let bracketCount = 0;
  let inString = false;
  let escapeNext = false;
  let lastValidEnd = -1;

  for (let i = 0; i < content.length; i++) {
    const char = content[i];

    if (escapeNext) {
      escapeNext = false;
      continue;
    }

    if (char === "\\") {
      escapeNext = true;
      continue;
    }

    if (char === '"') {
      inString = !inString;
      continue;
    }

    if (inString) {
      continue;
    }

    if (char === "{") {
      braceCount++;
    } else if (char === "}") {
      if (braceCount > 0) {
        braceCount--;
        if (braceCount === 0) {
          lastValidEnd = i;
        }
      }
    } else if (char === "[") {
      bracketCount++;
    } else if (char === "]") {
      if (bracketCount > 0) {
        bracketCount--;
        if (bracketCount === 0) {
          lastValidEnd = i;
        }
      }
    }
  }

  if (lastValidEnd > 0) {
    return content.substring(0, lastValidEnd + 1);
  }

  return content;
}

// 增强版：先判断是否为有效JSON，再解析，彻底避免非JSON触发警告
function isLikelyJSON(str: string): boolean {
  const trimmed = str.trim();
  // 只有以 { 或 [ 开头的，才可能是JSON
  return trimmed.startsWith("{") || trimmed.startsWith("[");
}

export function parseJSON<T>(json: string | null | undefined, fallback: T) {
  if (!json) {
    return fallback;
  }
  try {
    let raw = json
      .trim()
      .replace(/^```json\s*/, "")
      .replace(/^```js\s*/, "")
      .replace(/^```ts\s*/, "")
      .replace(/^```plaintext\s*/, "")
      .replace(/^```\s*/, "")
      .replace(/\s*```$/, "");

    // 🔴 核心修复1：如果不是JSON格式，直接返回兜底，不触发解析
    if (!isLikelyJSON(raw)) {
      console.warn("非JSON格式内容，直接返回兜底", raw.slice(0, 100));
      return fallback;
    }

    // First attempt: try to extract valid JSON to remove extra tokens
    if (raw.startsWith("{") || raw.startsWith("[")) {
      raw = extractValidJSON(raw);
    }

    // 🔴 核心修复2：用静默模式解析，关闭警告输出
    return parse(raw, {
      // 关闭所有解析警告，彻底消除 "parsed json with extra tokens" 报错
      onWarning: () => {}
    }) as T;
  } catch (e) {
    // Fallback: try to extract meaningful content from malformed JSON
    console.error("JSON解析失败，返回兜底", e);
    return fallback;
  }
}