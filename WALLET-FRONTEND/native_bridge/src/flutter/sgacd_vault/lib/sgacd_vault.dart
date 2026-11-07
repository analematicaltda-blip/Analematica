library sgacd_vault;
import 'dart:convert';
import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'src/metadata_contract.dart';

CreateControlFactory createControl = (CreateControlArgs args) => {'sgacdvault','sgacdsensitivedisplay'}.contains(args.control.type)
    ? VaultControl(control: args.control, backend: args.backend) : null;
void ensureInitialized() {}

class VaultControl extends StatefulWidget {
  final Control control;
  final FletControlBackend backend;
  const VaultControl({super.key, required this.control, required this.backend});
  @override
  State<VaultControl> createState() => _VaultControlState();
}
class _VaultControlState extends State<VaultControl> {
  static const channel = MethodChannel('co.analematica/sgacd_vault/v1');
  String? activeRequest;
  static const methods = {'provision', 'import_document', 'verify_document', 'list_documents'};
  @override
  void initState() {
    super.initState();
    widget.control.onRemove.add(remove);
    widget.backend.subscribeMethods(widget.control.id, (method, args) async {
      if (kIsWeb || !{TargetPlatform.android, TargetPlatform.iOS}.contains(defaultTargetPlatform)) {
        return jsonEncode({'ok': false, 'code': 'NATIVE_UNAVAILABLE'});
      }
      if (widget.control.type == 'sgacdsensitivedisplay') {
        if (method != 'protect_display' || args.isNotEmpty) return jsonEncode({'ok':false,'code':'UNSUPPORTED_METHOD'});
        try {
          final reply = await channel.invokeMapMethod<String,dynamic>('protect_display', <String,String>{});
          if (reply == null || reply.length != 3 || reply['ok'] != true || reply['protocol'] is! int || reply['protocol'] != 1 || reply['status'] != 'protected') return jsonEncode({'ok':false,'code':'NATIVE_UNAVAILABLE'});
          return jsonEncode(reply);
        } catch (_) { return jsonEncode({'ok':false,'code':'NATIVE_UNAVAILABLE'}); }
      }
      if (!methods.contains(method) || activeRequest != null) return jsonEncode({'ok': false, 'code': 'BUSY_OR_UNSUPPORTED'});
      if (!validRequest(method, args)) return jsonEncode({'ok': false, 'code': 'INVALID_ARGUMENTS'});
      activeRequest = args['request_id'];
      try {
        // Only opaque IDs and state are permitted in the native reply, never bytes.
        final reply = await channel.invokeMapMethod<String, dynamic>(method, args);
        if (publicReply(method, reply) == null) {
          return jsonEncode({'ok': false, 'code': 'INVALID_NATIVE_RESPONSE'});
        }
        return jsonEncode(reply);
      } on PlatformException catch (error) {
        final code = publicError(error.code);
        return jsonEncode({'ok': false, 'code': code});
      } catch (_) {
        return jsonEncode({'ok': false, 'code': 'NATIVE_UNAVAILABLE'});
      } finally { activeRequest = null; }
    });
  }
  void remove() {
    widget.backend.unsubscribeMethods(widget.control.id);
    final request = activeRequest;
    if (request != null) channel.invokeMethod<void>('cancel', {'request_id': request}).catchError((_) {});
  }
  @override
  void dispose() { remove(); widget.control.onRemove.remove(remove); super.dispose(); }
  @override
  Widget build(BuildContext context) => const SizedBox.shrink();
}
