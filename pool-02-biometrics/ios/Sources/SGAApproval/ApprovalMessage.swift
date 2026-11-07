import Foundation
import CryptoKit

public enum ApprovalError: Error { case invalidMessage, expired, scopeMismatch, keyUnavailable, hardwareUnavailable, cancelled, signatureFailed }

public struct ApprovalMessage {
    public let bytes: Data
    public let phase: String
    public let amount: String
    public let currency: String
    public let destination: String
    public var summary: String { "\(phase == "REVIEW" ? "Primera autorización" : "Segunda autorización")\n\(amount) \(currency)\nDestino: \(destination)" }
    private static func matches(_ text: String, _ pattern: String) -> Bool { text.range(of: pattern, options: .regularExpression) != nil }
    public static func parse(_ bytes: Data, audience: UUID, actor: Int64, credential: UUID, now: Int64 = Int64(Date().timeIntervalSince1970)) throws -> ApprovalMessage {
        guard bytes.count <= 1024, actor > 0, bytes.allSatisfy({ $0 < 128 }), let text = String(data: bytes, encoding: .ascii) else { throw ApprovalError.invalidMessage }
        let f = text.components(separatedBy: "\n")
        guard f.count == 15, f[14].isEmpty, f[0] == "SGACD-WALLET-APPROVAL-V1",
              f[1] == audience.uuidString.lowercased(), f[2] == String(actor), f[3] == credential.uuidString.lowercased() else { throw ApprovalError.scopeMismatch }
        for index in [1,3,4,5,9,10] { guard UUID(uuidString: f[index])?.uuidString.lowercased() == f[index] else { throw ApprovalError.invalidMessage } }
        guard ["REVIEW","EXECUTE"].contains(f[6]), matches(f[8], "^[0-9a-f]{64}$"), ["COP","USD","EUR"].contains(f[12]), f[9] != f[10],
              let nonce = Data(base64Encoded: f[7]), nonce.count == 32, nonce.base64EncodedString() == f[7],
              matches(f[11], "^(0|[1-9][0-9]{0,15})\\.[0-9]{2}$"), let amount = Decimal(string: f[11], locale: Locale(identifier: "en_US_POSIX")), amount > 0 else { throw ApprovalError.invalidMessage }
        let canonical = "{\"amount\":\"\(f[11])\",\"currency\":\"\(f[12])\",\"destination\":\"\(f[10])\",\"source\":\"\(f[9])\"}"
        let digest = SHA256.hash(data: Data(canonical.utf8)).map { String(format: "%02x", $0) }.joined()
        guard digest == f[8] else { throw ApprovalError.scopeMismatch }
        guard let expires = Int64(f[13]), String(expires) == f[13], expires > now, expires <= now + 180 else { throw ApprovalError.expired }
        return ApprovalMessage(bytes: bytes, phase: f[6], amount: f[11], currency: f[12], destination: f[10])
    }
}
