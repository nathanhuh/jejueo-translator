export const INPUT_CHAR_LIMIT = 500;
export const SUPPORTED_LANGS = new Set(["ko", "ko-jeju"]);
export const TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify";

function now(runtime = {}) {
  if (typeof runtime.now === "function") {
    return runtime.now();
  }
  return Date.now();
}

function jsonResponse(payload, status = 200) {
  const requestId = payload && typeof payload.requestId === "string" ? payload.requestId : null;
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      ...(requestId ? { "x-request-id": requestId } : {}),
    },
  });
}

function errorResponse(status, error, message, requestId) {
  return jsonResponse(
    {
      error,
      message,
      requestId,
    },
    status,
  );
}

function fallbackRequestId(payload, requestId) {
  if (payload && typeof payload.requestId === "string" && payload.requestId.trim()) {
    return payload.requestId;
  }
  return requestId;
}

function buildRequestId(runtime = {}) {
  if (typeof runtime.randomUUID === "function") {
    return runtime.randomUUID();
  }
  return crypto.randomUUID();
}

function getLogger(runtime = {}) {
  return runtime.logger ?? console;
}

function logEvent(runtime, level, event) {
  const logger = getLogger(runtime);
  const logMethod =
    typeof logger[level] === "function"
      ? logger[level].bind(logger)
      : level === "warn" && typeof logger.warning === "function"
        ? logger.warning.bind(logger)
      : typeof logger.log === "function"
        ? logger.log.bind(logger)
        : null;

  if (!logMethod) {
    return;
  }

  logMethod(
    Object.fromEntries(
      Object.entries(event).filter(([, value]) => value !== undefined && value !== null),
    ),
  );
}

function normalizeBaseUrl(value) {
  if (typeof value !== "string") {
    return "";
  }
  return value.replace(/\/+$/, "");
}

async function parseJsonBody(request, requestId) {
  let payload;
  try {
    payload = await request.json();
  } catch {
    return {
      response: errorResponse(400, "invalid_input", "Malformed JSON request body", requestId),
    };
  }

  if (!payload || Array.isArray(payload) || typeof payload !== "object") {
    return {
      response: errorResponse(400, "invalid_input", "Request body must be a JSON object", requestId),
    };
  }

  return { payload };
}

function validatePayload(payload, requestId) {
  if (typeof payload.sourceText !== "string") {
    return errorResponse(400, "invalid_input", "Invalid request field: sourceText", requestId);
  }
  if (typeof payload.sourceLang !== "string") {
    return errorResponse(400, "invalid_input", "Invalid request field: sourceLang", requestId);
  }
  if (typeof payload.targetLang !== "string") {
    return errorResponse(400, "invalid_input", "Invalid request field: targetLang", requestId);
  }
  if (!payload.sourceText.trim()) {
    return errorResponse(400, "invalid_input", "Input text must not be empty", requestId);
  }
  if (!SUPPORTED_LANGS.has(payload.sourceLang) || !SUPPORTED_LANGS.has(payload.targetLang)) {
    return errorResponse(400, "invalid_input", "Unsupported language pair", requestId);
  }
  if (payload.sourceLang === payload.targetLang) {
    return errorResponse(400, "invalid_input", "Source and target languages must differ", requestId);
  }
  if (payload.sourceText.length > INPUT_CHAR_LIMIT) {
    return errorResponse(
      413,
      "input_too_long",
      `Input exceeds the v1 limit of ${INPUT_CHAR_LIMIT} characters`,
      requestId,
    );
  }
  return null;
}

function summarizePayload(payload) {
  const sourceLang = typeof payload?.sourceLang === "string" ? payload.sourceLang : null;
  const targetLang = typeof payload?.targetLang === "string" ? payload.targetLang : null;
  const sourceText = typeof payload?.sourceText === "string" ? payload.sourceText : null;
  return {
    direction:
      sourceLang && targetLang
        ? `${sourceLang}->${targetLang}`
        : undefined,
    charLength: sourceText === null ? undefined : sourceText.length,
  };
}

async function checkRateLimit(request, env, requestId, runtime = {}) {
  if (typeof runtime.checkRateLimit !== "function") {
    return null;
  }

  const allowed = await runtime.checkRateLimit({ request, env, requestId });
  if (allowed) {
    return null;
  }

  return errorResponse(429, "rate_limited", "Request rejected by abuse protection", requestId);
}

async function verifyTurnstile(request, env, runtime = {}) {
  if (!env?.TURNSTILE_SECRET_KEY) {
    return true;
  }

  const token = request.headers.get("cf-turnstile-response");
  if (!token) {
    return false;
  }

  const payload = {
    secret: env.TURNSTILE_SECRET_KEY,
    response: token,
  };
  const remoteIp = request.headers.get("cf-connecting-ip");
  if (remoteIp) {
    payload.remoteip = remoteIp;
  }

  const fetchImpl = runtime.fetchImpl ?? fetch;
  try {
    const response = await fetchImpl(TURNSTILE_VERIFY_URL, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      return false;
    }

    const result = await response.json();
    return result?.success === true;
  } catch {
    return false;
  }
}

function isTranslationPayload(payload) {
  return (
    payload &&
    typeof payload.translation === "string" &&
    typeof payload.model === "string" &&
    typeof payload.latencyMs === "number" &&
    typeof payload.requestId === "string"
  );
}

