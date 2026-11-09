/** Browser envelope primitive. No network, persistence, key generation policy or recovery service. */
export const SCHEMA='sgacd-fiscal-envelope-v1';
export const ALGORITHM='AES-256-GCM+A256KW';
export const MAX_DOCUMENT_BYTES=16*1024*1024;
export type DocumentContext={company_id:string;document_id:string};
export type FiscalEnvelope={schema:typeof SCHEMA;algorithm:typeof ALGORITHM;context:DocumentContext;iv:string;wrapped_key:string;ciphertext:string};
const encoder=new TextEncoder();
function exact(value:unknown,keys:string[]):value is Record<string,unknown>{return !!value&&typeof value==='object'&&!Array.isArray(value)&&Object.keys(value).length===keys.length&&keys.every(k=>Object.prototype.hasOwnProperty.call(value,k));}
function context(value:unknown):DocumentContext{
 if(!exact(value,['company_id','document_id']))throw Error('Invalid document context.');
 const uuid=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
 if(typeof value.company_id!=='string'||typeof value.document_id!=='string'||!uuid.test(value.company_id)||!uuid.test(value.document_id))throw Error('UUID document context required.');
 return {company_id:value.company_id.toLowerCase(),document_id:value.document_id.toLowerCase()};
}
function aad(value:DocumentContext){return encoder.encode(JSON.stringify([SCHEMA,ALGORITHM,value.company_id,value.document_id,'fiscal-document']));}
function kek(key:CryptoKey,usage:KeyUsage){
 if(!key||key.type!=='secret'||key.extractable||key.algorithm.name!=='AES-KW'||(key.algorithm as AesKeyAlgorithm).length!==256||!key.usages.includes(usage))throw Error('A nonextractable client AES-KW-256 key with the required usage is required.');
}
function encode(bytes:Uint8Array){let text='';for(let i=0;i<bytes.length;i+=32768)text+=String.fromCharCode(...bytes.subarray(i,i+32768));return btoa(text).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');}
function decode(text:unknown,min:number,max:number){
 if(typeof text!=='string'||text.length>Math.ceil(max*4/3)+2||!text.length||!/^[A-Za-z0-9_-]+$/.test(text))throw Error('Invalid envelope encoding.');
 const raw=atob(text.replace(/-/g,'+').replace(/_/g,'/')+'='.repeat((4-text.length%4)%4));
 const bytes=Uint8Array.from(raw,c=>c.charCodeAt(0));
 if(bytes.length<min||bytes.length>max||encode(bytes)!==text)throw Error('Invalid envelope length or canonical encoding.');return bytes;
}
function parse(value:unknown,expected:DocumentContext){
 if(!exact(value,['schema','algorithm','context','iv','wrapped_key','ciphertext'])||value.schema!==SCHEMA||value.algorithm!==ALGORITHM)throw Error('Unsupported envelope.');
 const actual=context(value.context),wanted=context(expected);
 if(actual.company_id!==wanted.company_id||actual.document_id!==wanted.document_id)throw Error('Envelope context mismatch.');
 const envelope:FiscalEnvelope={schema:SCHEMA,algorithm:ALGORITHM,context:actual,iv:value.iv as string,wrapped_key:value.wrapped_key as string,ciphertext:value.ciphertext as string};
 return {envelope,iv:decode(value.iv,12,12),wrapped:decode(value.wrapped_key,40,40),ciphertext:decode(value.ciphertext,17,MAX_DOCUMENT_BYTES+16)};
}
export async function encryptDocument(plaintext:Uint8Array,clientKek:CryptoKey,documentContext:DocumentContext):Promise<FiscalEnvelope>{
 kek(clientKek,'wrapKey');const scope=context(documentContext);
 if(!(plaintext instanceof Uint8Array)||!plaintext.length||plaintext.length>MAX_DOCUMENT_BYTES)throw Error('Document size outside supported bounds.');
 const copy=new Uint8Array(plaintext);const raw=crypto.getRandomValues(new Uint8Array(32));const iv=crypto.getRandomValues(new Uint8Array(12));
 try{
  const dek=await crypto.subtle.importKey('raw',raw,{name:'AES-GCM'},true,['encrypt']);
  const wrapped=await crypto.subtle.wrapKey('raw',dek,clientKek,'AES-KW');
  const ciphertext=await crypto.subtle.encrypt({name:'AES-GCM',iv,additionalData:aad(scope),tagLength:128},dek,copy);
  return {schema:SCHEMA,algorithm:ALGORITHM,context:scope,iv:encode(iv),wrapped_key:encode(new Uint8Array(wrapped)),ciphertext:encode(new Uint8Array(ciphertext))};
 }finally{raw.fill(0);copy.fill(0);}
}
export async function decryptDocument(value:unknown,clientKek:CryptoKey,expected:DocumentContext):Promise<Uint8Array>{
 try{
  kek(clientKek,'unwrapKey');const parsed=parse(value,expected);
  const dek=await crypto.subtle.unwrapKey('raw',parsed.wrapped,clientKek,'AES-KW',{name:'AES-GCM',length:256},false,['decrypt']);
  return new Uint8Array(await crypto.subtle.decrypt({name:'AES-GCM',iv:parsed.iv,additionalData:aad(parsed.envelope.context),tagLength:128},dek,parsed.ciphertext));
 }catch{throw Error('Envelope unavailable or authentication failed.');}
}
export async function rewrapDocument(value:unknown,oldKek:CryptoKey,newKek:CryptoKey,expected:DocumentContext):Promise<FiscalEnvelope>{
 let verified:Uint8Array|undefined;
 try{
  kek(oldKek,'unwrapKey');kek(newKek,'wrapKey');const parsed=parse(value,expected);
  const dek=await crypto.subtle.unwrapKey('raw',parsed.wrapped,oldKek,'AES-KW',{name:'AES-GCM',length:256},true,['decrypt']);
  verified=new Uint8Array(await crypto.subtle.decrypt({name:'AES-GCM',iv:parsed.iv,additionalData:aad(parsed.envelope.context),tagLength:128},dek,parsed.ciphertext));
  const wrapped=await crypto.subtle.wrapKey('raw',dek,newKek,'AES-KW');
  return {...parsed.envelope,context:{...parsed.envelope.context},wrapped_key:encode(new Uint8Array(wrapped))};
 }catch{throw Error('Envelope unavailable or authentication failed.');}
 finally{verified?.fill(0);}
}
