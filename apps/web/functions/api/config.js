function jsonResponse(payload) {
  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: {
      "cache-control": "no-store",
      "content-type": "application/json; charset=utf-8",
    },
  });
}

export async function onRequestGet(context) {
  const siteKey =
    typeof context.env?.TURNSTILE_SITE_KEY === "string"
      ? context.env.TURNSTILE_SITE_KEY.trim()
      : "";

  return jsonResponse({
    turnstileSiteKey: siteKey,
  });
}