function isErrorPayload(payload) {
  return (
    payload &&
    typeof payload.error === "string" &&
    typeof payload.message === "string"
  );
}

async function normalizeUpstreamResponse(response, requestId) {
  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (response.ok) {
    if (isTranslationPayload(payload)) {
      return {
        response: jsonResponse(payload, 200),
        status: 200,
        responseRequestId: payload.requestId,
        inferenceLatencyMs: payload.latencyMs,
      };
    }
    return {
      response: errorResponse(503, "upstream_unavailable", "Translation service unavailable", requestId),
      status: 503,
      error: "upstream_unavailable",
      responseRequestId: requestId,
    };
  }

  if ((response.status === 400 || response.status === 413) && isErrorPayload(payload)) {
    const responseRequestId = fallbackRequestId(payload, requestId);
    return {
      response: jsonResponse(
        {
          ...payload,
          requestId: responseRequestId,
        },
        response.status,
      ),
      status: response.status,
      error: payload.error,
      responseRequestId,
    };
  }

  const responseRequestId = fallbackRequestId(payload, requestId);
  return {
    response: errorResponse(
      503,
      "upstream_unavailable",
      "Translation service unavailable",
      responseRequestId,
    ),
    status: 503,
    error: "upstream_unavailable",
    responseRequestId,
  };
}

async function forwardToInference(payload, env, requestId, runtime = {}, summary = {}, startedAt = now(runtime)) {
  const baseUrl = normalizeBaseUrl(env?.INFERENCE_BASE_URL);
  if (!baseUrl) {
    const response = errorResponse(503, "upstream_unavailable", "Translation service unavailable", requestId);
    logEvent(runtime, "warn", {
      event: "edge_translate",
      requestId,
      status: 503,
      error: "upstream_unavailable",
      edgeLatencyMs: Math.round(now(runtime) - startedAt),
      ...summary,
    });
    return response;
  }

  const fetchImpl = runtime.fetchImpl ?? fetch;
  const upstreamStartedAt = now(runtime);
  try {
    const upstreamResponse = await fetchImpl(`${baseUrl}/translate`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        accept: "application/json",
        "x-inference-auth": env?.INFERENCE_AUTH_TOKEN ?? "",
        "x-request-id": requestId,
      },
      body: JSON.stringify(payload),
    });
    const normalized = await normalizeUpstreamResponse(upstreamResponse, requestId);
    logEvent(runtime, normalized.status >= 500 ? "warn" : "info", {
      event: "edge_translate",
      requestId: normalized.responseRequestId ?? requestId,
      status: normalized.status,
      error: normalized.error,
      upstreamLatencyMs: Math.round(now(runtime) - upstreamStartedAt),
      inferenceLatencyMs: normalized.inferenceLatencyMs,
      edgeLatencyMs: Math.round(now(runtime) - startedAt),
      ...summary,
    });
    return normalized.response;
  } catch {
    const response = errorResponse(503, "upstream_unavailable", "Translation service unavailable", requestId);
    logEvent(runtime, "warn", {
      event: "edge_translate",
      requestId,
      status: 503,
      error: "upstream_unavailable",
      upstreamLatencyMs: Math.round(now(runtime) - upstreamStartedAt),
      edgeLatencyMs: Math.round(now(runtime) - startedAt),
      ...summary,
    });
    return response;
  }
}

export async function handleTranslateRequest(request, env = {}, runtime = {}) {
  const requestId = buildRequestId(runtime);
  const startedAt = now(runtime);

  const parsed = await parseJsonBody(request, requestId);
  if (parsed.response) {
    logEvent(runtime, "warn", {
      event: "edge_translate",
      requestId,
      status: parsed.response.status,
      error: "invalid_input",
      edgeLatencyMs: Math.round(now(runtime) - startedAt),
    });
    return parsed.response;
  }

  const summary = summarizePayload(parsed.payload);
  const validationError = validatePayload(parsed.payload, requestId);
  if (validationError) {
    logEvent(runtime, "warn", {
      event: "edge_translate",
      requestId,
      status: validationError.status,
      error: validationError.status === 413 ? "input_too_long" : "invalid_input",
      edgeLatencyMs: Math.round(now(runtime) - startedAt),
      ...summary,
    });
    return validationError;
  }

  const rateLimitError = await checkRateLimit(request, env, requestId, runtime);
  if (rateLimitError) {
    logEvent(runtime, "warn", {
      event: "edge_translate",
      requestId,
      status: 429,
      error: "rate_limited",
      edgeLatencyMs: Math.round(now(runtime) - startedAt),
      ...summary,
    });
    return rateLimitError;
  }

  const turnstileValid = await verifyTurnstile(request, env, runtime);
  if (!turnstileValid) {
    const response = errorResponse(429, "rate_limited", "Request rejected by abuse protection", requestId);
    logEvent(runtime, "warn", {
      event: "edge_translate",
      requestId,
      status: 429,
      error: "rate_limited",
      edgeLatencyMs: Math.round(now(runtime) - startedAt),
      ...summary,
    });
    return response;
  }

  return forwardToInference(parsed.payload, env, requestId, runtime, summary, startedAt);
}
