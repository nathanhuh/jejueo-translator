const form = document.querySelector("#translator-form");
const sourceLang = document.querySelector("#source-lang");
const targetLang = document.querySelector("#target-lang");
const sourceText = document.querySelector("#source-text");
const submitButton = document.querySelector("#submit-button");
const swapButton = document.querySelector("#swap-button");
const clearButton = document.querySelector("#clear-button");
const copyButton = document.querySelector("#copy-button");
const charCount = document.querySelector("#char-count");
const resultOutput = document.querySelector("#result-output");
const resultNote = document.querySelector("#result-note");
const errorText = document.querySelector("#error-text");
const statusText = document.querySelector("#status-text");
const exampleButtons = document.querySelectorAll(".example-button");
const turnstileBlock = document.querySelector("#turnstile-block");
const turnstileWidget = document.querySelector("#turnstile-widget");
const turnstileNote = document.querySelector("#turnstile-note");

const EMPTY_RESULT = "Translation will appear here.";
const EMPTY_NOTE = "Request ID will appear here after a response.";
const INPUT_LIMIT = 500;
const CONFIG_ENDPOINT = "/api/config";
const TURNSTILE_SCRIPT_URL = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
const TURNSTILE_PENDING_NOTE = "Complete the security check before translating.";
const TURNSTILE_REFRESH_NOTE = "Complete the refreshed security check before translating again.";
const TURNSTILE_READY_NOTE = "Security check ready.";

const turnstileState = {
  enabled: false,
  widgetId: null,
  token: "",
  scriptPromise: null,
};

function updateCharCount() {
  charCount.textContent = `${sourceText.value.length} / ${INPUT_LIMIT}`;
}

function setStatus(message) {
  statusText.textContent = message;
}

function setResultNote(message = EMPTY_NOTE) {
  resultNote.textContent = message;
}

function setTurnstileNote(message) {
  if (!turnstileNote) {
    return;
  }
  turnstileNote.textContent = message;
}

function showError(message) {
  errorText.hidden = false;
  errorText.textContent = message;
}

function clearError() {
  errorText.hidden = true;
  errorText.textContent = "";
}

function resetResult() {
  resultOutput.textContent = EMPTY_RESULT;
  setResultNote();
  copyButton.disabled = true;
}

function clearTurnstileToken() {
  turnstileState.token = "";
}

function resetTurnstileWidget(message = TURNSTILE_PENDING_NOTE) {
  if (!turnstileState.enabled) {
    return;
  }

  clearTurnstileToken();
  if (turnstileState.widgetId !== null && window.turnstile?.reset) {
    window.turnstile.reset(turnstileState.widgetId);
  }
  setTurnstileNote(message);
}

async function fetchDeploymentConfig() {
  try {
    const response = await fetch(CONFIG_ENDPOINT, {
      headers: {
        accept: "application/json",
      },
    });
    if (!response.ok) {
      return { turnstileSiteKey: "" };
    }

    const payload = await response.json();
    return {
      turnstileSiteKey:
        typeof payload?.turnstileSiteKey === "string" ? payload.turnstileSiteKey.trim() : "",
    };
  } catch {
    return { turnstileSiteKey: "" };
  }
}

function loadTurnstileScript() {
  if (window.turnstile?.render) {
    return Promise.resolve(window.turnstile);
  }
  if (turnstileState.scriptPromise) {
    return turnstileState.scriptPromise;
  }

  turnstileState.scriptPromise = new Promise((resolve, reject) => {
    const existingScript = document.querySelector('script[data-turnstile-script="true"]');
    const script = existingScript ?? document.createElement("script");

    const handleLoad = () => {
      if (window.turnstile?.render) {
        resolve(window.turnstile);
        return;
      }
      reject(new Error("Turnstile client did not initialize"));
    };

    const handleError = () => {
      reject(new Error("Turnstile client failed to load"));
    };

    script.addEventListener("load", handleLoad, { once: true });
    script.addEventListener("error", handleError, { once: true });

    if (!existingScript) {
      script.src = TURNSTILE_SCRIPT_URL;
      script.async = true;
      script.defer = true;
      script.dataset.turnstileScript = "true";
      document.head.append(script);
    }
  });

  return turnstileState.scriptPromise;
}

