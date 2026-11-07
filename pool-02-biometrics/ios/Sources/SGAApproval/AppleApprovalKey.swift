import Foundation
import CryptoKit
import Security
import LocalAuthentication

/// Hardware-biometric signing only. This is NOT an offline Apple attestation service.
public final class AppleApprovalKey {
    private static let enrollmentLock = NSLock()
    private let lock = NSLock()
    private var activeContext: LAContext?
    private var cancelled = false
    private let audience: UUID
    private let actor: Int64
    private let credential: UUID
    private let tag: Data
    public init(audience: UUID, actor: Int64, credential: UUID) throws {
        guard actor > 0 else { throw ApprovalError.scopeMismatch }
        self.audience = audience; self.actor = actor; self.credential = credential
        let scope = "\(audience.uuidString.lowercased())/\(actor)/\(credential.uuidString.lowercased())"
        let digest = SHA256.hash(data: Data(scope.utf8)).map { String(format: "%02x", $0) }.joined()
        tag = Data(("sgacd.approval." + digest).utf8)
    }
    private var query: [String: Any] { [kSecClass as String: kSecClassKey, kSecAttrApplicationTag as String: tag, kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom] }
    public func createKey() throws {
        guard Self.enrollmentLock.try() else { throw ApprovalError.keyUnavailable }; defer { Self.enrollmentLock.unlock() }
        guard SecureEnclave.isAvailable else { throw ApprovalError.hardwareUnavailable }
        var probe = query; probe[kSecUseAuthenticationUI as String] = kSecUseAuthenticationUIFail
        guard SecItemCopyMatching(probe as CFDictionary, nil) == errSecItemNotFound else { throw ApprovalError.keyUnavailable }
        var error: Unmanaged<CFError>?
        guard let access = SecAccessControlCreateWithFlags(nil, kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly, [.privateKeyUsage, .biometryCurrentSet], &error) else { throw ApprovalError.hardwareUnavailable }
        let params: [String: Any] = [kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom, kSecAttrKeySizeInBits as String: 256,
            kSecAttrTokenID as String: kSecAttrTokenIDSecureEnclave, kSecPrivateKeyAttrs as String: [kSecAttrIsPermanent as String: true,kSecAttrApplicationTag as String: tag,kSecAttrAccessControl as String: access]]
        guard SecKeyCreateRandomKey(params as CFDictionary, &error) != nil else { throw ApprovalError.hardwareUnavailable }
    }
    private func existing(reason: String) throws -> SecKey {
        guard SecureEnclave.isAvailable else { throw ApprovalError.hardwareUnavailable }
        let context = LAContext(); context.localizedReason = reason; context.touchIDAuthenticationAllowableReuseDuration = 0
        lock.lock(); guard !cancelled, activeContext == nil else { lock.unlock(); throw ApprovalError.cancelled }; activeContext = context; lock.unlock()
        do {
            var request = query; request[kSecReturnRef as String] = true; request[kSecUseAuthenticationContext as String] = context
            var item: CFTypeRef?
            guard SecItemCopyMatching(request as CFDictionary, &item) == errSecSuccess, let item else { throw ApprovalError.keyUnavailable }
            let key = item as! SecKey
            guard let attributes = SecKeyCopyAttributes(key) as? [String: Any], attributes[kSecAttrTokenID as String] as? String == kSecAttrTokenIDSecureEnclave as String else { throw ApprovalError.hardwareUnavailable }
            return key
        } catch { finish(); throw error }
    }
    private func finish() { lock.lock(); let context = activeContext; activeContext = nil; lock.unlock(); context?.invalidate() }
    public func cancel() { lock.lock(); cancelled = true; let context = activeContext; lock.unlock(); context?.invalidate() }
    public func publicKey() throws -> Data {
        let key = try existing(reason: "Consultar llave pública de autorización"); defer { finish() }
        var error: Unmanaged<CFError>?
        guard let publicKey = SecKeyCopyPublicKey(key), let data = SecKeyCopyExternalRepresentation(publicKey, &error) else { throw ApprovalError.keyUnavailable }
        let bytes = data as Data
        guard bytes.count == 65, bytes.first == 4 else { throw ApprovalError.keyUnavailable }
        return bytes // Public point only; no private-key export method exists.
    }
    public func approve(_ payload: Data) throws -> Data {
        let message = try ApprovalMessage.parse(payload, audience: audience, actor: actor, credential: credential)
        let key = try existing(reason: message.summary); defer { finish() }
        var error: Unmanaged<CFError>?
        guard SecKeyIsAlgorithmSupported(key, .sign, .ecdsaSignatureMessageX962SHA256),
              let signature = SecKeyCreateSignature(key, .ecdsaSignatureMessageX962SHA256, message.bytes as CFData, &error) else { throw ApprovalError.signatureFailed }
        _ = try ApprovalMessage.parse(message.bytes, audience: audience, actor: actor, credential: credential)
        return signature as Data
    }
}
