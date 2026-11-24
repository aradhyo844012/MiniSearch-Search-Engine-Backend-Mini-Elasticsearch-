
/* =========================================
   MINISEARCH FRONTEND CONFIGURATION
========================================= */

/*
  Default backend:
  http://localhost:8000

  To use a different backend URL, set this
  before loading app.js in index.html:

  window.MINISEARCH_CONFIG = {
    API_BASE_URL: "https://your-backend-url.com",
    API_TIMEOUT_MS: 15000
  };
*/

const customConfig = window.MINISEARCH_CONFIG || {};

/* =========================================
   API BASE URL
========================================= */

const isBackendOrigin =
  window.location.port === "8000";

const defaultApiBaseUrl = isBackendOrigin
  ? window.location.origin
  : "http://localhost:8000";

const configuredApiBaseUrl =
  customConfig.API_BASE_URL || defaultApiBaseUrl;

export const API_BASE_URL =
  String(configuredApiBaseUrl).replace(/\/+$/, "");

/* =========================================
   API TIMEOUT
========================================= */

const configuredTimeout = Number(
  customConfig.API_TIMEOUT_MS
);

export const API_TIMEOUT_MS =
  Number.isFinite(configuredTimeout) &&
  configuredTimeout > 0
    ? configuredTimeout
    : 10000;
