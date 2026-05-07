// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { env } from "~/env";

/**
 * Intelligently resolve the API service URL based on the current access context.
 * 
 * Priority Logic:
 * 0. SSR (Server-side): Use NEXT_PUBLIC_API_URL or fallback to http://localhost:8088/api
 * 1. Environment Variable Override: If NEXT_PUBLIC_API_URL is set in browser, use it
 * 2. Port-based Smart Detection:
 *    - Port 58032 (Public Network) -> http://{hostname}:58031/api
 *    - Port 3033 or others (Local/LAN) -> http://{hostname}:8088/api
 * 
 * Supported Scenarios:
 * - Public Network: http://IP:58032 -> API at http://IP:58031
 * - LAN/Internal: http://IP:3033 -> API at http://IP:8088
 * - Localhost Dev: http://localhost:3033 -> API at http://localhost:8088
 */
export function resolveServiceURL(path: string) {
  let BASE_URL: string;
  
  // Priority 0: SSR (Server-side rendering)
  if (typeof window === 'undefined') {
    BASE_URL = env.NEXT_PUBLIC_API_URL || "http://localhost:8088/api";
    console.log('[API] SSR mode, using:', BASE_URL);
  } else {
    // Priority 1: Environment Variable Override
    if (env.NEXT_PUBLIC_API_URL && env.NEXT_PUBLIC_API_URL.trim() !== '') {
      BASE_URL = env.NEXT_PUBLIC_API_URL;
      console.log('[API] Using environment variable override:', BASE_URL);
    } else {
      // Priority 2: Port-based Smart Detection
      const hostname = window.location.hostname;
      const port = window.location.port;
      
      if (port === '58032') {
        // Case A: Public Network Mapping
        BASE_URL = `http://${hostname}:58031/api`;
        console.log('[API] Detected public network (port 58032), using:', BASE_URL);
      } else {
        // Case B: Standard/Local (port 3033 or others)
        BASE_URL = `http://${hostname}:8088/api`;
        console.log('[API] Detected local/LAN access (port', port || 'default', '), using:', BASE_URL);
      }
    }
  }
  
  // Ensure BASE_URL ends with /
  if (!BASE_URL.endsWith("/")) {
    BASE_URL += "/";
  }
  
  // Remove leading slash from path if present
  const cleanPath = path.startsWith("/") ? path.slice(1) : path;
  
  return BASE_URL + cleanPath;
}
