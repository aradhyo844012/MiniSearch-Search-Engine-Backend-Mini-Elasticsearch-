
import { API_BASE_URL, API_TIMEOUT_MS } from "./config.js";

/* =========================================
   API ERROR
========================================= */

export class ApiError extends Error {
  constructor(
    message,
    status = null,
    code = "UNKNOWN_ERROR"
  ) {
    super(message);

    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

/* =========================================
   RESPONSE VALIDATION
========================================= */

function validateObject(data, requestName) {
  if (
    data === null ||
    typeof data !== "object" ||
    Array.isArray(data)
  ) {
    throw new ApiError(
      `Invalid response received from ${requestName}.`,
      null,
      "INVALID_RESPONSE"
    );
  }

  return data;
}

function validateSearchResponse(data) {
  validateObject(data, "search API");

  if (!Array.isArray(data.results)) {
    throw new ApiError(
      "The search API returned an invalid results format.",
      null,
      "INVALID_SEARCH_RESPONSE"
    );
  }

  if (
    typeof data.totalHits !== "number" ||
    !Number.isFinite(data.totalHits) ||
    data.totalHits < 0
  ) {
    throw new ApiError(
      "The search API returned an invalid result count.",
      null,
      "INVALID_SEARCH_RESPONSE"
    );
  }

  return data;
}

/* =========================================
   ERROR MESSAGE HANDLING
========================================= */

function getBackendErrorMessage(payload, status) {
  const backendMessage = payload?.error?.message;

  if (
    typeof backendMessage === "string" &&
    backendMessage.trim()
  ) {
    return backendMessage;
  }

  switch (status) {
    case 400:
      return "The request was invalid. Please check your input.";

    case 401:
      return "You are not authorized to access this resource.";

    case 403:
      return "Access to this resource is forbidden.";

    case 404:
      return "The requested resource could not be found.";

    case 429:
      return "Too many requests. Please try again shortly.";

    case 500:
      return "The backend encountered an internal error.";

    case 502:
    case 503:
    case 504:
      return "The backend is temporarily unavailable.";

    default:
      return `Request failed with status ${status}.`;
  }
}

/* =========================================
   COMMON API REQUEST HANDLER
========================================= */

async function request(path) {
  const controller = new AbortController();

  const timeout = setTimeout(() => {
    controller.abort();
  }, API_TIMEOUT_MS);

  try {
    const response = await fetch(
      `${API_BASE_URL}${path}`,
      {
        method: "GET",
        headers: {
          Accept: "application/json"
        },
        signal: controller.signal
      }
    );

    let payload = null;

    try {
      payload = await response.json();
    } catch {
      if (response.ok) {
        throw new ApiError(
          "The backend returned an invalid JSON response.",
          response.status,
          "INVALID_JSON"
        );
      }
    }

    if (!response.ok) {
      throw new ApiError(
        getBackendErrorMessage(payload, response.status),
        response.status,
        payload?.error?.code || "HTTP_ERROR"
      );
    }

    return payload;

  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error.name === "AbortError") {
      throw new ApiError(
        "The API request timed out. Please check whether the backend is running.",
        null,
        "TIMEOUT"
      );
    }

    throw new ApiError(
      "Could not connect to the MiniSearch API. Check your backend connection.",
      null,
      "NETWORK_ERROR"
    );

  } finally {
    clearTimeout(timeout);
  }
}

/* =========================================
   INPUT VALIDATION
========================================= */

function validateSearchInput({
  query,
  mode,
  limit,
  offset
}) {
  if (typeof query !== "string" || !query.trim()) {
    throw new ApiError(
      "Please enter a search query.",
      null,
      "INVALID_QUERY"
    );
  }

  if (!["OR", "AND"].includes(mode)) {
    throw new ApiError(
      "Invalid search mode. Use OR or AND.",
      null,
      "INVALID_MODE"
    );
  }

  if (!Number.isInteger(limit) || limit < 1) {
    throw new ApiError(
      "Search limit must be a positive integer.",
      null,
      "INVALID_LIMIT"
    );
  }

  if (!Number.isInteger(offset) || offset < 0) {
    throw new ApiError(
      "Search offset cannot be negative.",
      null,
      "INVALID_OFFSET"
    );
  }
}

/* =========================================
   SEARCH DOCUMENTS
========================================= */

export async function searchDocuments({
  query,
  mode = "OR",
  limit = 10,
  offset = 0
}) {
  validateSearchInput({
    query,
    mode,
    limit,
    offset
  });

  const params = new URLSearchParams({
    query: query.trim(),
    mode,
    k: String(limit),
    offset: String(offset)
  });

  const response = await request(
    `/search?${params.toString()}`
  );

  return validateSearchResponse(response);
}

/* =========================================
   GET INDEX STATISTICS
========================================= */

export async function getStats() {
  const response = await request("/stats");

  return validateObject(response, "stats API");
}

/* =========================================
   GET DOCUMENT BY ID
========================================= */

export async function getDocument(id) {
  if (
    id === null ||
    id === undefined ||
    String(id).trim() === ""
  ) {
    throw new ApiError(
      "A valid document ID is required.",
      null,
      "INVALID_DOCUMENT_ID"
    );
  }

  const safeId = encodeURIComponent(String(id));

  const response = await request(`/doc/${safeId}`);

  return validateObject(response, "document API");
}

/* =========================================
   EXPORTS
========================================= */

export { API_BASE_URL };
