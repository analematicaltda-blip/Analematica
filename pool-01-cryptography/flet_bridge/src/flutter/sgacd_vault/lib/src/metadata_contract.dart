// Validation happens in the native client BEFORE a reply crosses the Flet transport.
bool _uuid(Object? value) => value is String && value.length == 36 &&
    RegExp(r'^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$').hasMatch(value);
const _statuses = {'provision':'provisioned','import_document':'stored','verify_document':'verified','list_documents':'listed'};
bool validRequest(String method, Map<String, String> args) {
  if (!_statuses.containsKey(method)) return false;
  final required = {'tenant','account','version','hardware','request_id', if(method == 'verify_document') 'document_id'};
  if (args.length != required.length || !args.keys.every(required.contains)) return false;
  if (!['tenant','account','request_id',if(method == 'verify_document') 'document_id'].every((key) => _uuid(args[key]))) return false;
  final version = int.tryParse(args['version'] ?? '');
  return version != null && version > 0 && version <= 2147483647 && version.toString() == args['version'] &&
      {'STRONGBOX_REQUIRED','TRUSTED_HARDWARE'}.contains(args['hardware']);
}
Map<String, dynamic>? publicReply(String method, Map<String, dynamic>? reply) {
  if (!_statuses.containsKey(method) || reply == null || reply['ok'] != true || reply['protocol'] is! int || reply['protocol'] != 1 || reply['status'] != _statuses[method]) return null;
  final fields = {'ok','protocol','status', if(method == 'import_document' || method == 'verify_document') 'document_id', if(method == 'list_documents') ...['documents','has_more']};
  if (reply.length != fields.length || !reply.keys.every(fields.contains)) return null;
  if ((method == 'import_document' || method == 'verify_document') && !_uuid(reply['document_id'])) return null;
  if (method == 'list_documents') {
    final docs = reply['documents'];
    if (docs is! List || docs.length > 64 || !docs.every(_uuid) || reply['has_more'] is! bool) return null;
  }
  return reply;
}

const _safeErrors = {'NATIVE_UNAVAILABLE','BUSY','BUSY_OR_UNSUPPORTED','INVALID_ARGUMENTS','INVALID_ARGUMENTS_OR_UNAVAILABLE','ACTIVITY_UNAVAILABLE','CANCELLED','UNSUPPORTED_METHOD','KEY_ALREADY_EXISTS','KEY_OR_HARDWARE_UNAVAILABLE','KEY_OR_ENCRYPTION_UNAVAILABLE','STRONG_BIOMETRICS_REQUIRED','ENROLLMENT_BUSY','ENROLLMENT_LOCK_UNAVAILABLE','HARDWARE_POLICY_MISMATCH','KEY_MISSING','AUTHENTICATION_OR_INTEGRITY_FAILED','INVALID_DOCUMENT_OR_KEY_UNAVAILABLE','BIOMETRIC_CANCELLED_OR_UNAVAILABLE','BIOMETRIC_CANCELLED','BIOMETRIC_UNAVAILABLE','PICKER_UNAVAILABLE','INVALID_DOCUMENT_SOURCE','DOCUMENT_IMPORT_FAILED','DOCUMENT_ALREADY_EXISTS_USE_NEW_UUID','ENCRYPTED_STORAGE_FAILED','INVALID_ENCRYPTED_FILE','ENCRYPTED_FILE_TOO_LARGE','PRIVATE_STORAGE_UNAVAILABLE','STORAGE_UNAVAILABLE','NATIVE_OPERATION_FAILED','CLIENT_INTEGRITY_BLOCKED'};
String publicError(String code) => _safeErrors.contains(code) ? code : 'NATIVE_UNAVAILABLE';
