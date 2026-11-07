import Foundation
import CommonCrypto

public enum PasswordKdf {
    public static let iterations: UInt32 = 600_000
    /// Optional passphrase derivation. Not a replacement for hardware keys or OS PIN throttling.
    public static func derive(_ passphrase: String, salt: Data) throws -> Data {
        var password = Data(passphrase.utf8)
        guard passphrase.count >= 12, passphrase.utf8.count <= 1024, salt.count == 16 else { throw VaultError.invalidPassphrase }
        defer { password.resetBytes(in: 0..<password.count) }
        var output = Data(count: 32)
        let status = output.withUnsafeMutableBytes { derived in
            password.withUnsafeBytes { secret in
                salt.withUnsafeBytes { random in
                    CCKeyDerivationPBKDF(CCPBKDFAlgorithm(kCCPBKDF2), secret.baseAddress!.assumingMemoryBound(to: Int8.self), password.count,
                        random.baseAddress!.assumingMemoryBound(to: UInt8.self), salt.count, CCPseudoRandomAlgorithm(kCCPRFHmacAlgSHA256),
                        iterations, derived.baseAddress!.assumingMemoryBound(to: UInt8.self), 32)
                }
            }
        }
        guard status == kCCSuccess else { throw VaultError.cryptoFailed }
        return output
    }
}
