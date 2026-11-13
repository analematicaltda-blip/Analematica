import XCTest
import SGAIntegrity
import CryptoKit
@testable import SGAVault

final class CryptoTests: XCTestCase {
    let scope = DocumentScope(tenant: UUID(uuidString: "00000000-0000-0000-0000-000000000001")!, account: UUID(uuidString: "00000000-0000-0000-0000-000000000002")!)
    let document = UUID(uuidString: "00000000-0000-0000-0000-000000000003")!
    let key = SymmetricKey(data: Data(repeating: 0, count: 32)) // Public test vector only.
    func testNISTVector() throws {
        let box = try AES.GCM.seal(Data(repeating: 0, count: 16), using: key, nonce: AES.GCM.Nonce(data: Data(repeating: 0, count: 12)))
        XCTAssertEqual((box.ciphertext + box.tag).map { String(format: "%02x", $0) }.joined(), "cea7403d4d606b6e074ec5d3baf39d18d0d1c8a799996bf0265b98b5d48ab919")
    }
    func testRoundTripAndEveryByteTampering() throws {
        let context = scope.context(document: document), keyID = try scope.keyID(version: 1)
        let plaintext = Data("public test document".utf8)
        let encoded = try DocumentAEAD.seal(plaintext, key: key, context: context, keyID: keyID, wrapped: Data([1,2,3]))
        XCTAssertEqual(try DocumentAEAD.open(Envelope.parse(encoded, platform: 2, context: context, keyID: keyID), key: key), plaintext)
        for index in encoded.indices {
            var changed = encoded; changed[index] ^= 1
            XCTAssertThrowsError(try DocumentAEAD.open(Envelope.parse(changed, platform: 2, context: context, keyID: keyID), key: key))
        }
        XCTAssertThrowsError(try Envelope.parse(encoded, platform: 2, context: scope.context(document: UUID()), keyID: keyID))
        XCTAssertThrowsError(try Envelope.parse(encoded + Data([0]), platform: 2, context: context, keyID: keyID))
    }
    func testTruncationAndSizeLimits() throws {
        for size in [0,1,8,30] { XCTAssertThrowsError(try Envelope.parse(Data(repeating: 0, count: size), platform: 2, context: "test", keyID: "test")) }
        XCTAssertThrowsError(try Envelope.header(platform: 2, context: "test", keyID: "test", wrapped: Data([1]), nonce: Data(count: 12), size: Envelope.maximum + 17))
    }
    func testPINRejectedAndPBKDF2Vector() throws {
        XCTAssertThrowsError(try PasswordKdf.derive("123456", salt: Data(count: 16)))
        let derived = try PasswordKdf.derive("integration-passphrase", salt: Data((0..<16).map { UInt8($0) }))
        // Verified independently by Python hashlib and JCE; no production secret.
        XCTAssertEqual(derived.map { String(format: "%02x", $0) }.joined(), "1a27e935f1ae1eb7b46bdf4b5face82298b486be835f0de094f033915031f174")
    }
    func testNoSilentHardwareFallback() throws {
        guard !SecureEnclave.isAvailable else { throw XCTSkip("Unavailable-hardware contract requires a host without Secure Enclave; physical biometric tests are separate") }
        XCTAssertThrowsError(try SecureEnclaveVault(scope: scope, keyVersion: 1, integrity: AppleIntegrityGuard(policy: try IntegrityPolicy(expectedBundle: "co.analematica.vault", minimumVersion: 1))).createKey())
        // Physical biometric approval/cancellation must be tested on a real device.
    }
}
