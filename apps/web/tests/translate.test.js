import test from "node:test";
import assert from "node:assert/strict";

import { handleTranslateRequest, TURNSTILE_VERIFY_URL } from "../src/translate.js";

function makeRequest(body, headers = {}) {
  return new Request("https://example.com/api/translate", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      ...headers,
    },
    body,
  });
}

function runtime(overrides = {}) {
  return {
    logger: {
      info() {},
      warn() {},
      log() {},
    },
    ...overrides,
  };
}

test("valid requests are forwarded to inference with auth headers", async () => {
  let seenUrl = "";
  let seenOptions = null;

  const response = await handleTranslateRequest(
    makeRequest(
      JSON.stringify({
        sourceText: "안녕하세요",
        sourceLang: "ko",
        targetLang: "ko-jeju",
      }),
    ),
    {
      INFERENCE_BASE_URL: "https://inference.example.com/",
      INFERENCE_AUTH_TOKEN: "secret-token",
    },
    runtime({
      randomUUID: () => "edge-request-1",
      fetchImpl: async (url, options) => {
        seenUrl = url;
        seenOptions = options;
        return new Response(
          JSON.stringify({
            translation: "혼저 옵서",
            model: "alan-llm-jeju-dialect-v1-4b-q4km",
            latencyMs: 41,
            requestId: "upstream-1",
          }),
          {
            status: 200,
            headers: { "content-type": "application/json" },
          },
        );
      },
    }),
  );

  assert.equal(seenUrl, "https://inference.example.com/translate");
  assert.equal(seenOptions.headers["x-inference-auth"], "secret-token");
  assert.equal(seenOptions.headers["x-request-id"], "edge-request-1");
  assert.equal(response.headers.get("x-request-id"), "upstream-1");
  assert.deepEqual(await response.json(), {
    translation: "혼저 옵서",
    model: "alan-llm-jeju-dialect-v1-4b-q4km",
    latencyMs: 41,
    requestId: "upstream-1",
  });
});

test("same-language requests are rejected before inference", async () => {
  const response = await handleTranslateRequest(
    makeRequest(
      JSON.stringify({
        sourceText: "안녕하세요",
        sourceLang: "ko",
        targetLang: "ko",
      }),
    ),
    {},
    runtime({
      randomUUID: () => "edge-request-2",
    }),
  );

  assert.equal(response.status, 400);
  assert.equal(response.headers.get("x-request-id"), "edge-request-2");
  assert.deepEqual(await response.json(), {
    error: "invalid_input",
    message: "Source and target languages must differ",
    requestId: "edge-request-2",
  });
});

test("oversized requests return 413", async () => {
  const response = await handleTranslateRequest(
    makeRequest(
      JSON.stringify({
        sourceText: "가".repeat(501),
        sourceLang: "ko",
        targetLang: "ko-jeju",
      }),
    ),
    {},
    runtime({
      randomUUID: () => "edge-request-3",
    }),
  );

  assert.equal(response.status, 413);
  assert.equal(response.headers.get("x-request-id"), "edge-request-3");
  assert.deepEqual(await response.json(), {
    error: "input_too_long",
    message: "Input exceeds the v1 limit of 500 characters",
    requestId: "edge-request-3",
  });
});

test("turnstile failures map to the shared 429 response shape", async () => {
  const response = await handleTranslateRequest(
    makeRequest(
      JSON.stringify({
        sourceText: "안녕하세요",
        sourceLang: "ko",
        targetLang: "ko-jeju",
      }),
    ),
    {
      TURNSTILE_SECRET_KEY: "turnstile-secret",
    },
    runtime({
      randomUUID: () => "edge-request-4",
    }),
  );

  assert.equal(response.status, 429);
  assert.equal(response.headers.get("x-request-id"), "edge-request-4");
  assert.deepEqual(await response.json(), {
    error: "rate_limited",
    message: "Request rejected by abuse protection",
    requestId: "edge-request-4",
  });
});

test("turnstile verification calls the official siteverify endpoint", async () => {
  const calls = [];

  const response = await handleTranslateRequest(
    makeRequest(
      JSON.stringify({
        sourceText: "안녕하세요",
        sourceLang: "ko",
        targetLang: "ko-jeju",
      }),
      {
        "cf-turnstile-response": "token-123",
        "cf-connecting-ip": "127.0.0.1",
      },
    ),
    {
      TURNSTILE_SECRET_KEY: "turnstile-secret",
      INFERENCE_BASE_URL: "https://inference.example.com",
      INFERENCE_AUTH_TOKEN: "secret-token",
    },
    runtime({
      randomUUID: () => "edge-request-5",
      fetchImpl: async (url, options) => {
        calls.push({ url, options });
        if (url === TURNSTILE_VERIFY_URL) {
          return new Response(JSON.stringify({ success: true }), {
            status: 200,
            headers: { "content-type": "application/json" },
          });
        }

        return new Response(
          JSON.stringify({
            translation: "혼저 옵서",
            model: "alan-llm-jeju-dialect-v1-4b-q4km",
            latencyMs: 22,
            requestId: "upstream-5",
          }),
          {
            status: 200,
            headers: { "content-type": "application/json" },
          },
        );
      },
    }),
  );

  assert.equal(response.status, 200);
  assert.equal(calls[0].url, TURNSTILE_VERIFY_URL);
  assert.match(calls[0].options.body, /"remoteip":"127.0.0.1"/);
});

