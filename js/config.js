
const customConfig = window.MINISEARCH_CONFIG || {};

const isBackendOrigin = window.location.port === "8000";

const defaultApiBaseUrl = isBackendOrigin
  ? window.location.origin
  : "https://minisearch-search-engine-backend-mini.onrender.com";

const configuredApiBaseUrl =
  customConfig.API_BASE_URL || defaultApiBaseUrl;

export const API_BASE_URL = String(configuredApiBaseUrl).replace(/\/+$/, "");

const configuredTimeout = Number(customConfig.API_TIMEOUT_MS);

export const API_TIMEOUT_MS =
  Number.isFinite(configuredTimeout) && configuredTimeout > 0
    ? configuredTimeout
    : 10000;
