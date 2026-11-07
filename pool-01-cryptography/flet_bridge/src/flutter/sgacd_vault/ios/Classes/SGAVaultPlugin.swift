import Flutter
import UIKit
import UniformTypeIdentifiers
import Foundation

/// A native picker supplies bytes directly to the vault. Flet sees only opaque IDs.
public final class SGAVaultPlugin: NSObject, FlutterPlugin, UIDocumentPickerDelegate {
    private final class Lifetime {
        private let lock = NSLock()
        private var cancelled = false
        func cancel() { lock.lock(); cancelled = true; lock.unlock() }
        func isActive() -> Bool { lock.lock(); defer { lock.unlock() }; return !cancelled }
    }
    private struct Operation {
        let id: UUID
        let vault: SecureEnclaveVault
        let scope: DocumentScope
        let version: Int
        let result: FlutterResult
        let lifetime = Lifetime()
    }
    private var active: Operation?
    private var pickerOperations: [ObjectIdentifier: UUID] = [:]
    private var currentPicker: UIDocumentPickerViewController?
    private let work = DispatchQueue(label: "co.analematica.vault.io")

    public static func register(with registrar: FlutterPluginRegistrar) {
        let channel = FlutterMethodChannel(name: "co.analematica/sgacd_vault/v1", binaryMessenger: registrar.messenger())
        let instance = SGAVaultPlugin(); registrar.addMethodCallDelegate(instance, channel: channel)
    }
    private func uuid(_ value: Any?) throws -> UUID {
        guard let text = value as? String, let id = UUID(uuidString: text), id.uuidString.lowercased() == text else { throw VaultError.invalidEnvelope }
        return id
    }
    private func presenter() -> UIViewController? {
        var view = UIApplication.shared.connectedScenes.filter { $0.activationState == .foregroundActive }.compactMap { $0 as? UIWindowScene }.flatMap { $0.windows }.first(where: { $0.isKeyWindow })?.rootViewController
        while let next = view?.presentedViewController { view = next }
        return view
    }
    private func finish(_ operation: Operation, status: String, fields: [String: Any] = [:]) {
        do { try AppleSensitiveScreen.requireSensitiveDisplay(); try AppleIntegrityGuard.fromApplication().requireSensitiveOperation() }
        catch { fail(operation, code: "CLIENT_INTEGRITY_BLOCKED"); return }
        DispatchQueue.main.async {
            guard self.active?.id == operation.id else { return }
            self.active = nil; operation.lifetime.cancel()
            var reply = fields; reply["ok"] = true; reply["protocol"] = 1; reply["status"] = status
            operation.result(reply)
        }
    }
    private func fail(_ operation: Operation, code: String) {
        DispatchQueue.main.async {
            guard self.active?.id == operation.id else { return }
            self.active = nil; operation.lifetime.cancel(); operation.vault.cancelPendingAuthentication(); operation.result(FlutterError(code: code, message: nil, details: nil))
        }
    }
    public func handle(_ call: FlutterMethodCall, result: @escaping FlutterResult) {
        guard let args = call.arguments as? [String: Any] else { result(FlutterError(code: "INVALID_ARGUMENTS", message: nil, details: nil)); return }
        if call.method == "cancel" {
            if let id = try? uuid(args["request_id"]), let operation = active, operation.id == id {
                if let picker = currentPicker { pickerOperations.removeValue(forKey: ObjectIdentifier(picker)); picker.dismiss(animated: true) }; currentPicker = nil
                active = nil; operation.lifetime.cancel(); operation.vault.cancelPendingAuthentication(); operation.result(FlutterError(code: "CANCELLED", message: nil, details: nil))
                // Keychain biometric prompts remain cancellable by the user. No key is removed.
            }
            result(nil); return
        }
        guard active == nil else { result(FlutterError(code: "BUSY", message: nil, details: nil)); return }
        guard ["provision", "import_document", "verify_document", "list_documents"].contains(call.method),
              Set(args.keys).isSubset(of: ["tenant","account","version","hardware","request_id","document_id"]) else {
            result(FlutterError(code: "UNSUPPORTED_METHOD", message: nil, details: nil)); return
        }
        do { try AppleSensitiveScreen.requireSensitiveDisplay(); try AppleIntegrityGuard.fromApplication().requireSensitiveOperation() }
        catch { result(FlutterError(code: "CLIENT_INTEGRITY_BLOCKED", message: nil, details: nil)); return }
        let operation: Operation
        do {
            let scope = DocumentScope(tenant: try uuid(args["tenant"]), account: try uuid(args["account"]))
            guard let versionText = args["version"] as? String, let version = Int(versionText), version > 0, version <= 2147483647,
                  let hardware = args["hardware"] as? String, ["STRONGBOX_REQUIRED","TRUSTED_HARDWARE"].contains(hardware) else { throw VaultError.invalidEnvelope }
            // Both policies map to Secure Enclave on iOS; there is no software option.
            operation = Operation(id: try uuid(args["request_id"]), vault: try SecureEnclaveVault(scope: scope, keyVersion: version, integrity: try AppleIntegrityGuard.fromApplication()), scope: scope, version: version, result: result)
        } catch { result(FlutterError(code: "INVALID_ARGUMENTS", message: nil, details: nil)); return }
        active = operation
        switch call.method {
        case "provision":
            guard let view = presenter() else { fail(operation, code: "ACTIVITY_UNAVAILABLE"); return }
            let alert = UIAlertController(title: "Crear llave local protegida", message: "Se creará una llave nueva para esta cuenta; no se borrará ni reemplazará una llave existente.", preferredStyle: .alert)
            alert.addAction(UIAlertAction(title: "Cancelar", style: .cancel) { _ in self.fail(operation, code: "CANCELLED") })
            alert.addAction(UIAlertAction(title: "Crear llave", style: .default) { _ in
                self.work.async {
                    guard operation.lifetime.isActive() else { return }
                    do { try operation.vault.createKey(); self.finish(operation, status: "provisioned") }
                    catch { self.fail(operation, code: "KEY_OR_HARDWARE_UNAVAILABLE") }
                }
            })
            view.present(alert, animated: true)
        case "import_document":
            guard let view = presenter() else { fail(operation, code: "ACTIVITY_UNAVAILABLE"); return }
            let picker = UIDocumentPickerViewController(forOpeningContentTypes: [.pdf, .jpeg, .png], asCopy: false)
            picker.allowsMultipleSelection = false; picker.delegate = self
            pickerOperations[ObjectIdentifier(picker)] = operation.id; currentPicker = picker
            view.present(picker, animated: true)
        case "verify_document":
            guard let document = try? uuid(args["document_id"]) else { fail(operation, code: "INVALID_ARGUMENTS"); return }
            work.async {
                do {
                    let encoded = try operation.vault.readEncrypted(documentID: document)
                    var bytes = try operation.vault.decrypt(encoded, documentID: document)
                    bytes.resetBytes(in: 0..<bytes.count)
                    self.finish(operation, status: "verified", fields: ["document_id": document.uuidString.lowercased()])
                } catch { self.fail(operation, code: "AUTHENTICATION_OR_INTEGRITY_FAILED") }
            }
        case "list_documents":
            work.async {
                do {
                    let support = try FileManager.default.url(for: .applicationSupportDirectory, in: .userDomainMask, appropriateFor: nil, create: true)
                    let folder = support.appendingPathComponent("SGAVault").appendingPathComponent(try operation.scope.keyID(version: operation.version))
                    let files = (try? FileManager.default.contentsOfDirectory(at: folder, includingPropertiesForKeys: nil)) ?? []
                    let documents = files.filter { $0.pathExtension == "vault" }.compactMap { UUID(uuidString: $0.deletingPathExtension().lastPathComponent)?.uuidString.lowercased() }.sorted()
                    self.finish(operation, status: "listed", fields: ["documents": Array(documents.prefix(64)), "has_more": documents.count > 64])
                } catch { self.fail(operation, code: "STORAGE_UNAVAILABLE") }
            }
        default: fail(operation, code: "UNSUPPORTED_METHOD")
        }
    }
    private func readDocument(_ source: URL) throws -> Data {
        let file = try FileHandle(forReadingFrom: source); defer { try? file.close() }
        var bytes = Data()
        do {
            while var part = try file.read(upToCount: 65536), !part.isEmpty {
                defer { part.resetBytes(in: 0..<part.count) }
                guard bytes.count + part.count <= Envelope.maximum else { throw VaultError.invalidEnvelope }
                bytes.append(part)
            }
            return bytes
        } catch { bytes.resetBytes(in: 0..<bytes.count); throw VaultError.storageFailed }
    }
    public func documentPickerWasCancelled(_ controller: UIDocumentPickerViewController) {
        let id = pickerOperations.removeValue(forKey: ObjectIdentifier(controller))
        guard let operation = active, id == operation.id else { return }
        currentPicker = nil; fail(operation, code: "CANCELLED")
    }
    public func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
        let id = pickerOperations.removeValue(forKey: ObjectIdentifier(controller))
        guard let operation = active, id == operation.id else { return }
        guard urls.count == 1, let source = urls.first, source.isFileURL else { fail(operation, code: "INVALID_DOCUMENT_SOURCE"); return }
        currentPicker = nil
        work.async {
            let document = UUID()
            let granted = source.startAccessingSecurityScopedResource()
            defer { if granted { source.stopAccessingSecurityScopedResource() } }
            do {
                guard operation.lifetime.isActive() else { return }
                var bytes = try self.readDocument(source)
                defer { bytes.resetBytes(in: 0..<bytes.count) }
                guard bytes.count <= Envelope.maximum else { throw VaultError.invalidEnvelope }
                let encrypted = try operation.vault.encrypt(bytes, documentID: document)
                guard operation.lifetime.isActive() else { return }
                try operation.vault.storeEncrypted(encrypted, documentID: document)
                self.finish(operation, status: "stored", fields: ["document_id": document.uuidString.lowercased()])
            } catch { self.fail(operation, code: "DOCUMENT_IMPORT_FAILED") }
        }
    }
}
