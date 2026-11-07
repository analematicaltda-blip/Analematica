import XCTest
import CryptoKit
import Security
@testable import SGAProtection
final class ProtectionTests: XCTestCase {
    private func pin(_ bytes: Data) -> String { "sha256/"+Data(SHA256.hash(data: bytes)).base64EncodedString() }
    func testOriginSubstitutionExpiryAndBackupPin() throws {
        let a=Data([1,2,3]),b=Data([4,5,6])
        let policy=try OriginPinPolicy(host: "wallet.example.test",pins: [pin(a),pin(b)],validUntil: 2000)
        try policy.requireOrigin(URL(string: "https://wallet.example.test/")!,now: 1000)
        try policy.requireOrigin(URL(string: "https://wallet.example.test:443/")!,now: 1000)
        for text in ["http://wallet.example.test/","https://wallet.example.test.evil.test/","https://user@wallet.example.test/","https://wallet.example.test:8443/","https://wallet.example.test/#secret","https://wallet.example.test./","https://%77allet.example.test/","https://WALLET.example.test/"] {
            XCTAssertThrowsError(try policy.requireOrigin(URL(string: text)!,now: 1000))
        }
        XCTAssertTrue(try policy.acceptsSPKI(a,now: 1000)); XCTAssertTrue(try policy.acceptsSPKI(b,now: 1000))
        XCTAssertFalse(try policy.acceptsSPKI(Data([9]),now: 1000))
        XCTAssertThrowsError(try policy.requireOrigin(URL(string: "https://wallet.example.test/")!,now: 2000))
        XCTAssertThrowsError(try policy.acceptsSPKI(a,now: 2000))
        XCTAssertThrowsError(try OriginPinPolicy(host: "wallet.example.test",pins: [pin(a)],validUntil: 2000))
    }
    func testSPKIEncodingsMatchIndependentPythonVectors() throws {
        do {
            // Public synthetic key only; expected DER produced independently by Python.
            let raw=Data(base64Encoded: "BGsX0fLhLEJH+Lzm5WOkQPJ3A32BLeszoPShOUXYmMKWT+NC4v4af5uO5+tKfA+eFivOM1drMV7Oy7ZAaDe/UfU=")!
            let expected=Data(base64Encoded: "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEaxfR8uEsQkf4vOblY6RA8ncDfYEt6zOg9KE5RdiYwpZP40Li/hp/m47n60p8D54WK84zV2sxXs7LtkBoN79R9Q==")!
            let attrs: [String:Any]=[kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom, kSecAttrKeyClass as String: kSecAttrKeyClassPublic]
            let key=try XCTUnwrap(SecKeyCreateWithData(raw as CFData,attrs as CFDictionary,nil))
            XCTAssertEqual(SPKIEncoding.encode(key),expected)
        }
        do {
            // Public synthetic key only; expected DER produced independently by Python.
            let raw=Data(base64Encoded: "MIIBCgKCAQEAxaPJveVALpMYWX78n3rwjPaWmB7SmUlnjOvit4pbHqG/W5IIUmm0ttRJAZRt5E4rxmWIlNme3iub3uZ7NBedL2Z5+NdDjrqlt9PIVnZsV5huUW2v44+Py+onL31qMKYJUHG2oSSMTxR+/JS7K1zVeN533j4GkecLK05BuKHvJtFuTcmeSYWVekF7LC+qS1CzHz72M7IRNCBhwWAfG0oQVNYIfP85ffcYEiis489tnqjEhYS70sf+ROuVoGZJcL83hyonW/AfwVH34PSLOisbV0o1OSsYDwpbAmjh8UY3Dp2R6cS5SwYLZ36zHl0sVTER1VmGBFLilFV4WelGT5YPUQIDAQAB")!
            let expected=Data(base64Encoded: "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxaPJveVALpMYWX78n3rwjPaWmB7SmUlnjOvit4pbHqG/W5IIUmm0ttRJAZRt5E4rxmWIlNme3iub3uZ7NBedL2Z5+NdDjrqlt9PIVnZsV5huUW2v44+Py+onL31qMKYJUHG2oSSMTxR+/JS7K1zVeN533j4GkecLK05BuKHvJtFuTcmeSYWVekF7LC+qS1CzHz72M7IRNCBhwWAfG0oQVNYIfP85ffcYEiis489tnqjEhYS70sf+ROuVoGZJcL83hyonW/AfwVH34PSLOisbV0o1OSsYDwpbAmjh8UY3Dp2R6cS5SwYLZ36zHl0sVTER1VmGBFLilFV4WelGT5YPUQIDAQAB")!
            let attrs: [String:Any]=[kSecAttrKeyType as String: kSecAttrKeyTypeRSA, kSecAttrKeyClass as String: kSecAttrKeyClassPublic]
            let key=try XCTUnwrap(SecKeyCreateWithData(raw as CFData,attrs as CFDictionary,nil))
            XCTAssertEqual(SPKIEncoding.encode(key),expected)
        }
    }
    func testHeaderNewlinesRejectedSynchronously() throws {
        let policy=try OriginPinPolicy(host: "127.0.0.1",pins: [pin(Data([1])),pin(Data([2]))],validUntil: Int64(Date().timeIntervalSince1970)+60)
        for token in ["fixture\n","fixture\r\nInjected: yes"] {
            var completed=false
            PinnedHTTPSClient(policy: policy).request(URL(string: "https://127.0.0.1/")!,bearer: token) { result in
                completed=true
                if case .success = result { XCTFail("Header injection accepted") }
            }
            XCTAssertTrue(completed)
        }
    }
    func testMacCannotPretendToProtectAnIPhoneDisplay() {
        #if !canImport(UIKit)
        XCTAssertThrowsError(try AppleSensitiveScreen.requireSensitiveDisplay())
        #endif
    }
}
