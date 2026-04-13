import { handleTranslateRequest } from "../../src/translate.js";

export async function onRequestPost(context) {
  return handleTranslateRequest(context.request, context.env);
}