async function initializeTurnstile() {
  const config = await fetchDeploymentConfig();
  if (!config.turnstileSiteKey || !turnstileBlock || !turnstileWidget) {
    return;
  }

  turnstileState.enabled = true;
  turnstileBlock.hidden = false;
  setTurnstileNote(TURNSTILE_PENDING_NOTE);

  try {
    const turnstile = await loadTurnstileScript();
    turnstileState.widgetId = turnstile.render(turnstileWidget, {
      sitekey: config.turnstileSiteKey,
      theme: "light",
      callback(token) {
        turnstileState.token = token;
        clearError();
        setTurnstileNote(TURNSTILE_READY_NOTE);
        if (statusText.textContent === "Complete security check") {
          setStatus("Ready");
        }
      },
      "expired-callback"() {
        clearTurnstileToken();
        setTurnstileNote("Security check expired. Please verify again.");
      },
      "error-callback"() {
        clearTurnstileToken();
        setStatus("Security check unavailable");
        setTurnstileNote("Security check failed to load. Refresh and try again.");
      },
      "timeout-callback"() {
        clearTurnstileToken();
        setTurnstileNote("Security check timed out. Please verify again.");
      },
    });
  } catch {
    setStatus("Security check unavailable");
    setTurnstileNote("Security check failed to load. Refresh and try again.");
  }
}

function applyExample(button) {
  sourceLang.value = button.dataset.sourceLang;
  targetLang.value = button.dataset.targetLang;
  sourceText.value = button.dataset.sourceText;
  updateCharCount();
  resetResult();
  clearError();
  setStatus("Ready");
}

function validateForm() {
  if (!sourceText.value.trim()) {
    return "Input text must not be empty";
  }
  if (sourceLang.value === targetLang.value) {
    return "Source and target languages must differ";
  }
  if (sourceText.value.length > INPUT_LIMIT) {
    return `Input exceeds the v1 limit of ${INPUT_LIMIT} characters`;
  }
  return null;
}

swapButton.addEventListener("click", () => {
  const previousSource = sourceLang.value;
  sourceLang.value = targetLang.value;
  targetLang.value = previousSource;
  clearError();
  setStatus("Ready");
});

clearButton.addEventListener("click", () => {
  sourceText.value = "";
  updateCharCount();
  resetResult();
  clearError();
  setStatus("Ready");
});

copyButton.addEventListener("click", async () => {
  if (copyButton.disabled || resultOutput.textContent === EMPTY_RESULT) {
    return;
  }

  try {
    await navigator.clipboard.writeText(resultOutput.textContent);
    setStatus("Copied");
  } catch {
    showError("Copy failed in this browser.");
    setStatus("Copy failed");
  }
});

exampleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    applyExample(button);
  });
});

sourceText.addEventListener("input", () => {
  updateCharCount();
});

updateCharCount();
resetResult();
void initializeTurnstile();

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  clearError();
  const validationError = validateForm();
  if (validationError) {
    resetResult();
    showError(validationError);
    setStatus("Check input");
    return;
  }
  if (turnstileState.enabled && !turnstileState.token) {
    resetResult();
    showError("Complete the security check before translating.");
    setStatus("Complete security check");
    return;
  }

  setStatus("Translating...");
  submitButton.disabled = true;

  try {
    const headers = {
      "content-type": "application/json",
    };
    if (turnstileState.enabled && turnstileState.token) {
      headers["cf-turnstile-response"] = turnstileState.token;
    }

    const response = await fetch("/api/translate", {
      method: "POST",
      headers,
      body: JSON.stringify({
        sourceText: sourceText.value,
        sourceLang: sourceLang.value,
        targetLang: targetLang.value,
      }),
    });

    const payload = await response.json();
    if (!response.ok) {
      resetResult();
      showError(payload.message ?? "Translation failed");
      setResultNote(payload.requestId ? `Request ID: ${payload.requestId}` : EMPTY_NOTE);
      setStatus(
        response.status === 429
          ? "Blocked by protection"
          : response.status === 503
            ? "Translator unavailable"
            : `Error ${response.status}`,
      );
      return;
    }

    resultOutput.textContent = payload.translation;
    setResultNote(`Request ID: ${payload.requestId}`);
    copyButton.disabled = false;
    setStatus(`Done · ${payload.model}`);
  } catch {
    resetResult();
    showError("Request failed before reaching the translator service.");
    setStatus("Network error");
  } finally {
    submitButton.disabled = false;
    resetTurnstileWidget(TURNSTILE_REFRESH_NOTE);
  }
});
