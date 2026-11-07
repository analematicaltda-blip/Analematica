import XCTest
@testable import SGAIntegrity

final class PolicyTests: XCTestCase {
    func sample(bundle: String? = "co.analematica.wallet", version: Int64? = 10, debug: Bool = false, debugger: Bool = false, jailbreak: Bool = false, supported: Bool = true, complete: Bool = true) -> IntegrityObservation {
        IntegrityObservation(bundleID: bundle, version: version, debugBuild: debug, debugger: debugger, jailbreakSignal: jailbreak, supported: supported, complete: complete)
    }
    func testAllowedLocalPolicyIsNotAttestation() throws {
        let policy=try IntegrityPolicy(expectedBundle: "co.analematica.wallet", minimumVersion: 10)
        XCTAssertTrue(policy.evaluate(sample()).isEmpty)
        XCTAssertTrue(policy.evaluate(sample(version: 11)).isEmpty)
    }
    func testRiskUnknownAndOtherIdentityBlock() throws {
        let policy=try IntegrityPolicy(expectedBundle: "co.analematica.wallet", minimumVersion: 10)
        XCTAssertEqual(policy.evaluate(nil), [.unknown])
        XCTAssertEqual(policy.evaluate(sample(bundle: "co.other.wallet")), [.identity])
        XCTAssertEqual(policy.evaluate(sample(bundle: nil)), [.identity])
        XCTAssertEqual(policy.evaluate(sample(version: nil)), [.version])
        XCTAssertEqual(policy.evaluate(sample(version: 9)), [.version])
        XCTAssertEqual(policy.evaluate(sample(debug: true)), [.debugBuild])
        XCTAssertEqual(policy.evaluate(sample(debugger: true)), [.debugger])
        XCTAssertEqual(policy.evaluate(sample(jailbreak: true)), [.jailbreakSignal])
        XCTAssertEqual(policy.evaluate(sample(supported: false)), [.unsupportedPlatform])
        XCTAssertEqual(policy.evaluate(sample(complete: false)), [.unknown])
        XCTAssertEqual(policy.evaluate(sample(bundle: nil, version: nil, debug: true, debugger: true, jailbreak: true, supported: false, complete: false)).count, 7)
    }
    func testConfigurationRequired() {
        XCTAssertThrowsError(try IntegrityPolicy(expectedBundle: "", minimumVersion: 1))
        XCTAssertThrowsError(try IntegrityPolicy(expectedBundle: "co.test", minimumVersion: 0))
    }
    func testHostCollectorCannotAuthorizeMacOrSimulator() throws {
        let policy=try IntegrityPolicy(expectedBundle: "co.analematica.wallet", minimumVersion: 10)
        #if !os(iOS) || targetEnvironment(simulator)
        XCTAssertTrue(AppleIntegrityGuard(policy: policy).inspect().contains(.unsupportedPlatform))
        XCTAssertThrowsError(try AppleIntegrityGuard(policy: policy).requireSensitiveOperation())
        #endif
    }
}
