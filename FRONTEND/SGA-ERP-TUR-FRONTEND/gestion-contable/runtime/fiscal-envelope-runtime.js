/* Own ERP browser adapter; server rendering performs no DOM work. */
if(typeof window!=='undefined'){
/* GENERATED from FRONTEND/shared/accounting/fiscalEnvelope.ts with esbuild0.25.11; rebuild/check with FRONTEND/deployment/build_fiscal_runtime.cjs. */
(()=>{
var SGACDEnvelopeRuntime = (() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // fiscalEnvelope.ts
  var fiscalEnvelope_exports = {};
  __export(fiscalEnvelope_exports, {
    ALGORITHM: () => ALGORITHM,
    MAX_DOCUMENT_BYTES: () => MAX_DOCUMENT_BYTES,
    SCHEMA: () => SCHEMA,
    decryptDocument: () => decryptDocument,
    encryptDocument: () => encryptDocument,
    rewrapDocument: () => rewrapDocument
  });
  var SCHEMA = "sgacd-fiscal-envelope-v1";
  var ALGORITHM = "AES-256-GCM+A256KW";
  var MAX_DOCUMENT_BYTES = 16 * 1024 * 1024;
  var encoder = new TextEncoder();
  function exact(value, keys) {
    return !!value && typeof value === "object" && !Array.isArray(value) && Object.keys(value).length === keys.length && keys.every((k) => Object.prototype.hasOwnProperty.call(value, k));
  }
  function context(value) {
    if (!exact(value, ["company_id", "document_id"])) throw Error("Invalid document context.");
    const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (typeof value.company_id !== "string" || typeof value.document_id !== "string" || !uuid.test(value.company_id) || !uuid.test(value.document_id)) throw Error("UUID document context required.");
    return { company_id: value.company_id.toLowerCase(), document_id: value.document_id.toLowerCase() };
  }
  function aad(value) {
    return encoder.encode(JSON.stringify([SCHEMA, ALGORITHM, value.company_id, value.document_id, "fiscal-document"]));
  }
  function kek(key, usage) {
    if (!key || key.type !== "secret" || key.extractable || key.algorithm.name !== "AES-KW" || key.algorithm.length !== 256 || !key.usages.includes(usage)) throw Error("A nonextractable client AES-KW-256 key with the required usage is required.");
  }
  function encode(bytes) {
    let text = "";
    for (let i = 0; i < bytes.length; i += 32768) text += String.fromCharCode(...bytes.subarray(i, i + 32768));
    return btoa(text).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }
  function decode(text, min, max) {
    if (typeof text !== "string" || text.length > Math.ceil(max * 4 / 3) + 2 || !text.length || !/^[A-Za-z0-9_-]+$/.test(text)) throw Error("Invalid envelope encoding.");
    const raw = atob(text.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - text.length % 4) % 4));
    const bytes = Uint8Array.from(raw, (c) => c.charCodeAt(0));
    if (bytes.length < min || bytes.length > max || encode(bytes) !== text) throw Error("Invalid envelope length or canonical encoding.");
    return bytes;
  }
  function parse(value, expected) {
    if (!exact(value, ["schema", "algorithm", "context", "iv", "wrapped_key", "ciphertext"]) || value.schema !== SCHEMA || value.algorithm !== ALGORITHM) throw Error("Unsupported envelope.");
    const actual = context(value.context), wanted = context(expected);
    if (actual.company_id !== wanted.company_id || actual.document_id !== wanted.document_id) throw Error("Envelope context mismatch.");
    const envelope = { schema: SCHEMA, algorithm: ALGORITHM, context: actual, iv: value.iv, wrapped_key: value.wrapped_key, ciphertext: value.ciphertext };
    return { envelope, iv: decode(value.iv, 12, 12), wrapped: decode(value.wrapped_key, 40, 40), ciphertext: decode(value.ciphertext, 17, MAX_DOCUMENT_BYTES + 16) };
  }
  async function encryptDocument(plaintext, clientKek, documentContext) {
    kek(clientKek, "wrapKey");
    const scope = context(documentContext);
    if (!(plaintext instanceof Uint8Array) || !plaintext.length || plaintext.length > MAX_DOCUMENT_BYTES) throw Error("Document size outside supported bounds.");
    const copy = new Uint8Array(plaintext);
    const raw = crypto.getRandomValues(new Uint8Array(32));
    const iv = crypto.getRandomValues(new Uint8Array(12));
    try {
      const dek = await crypto.subtle.importKey("raw", raw, { name: "AES-GCM" }, true, ["encrypt"]);
      const wrapped = await crypto.subtle.wrapKey("raw", dek, clientKek, "AES-KW");
      const ciphertext = await crypto.subtle.encrypt({ name: "AES-GCM", iv, additionalData: aad(scope), tagLength: 128 }, dek, copy);
      return { schema: SCHEMA, algorithm: ALGORITHM, context: scope, iv: encode(iv), wrapped_key: encode(new Uint8Array(wrapped)), ciphertext: encode(new Uint8Array(ciphertext)) };
    } finally {
      raw.fill(0);
      copy.fill(0);
    }
  }
  async function decryptDocument(value, clientKek, expected) {
    try {
      kek(clientKek, "unwrapKey");
      const parsed = parse(value, expected);
      const dek = await crypto.subtle.unwrapKey("raw", parsed.wrapped, clientKek, "AES-KW", { name: "AES-GCM", length: 256 }, false, ["decrypt"]);
      return new Uint8Array(await crypto.subtle.decrypt({ name: "AES-GCM", iv: parsed.iv, additionalData: aad(parsed.envelope.context), tagLength: 128 }, dek, parsed.ciphertext));
    } catch {
      throw Error("Envelope unavailable or authentication failed.");
    }
  }
  async function rewrapDocument(value, oldKek, newKek, expected) {
    let verified;
    try {
      kek(oldKek, "unwrapKey");
      kek(newKek, "wrapKey");
      const parsed = parse(value, expected);
      const dek = await crypto.subtle.unwrapKey("raw", parsed.wrapped, oldKek, "AES-KW", { name: "AES-GCM", length: 256 }, true, ["decrypt"]);
      verified = new Uint8Array(await crypto.subtle.decrypt({ name: "AES-GCM", iv: parsed.iv, additionalData: aad(parsed.envelope.context), tagLength: 128 }, dek, parsed.ciphertext));
      const wrapped = await crypto.subtle.wrapKey("raw", dek, newKek, "AES-KW");
      return { ...parsed.envelope, context: { ...parsed.envelope.context }, wrapped_key: encode(new Uint8Array(wrapped)) };
    } catch {
      throw Error("Envelope unavailable or authentication failed.");
    } finally {
      verified?.fill(0);
    }
  }
  return __toCommonJS(fiscalEnvelope_exports);
})();

if(typeof window!=="undefined")window.SGACDFiscalEnvelope=SGACDEnvelopeRuntime;
})();

}
