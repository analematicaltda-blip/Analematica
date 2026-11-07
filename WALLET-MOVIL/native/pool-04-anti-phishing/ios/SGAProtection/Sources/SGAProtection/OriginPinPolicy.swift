import Foundation
import CryptoKit
public enum NetworkProtectionError: Error { case configurationRequired, rejected }
public struct OriginPinPolicy {
    private let host: String
    private let pins: Set<String>
    private let validUntil: Int64
    public init(host: String, pins: Set<String>, validUntil: Int64) throws {
        guard host.count <= 253, host.utf8.allSatisfy({ $0 > 32 && $0 < 127 }), host.range(of: "^[a-z0-9]+(?:[a-z0-9-]*[a-z0-9])?(?:\\.[a-z0-9]+(?:[a-z0-9-]*[a-z0-9])?)+$",options: .regularExpression) != nil,
              pins.count >= 2, pins.count <= 4, validUntil > 0 else { throw NetworkProtectionError.configurationRequired }
        for pin in pins {
            guard pin.hasPrefix("sha256/"), let bytes=Data(base64Encoded: String(pin.dropFirst(7))), bytes.count == 32,
                  "sha256/"+bytes.base64EncodedString() == pin else { throw NetworkProtectionError.configurationRequired }
        }
        self.host=host; self.pins=pins; self.validUntil=validUntil
    }
    public func requireOrigin(_ url: URL, now: Int64 = Int64(Date().timeIntervalSince1970)) throws {
        let raw=url.absoluteString
        guard now < validUntil, raw.utf8.allSatisfy({ $0 > 32 && $0 < 127 && $0 != 92 }),
              let parts=URLComponents(string: raw), parts.scheme == "https", parts.host == host, parts.user == nil, parts.password == nil, parts.fragment == nil,
              let range=raw.range(of: "://") else { throw NetworkProtectionError.rejected }
        let authority=raw[range.upperBound...].prefix { $0 != "/" && $0 != "?" && $0 != "#" }
        guard authority == host || authority == host+":443" else { throw NetworkProtectionError.rejected }
    }
    public func acceptsSPKI(_ bytes: Data, now: Int64 = Int64(Date().timeIntervalSince1970)) throws -> Bool {
        guard now < validUntil else { throw NetworkProtectionError.rejected }
        return pins.contains("sha256/"+Data(SHA256.hash(data: bytes)).base64EncodedString())
    }
}
