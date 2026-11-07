import Foundation
#if canImport(SGAProtection)
import SGAProtection
#endif
#if canImport(SGAIntegrity)
import SGAIntegrity
#endif
import CryptoKit
import Security
import LocalAuthentication

/// Explicit provisioning and biometric-bound private-key operations. Never deletes
/// or regenerates an existing key after a failure, restore or biometric change.
public final class SecureEnclaveVault {
    private static let enrollmentLock = NSLock()
    private let contextLock = NSLock()
    private var activeContext: LAContext?
    private var cancelled = false
    private let integrity: AppleIntegrityGuard
    private let scope: DocumentScope
    private let keyID: String
    private let algorithm = SecKeyAlgorithm.eciesEncryptionCofactorX963SHA256AESGCM
    public init(scope: DocumentScope, keyVersion: Int, integrity: AppleIntegrityGuard) throws { self.integrity = integrity; self.scope = scope; self.keyID = try scope.keyID(version: keyVersion) }

    private var query: [String: Any] { [kSecClass as String: kSecClassKey, kSecAttrApplicationTag as String: Data(keyID.utf8), kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom] }

    public func createKey() throws {
        try integrity.requireSensitiveOperation()
        guard Self.enrollmentLock.try() else { throw VaultError.keyUnavailable }
        defer { Self.enrollmentLock.unlock() }
        guard SecureEnclave.isAvailable else { throw VaultError.hardwareUnavailable }
        var lookup = query; lookup[kSecUseAuthenticationUI as String] = kSecUseAuthenticationUIFail
        let status = SecItemCopyMatching(lookup as CFDictionary, nil)
        guard status == errSecItemNotFound else { throw VaultError.keyExists }
        var accessError: Unmanaged<CFError>?
        guard let access = SecAccessControlCreateWithFlags(nil, kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly, [.privateKeyUsage, .biometryCurrentSet], &accessError) else { throw VaultError.hardwareUnavailable }
        let attributes: [String: Any] = [kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom, kSecAttrKeySizeInBits as String: 256,
            kSecAttrTokenID as String: kSecAttrTokenIDSecureEnclave, kSecPrivateKeyAttrs as String: [kSecAttrIsPermanent as String: true,
                kSecAttrApplicationTag as String: Data(keyID.utf8), kSecAttrAccessControl as String: access]]
        var error: Unmanaged<CFError>?
        guard SecKeyCreateRandomKey(attributes as CFDictionary, &error) != nil else { throw VaultError.hardwareUnavailable }
    }

    /// Cancels this instance's pending authentication without deleting a key.
    /// Retry with a new vault instance (same scope/version), not a new key.
    public func cancelPendingAuthentication() {
        contextLock.lock(); cancelled = true; let context = activeContext; contextLock.unlock()
        context?.invalidate()
    }
    private func endAuthentication() {
        contextLock.lock(); let context = activeContext; activeContext = nil; contextLock.unlock()
        context?.invalidate()
    }
    private func existingKey() throws -> SecKey {
        try AppleSensitiveScreen.requireSensitiveDisplay()
        try integrity.requireSensitiveOperation()
        guard SecureEnclave.isAvailable else { throw VaultError.hardwareUnavailable }
        let context = LAContext(); context.touchIDAuthenticationAllowableReuseDuration = 0
        context.localizedReason = "Autorizar acceso al documento cifrado"
        contextLock.lock()
        guard !cancelled, activeContext == nil else { contextLock.unlock(); throw VaultError.authenticationFailed }
        activeContext = context; contextLock.unlock()
        do {
            var lookup = query; lookup[kSecReturnRef as String] = true
            lookup[kSecUseAuthenticationContext as String] = context
            var result: CFTypeRef?
            guard SecItemCopyMatching(lookup as CFDictionary, &result) == errSecSuccess, let result else { throw VaultError.keyUnavailable }
            let key = result as! SecKey
            guard let attributes = SecKeyCopyAttributes(key) as? [String: Any],
                  attributes[kSecAttrTokenID as String] as? String == kSecAttrTokenIDSecureEnclave as String else { throw VaultError.hardwareUnavailable }
            return key
        } catch { endAuthentication(); throw error }
    }

