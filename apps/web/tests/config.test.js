import test from "node:test";
import assert from "node:assert/strict";

import { onRequestGet } from "../functions/api/config.js";

test("config endpoint returns the configured Turnstile site key", async () => {
  const response = await onRequestGet({
    env: {
      TURNSTILE_SITE_KEY: "site-key-123",
    },
  });

  assert.equal(response.status, 200);
  assert.equal(response.headers.get("cache-control"), "no-store");
  assert.deepEqual(await response.json(), {
    turnstileSiteKey: "site-key-123",
  });
});

test("config endpoint normalizes an unset Turnstile site key", async () => {
  const response = await onRequestGet({
    env: {},
  });

  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), {
    turnstileSiteKey: "",
  });
});
