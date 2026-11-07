import 'package:flutter_test/flutter_test.dart';
import 'package:sgacd_vault/src/metadata_contract.dart';

void main() {
  const id = '00000000-0000-0000-0000-000000000001';
  Map<String,String> request() => {'tenant':id,'account':id,'version':'1','hardware':'STRONGBOX_REQUIRED','request_id':id};
  test('only scoped metadata can reach the native channel', () {
    expect(validRequest('provision', request()), isTrue);
    expect(validRequest('import_document', {...request(),'plaintext':'secret'}), isFalse);
    expect(validRequest('verify_document', request()), isFalse);
    expect(validRequest('verify_document', {...request(),'document_id':id}), isTrue);
    expect(validRequest('import_document', {...request(),'account':'file:///private/document'}), isFalse);
    expect(validRequest('export_key', request()), isFalse);
    expect(validRequest('provision', {...request(),'hardware':'SOFTWARE'}), isFalse);
  });
  test('sensitive or malformed native replies never reach Python', () {
    expect(publicError('PRIVATEUPPERCASECONTENTS'), 'NATIVE_UNAVAILABLE');
    expect(publicError('CANCELLED'), 'CANCELLED');
    final good = {'ok':true,'protocol':1,'status':'stored','document_id':id};
    expect(publicReply('import_document', good), good);
    expect(publicReply('import_document', {...good,'bytes':'sensitive'}), isNull);
    expect(publicReply('import_document', {...good,'document_id':'plain document contents'}), isNull);
    expect(publicReply('import_document', {...good,'protocol':true}), isNull);
    expect(publicReply('list_documents', {'ok':true,'protocol':1,'status':'listed','documents':['file:///identity'],'has_more':false}), isNull);
    expect(publicReply('list_documents', {'ok':true,'protocol':1,'status':'listed','documents':List.filled(65,id),'has_more':true}), isNull);
  });
}