    public func encrypt(_ document: Data, documentID: UUID) throws -> Data {
        guard document.count <= Envelope.maximum else { throw VaultError.invalidEnvelope }
        let privateKey = try existingKey()
        defer { endAuthentication() }
        guard let publicKey = SecKeyCopyPublicKey(privateKey), SecKeyIsAlgorithmSupported(publicKey, .encrypt, algorithm) else { throw VaultError.hardwareUnavailable }
        var bytes = Data(count: 32)
        let status = bytes.withUnsafeMutableBytes { SecRandomCopyBytes(kSecRandomDefault, 32, $0.baseAddress!) }
        guard status == errSecSuccess else { throw VaultError.cryptoFailed }
        defer { bytes.resetBytes(in: 0..<bytes.count) } // Best effort; Swift/CryptoKit may retain internal copies.
        var error: Unmanaged<CFError>?
        guard let wrapped = SecKeyCreateEncryptedData(publicKey, algorithm, bytes as CFData, &error) else { throw VaultError.cryptoFailed }
        try integrity.requireSensitiveOperation()
        return try DocumentAEAD.seal(document, key: SymmetricKey(data: bytes), context: scope.context(document: documentID), keyID: keyID, wrapped: wrapped as Data)
    }

    public func decrypt(_ encoded: Data, documentID: UUID) throws -> Data {
        let envelope = try Envelope.parse(encoded, platform: 2, context: scope.context(document: documentID), keyID: keyID)
        let privateKey = try existingKey()
        defer { endAuthentication() }
        guard SecKeyIsAlgorithmSupported(privateKey, .decrypt, algorithm) else { throw VaultError.hardwareUnavailable }
        var error: Unmanaged<CFError>?
        // The actual private-key operation triggers the system's access control.
        guard let unwrapped = SecKeyCreateDecryptedData(privateKey, algorithm, envelope.wrapped as CFData, &error) else { throw VaultError.authenticationFailed }
        var bytes = unwrapped as Data
        defer { bytes.resetBytes(in: 0..<bytes.count) }
        guard bytes.count == 32 else { throw VaultError.cryptoFailed }
        var plaintext = try DocumentAEAD.open(envelope, key: SymmetricKey(data: bytes))
        do { try integrity.requireSensitiveOperation(); try AppleSensitiveScreen.requireSensitiveDisplay(); return plaintext }
        catch { plaintext.resetBytes(in: 0..<plaintext.count); throw error } // No partial plaintext or error payload returned.
    }

    public func readEncrypted(documentID: UUID) throws -> Data {
        try integrity.requireSensitiveOperation()
        let support = try FileManager.default.url(for: .applicationSupportDirectory, in: .userDomainMask, appropriateFor: nil, create: false).standardizedFileURL
        let folder = support.appendingPathComponent("SGAVault", isDirectory: true).appendingPathComponent(keyID, isDirectory: true)
        let target = folder.appendingPathComponent(documentID.uuidString.lowercased() + ".vault")
        guard target.resolvingSymlinksInPath().path.hasPrefix(folder.resolvingSymlinksInPath().path + "/"),
              folder.resolvingSymlinksInPath().path.hasPrefix(support.resolvingSymlinksInPath().path + "/") else { throw VaultError.storageFailed }
        let file = try FileHandle(forReadingFrom: target)
        defer { try? file.close() }
        let encoded = try file.read(upToCount: Envelope.maximum + 2049) ?? Data()
        _ = try Envelope.parse(encoded, platform: 2, context: scope.context(document: documentID), keyID: keyID)
        return encoded
    }

    public func storeEncrypted(_ encoded: Data, documentID: UUID) throws {
        try integrity.requireSensitiveOperation()
        _ = try Envelope.parse(encoded, platform: 2, context: scope.context(document: documentID), keyID: keyID)
        // Directory must be app-private Application Support, never Documents/iCloud.
        let support = try FileManager.default.url(for: .applicationSupportDirectory, in: .userDomainMask, appropriateFor: nil, create: true).standardizedFileURL
        let folder = support.appendingPathComponent("SGAVault", isDirectory: true).appendingPathComponent(keyID, isDirectory: true)
        try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true, attributes: [.posixPermissions: 0o700])
        guard folder.resolvingSymlinksInPath().path.hasPrefix(support.resolvingSymlinksInPath().path + "/") else { throw VaultError.storageFailed }
        var resources = URLResourceValues(); resources.isExcludedFromBackup = true
        var mutableFolder = folder; try mutableFolder.setResourceValues(resources)
        let target = folder.appendingPathComponent(documentID.uuidString.lowercased() + ".vault")
        guard !FileManager.default.fileExists(atPath: target.path) else { throw VaultError.storageFailed }
        #if os(iOS)
        try encoded.write(to: target, options: [.atomic, .completeFileProtection])
        #else
        try encoded.write(to: target, options: [.atomic])
        #endif
        try FileManager.default.setAttributes([.posixPermissions: 0o600], ofItemAtPath: target.path)
    }
}