test("upstream failures are normalized to 503", async () => {
  const response = await handleTranslateRequest(
    makeRequest(
      JSON.stringify({
        sourceText: "안녕하세요",
        sourceLang: "ko",
        targetLang: "ko-jeju",
      }),
    ),
    {
      INFERENCE_BASE_URL: "https://inference.example.com",
      INFERENCE_AUTH_TOKEN: "secret-token",
    },
    runtime({
      randomUUID: () => "edge-request-6",
      fetchImpl: async () =>
        new Response(
          JSON.stringify({
            error: "unauthorized",
            message: "Missing or invalid upstream auth",
            requestId: "upstream-6",
          }),
          {
            status: 401,
            headers: { "content-type": "application/json" },
          },
        ),
    }),
  );

  assert.equal(response.status, 503);
  assert.equal(response.headers.get("x-request-id"), "upstream-6");
  assert.deepEqual(await response.json(), {
    error: "upstream_unavailable",
    message: "Translation service unavailable",
    requestId: "upstream-6",
  });
});

test("upstream fetch exceptions are normalized to 503", async () => {
  const response = await handleTranslateRequest(
    makeRequest(
      JSON.stringify({
        sourceText: "안녕하세요",
        sourceLang: "ko",
        targetLang: "ko-jeju",
      }),
    ),
    {
      INFERENCE_BASE_URL: "https://inference.example.com",
      INFERENCE_AUTH_TOKEN: "secret-token",
    },
    runtime({
      randomUUID: () => "edge-request-timeout",
      fetchImpl: async () => {
        throw new Error("timeout");
      },
    }),
  );

  assert.equal(response.status, 503);
  assert.equal(response.headers.get("x-request-id"), "edge-request-timeout");
  assert.deepEqual(await response.json(), {
    error: "upstream_unavailable",
    message: "Translation service unavailable",
    requestId: "edge-request-timeout",
  });
});

test("malformed json is rejected with a contract-aligned 400", async () => {
  const response = await handleTranslateRequest(
    makeRequest("{not-json"),
    {},
    runtime({
      randomUUID: () => "edge-request-7",
    }),
  );

  assert.equal(response.status, 400);
  assert.equal(response.headers.get("x-request-id"), "edge-request-7");
  assert.deepEqual(await response.json(), {
    error: "invalid_input",
    message: "Malformed JSON request body",
    requestId: "edge-request-7",
  });
});

test("rate-limit hook can reject requests before inference", async () => {
  const response = await handleTranslateRequest(
    makeRequest(
      JSON.stringify({
        sourceText: "안녕하세요",
        sourceLang: "ko",
        targetLang: "ko-jeju",
      }),
    ),
    {},
    runtime({
      randomUUID: () => "edge-request-8",
      checkRateLimit: async () => false,
    }),
  );

  assert.equal(response.status, 429);
  assert.equal(response.headers.get("x-request-id"), "edge-request-8");
  assert.deepEqual(await response.json(), {
    error: "rate_limited",
    message: "Request rejected by abuse protection",
    requestId: "edge-request-8",
  });
});

test("edge logging captures metadata without raw text", async () => {
  const events = [];

  await handleTranslateRequest(
    makeRequest(
      JSON.stringify({
        sourceText: "안녕하세요",
        sourceLang: "ko",
        targetLang: "ko-jeju",
      }),
    ),
    {
      INFERENCE_BASE_URL: "https://inference.example.com",
      INFERENCE_AUTH_TOKEN: "secret-token",
    },
    runtime({
      randomUUID: () => "edge-request-9",
      now: (() => {
        let current = 100;
        return () => {
          current += 5;
          return current;
        };
      })(),
      logger: {
        info(event) {
          events.push(event);
        },
      },
      fetchImpl: async () =>
        new Response(
          JSON.stringify({
            translation: "혼저 옵서",
            model: "alan-llm-jeju-dialect-v1-4b-q4km",
            latencyMs: 19,
            requestId: "edge-request-9",
          }),
          {
            status: 200,
            headers: { "content-type": "application/json" },
          },
        ),
    }),
  );

  assert.equal(events.length, 1);
  assert.equal(events[0].event, "edge_translate");
  assert.equal(events[0].requestId, "edge-request-9");
  assert.equal(events[0].status, 200);
  assert.equal(events[0].direction, "ko->ko-jeju");
  assert.equal(events[0].charLength, 5);
  assert.equal(events[0].upstreamLatencyMs, 5);
  assert.equal(events[0].inferenceLatencyMs, 19);
  assert.ok(events[0].edgeLatencyMs >= events[0].upstreamLatencyMs);
  assert.equal("sourceText" in events[0], false);
});
