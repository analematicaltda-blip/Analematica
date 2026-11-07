import Foundation
import CryptoKit

public enum VaultError: Error { case invalidEnvelope, keyUnavailable, keyExists, hardwareUnavailable, authenticationFailed, cryptoFailed, storageFailed, invalidPassphrase }

public struct DocumentScope: Sendable {
    public let tenant: UUID
    public let account: UUID
    public init(tenant: UUID, account: UUID) { self.tenant = tenant; self.account = account }
    public func context(document: UUID) -> String { "sgacd/v1/\(tenant.uuidString.lowercased())/\(account.uuidString.lowercased())/\(document.uuidString.lowercased())" }
    public func keyID(version: Int) throws -> String {
        guard version > 0 else { throw VaultError.keyUnavailable }
        let input = "\(tenant.uuidString.lowercased())/\(account.uuidString.lowercased())/\(version)"
        return "sgacd.vault." + SHA256.hash(data: Data(input.utf8)).map { String(format: "%02x", $0) }.joined()
    }
}

struct Envelope {
    static let maximum = 8 * 1024 * 1024
    static let magic = Data("SGAVLT01".utf8)
    let header: Data
    let nonce: Data
    let wrapped: Data
    let ciphertext: Data

    static func header(platform: UInt8, context: String, keyID: String, wrapped: Data, nonce: Data, size: Int) throws -> Data {
        let scope = Data(context.utf8), key = Data(keyID.utf8)
        guard (platform == 1 || platform == 2), !scope.isEmpty, scope.count <= 256, !key.isEmpty, key.count <= 128,
              wrapped.count <= 1024, (platform == 1 ? wrapped.isEmpty : !wrapped.isEmpty),
              nonce.count == 12, size >= 16, size <= maximum + 16 else { throw VaultError.invalidEnvelope }
        var result = magic; result.append(platform)
        func length(_ count: Int) { result.append(UInt8((count >> 8) & 255)); result.append(UInt8(count & 255)) }
        length(scope.count); result.append(scope); length(key.count); result.append(key); length(wrapped.count); result.append(wrapped)
        result.append(nonce)
        for shift in [24, 16, 8, 0] { result.append(UInt8((size >> shift) & 255)) }
        return result
    }

    static func parse(_ encoded: Data, platform: UInt8, context: String, keyID: String) throws -> Envelope {
        guard encoded.count <= maximum + 2048 else { throw VaultError.invalidEnvelope }
        let input = Data(encoded); var offset = 0
        func read(_ size: Int) throws -> Data {
            guard size >= 0, offset <= input.count, size <= input.count - offset else { throw VaultError.invalidEnvelope }
            defer { offset += size }; return input.subdata(in: offset..<(offset + size))
        }
        func field(_ maximum: Int, empty: Bool = false) throws -> Data {
            let length = try read(2).reduce(0) { ($0 << 8) | Int($1) }
            guard length <= maximum, empty || length > 0 else { throw VaultError.invalidEnvelope }
            return try read(length)
        }
        guard try read(8) == magic, try read(1) == Data([platform]), platform == 1 || platform == 2 else { throw VaultError.invalidEnvelope }
        let scope = try field(256), key = try field(128), wrapped = try field(1024, empty: true), nonce = try read(12)
        guard String(data: scope, encoding: .utf8) == context, String(data: key, encoding: .utf8) == keyID,
              (platform == 1 ? wrapped.isEmpty : !wrapped.isEmpty) else { throw VaultError.invalidEnvelope }
        let size = try read(4).reduce(0) { ($0 << 8) | Int($1) }
        guard size >= 16, size <= maximum + 16, size == input.count - offset else { throw VaultError.invalidEnvelope }
        let header = input.prefix(offset), ciphertext = try read(size)
        return Envelope(header: Data(header), nonce: nonce, wrapped: wrapped, ciphertext: ciphertext)
    }
}

// AES executes in process memory on Apple platforms. Only the wrapping private key
// resides in Secure Enclave; an AES SymmetricKey is NOT a Secure Enclave key.
enum DocumentAEAD {
    static func seal(_ document: Data, key: SymmetricKey, context: String, keyID: String, wrapped: Data) throws -> Data {
        guard document.count <= Envelope.maximum, key.bitCount == 256 else { throw VaultError.invalidEnvelope }
        let nonce = AES.GCM.Nonce()
        let header = try Envelope.header(platform: 2, context: context, keyID: keyID, wrapped: wrapped, nonce: Data(nonce), size: document.count + 16)
        let box = try AES.GCM.seal(document, using: key, nonce: nonce, authenticating: header)
        return header + box.ciphertext + box.tag
    }
    static func open(_ envelope: Envelope, key: SymmetricKey) throws -> Data {
        guard key.bitCount == 256 else { throw VaultError.cryptoFailed }
        let box = try AES.GCM.SealedBox(nonce: AES.GCM.Nonce(data: envelope.nonce), ciphertext: envelope.ciphertext.dropLast(16), tag: envelope.ciphertext.suffix(16))
        return try AES.GCM.open(box, using: key, authenticating: envelope.header)
    }
}
