import XCTest
import CryptoKit
@testable import SGAApproval

final class MessageTests: XCTestCase {
    let audience = UUID(uuidString: "00000000-0000-0000-0000-000000000001")!
    let credential = UUID(uuidString: "00000000-0000-0000-0000-000000000002")!
    func message() -> Data {
        var fields = ["SGACD-WALLET-APPROVAL-V1",audience.uuidString.lowercased(),"7",credential.uuidString.lowercased(),UUID().uuidString.lowercased(),UUID().uuidString.lowercased(),"REVIEW",Data(repeating: 0,count: 32).base64EncodedString(),String(repeating: "0",count: 64),UUID().uuidString.lowercased(),UUID().uuidString.lowercased(),"10.00","COP","1120"]
        let canonical = "{\"amount\":\"10.00\",\"currency\":\"COP\",\"destination\":\"\(fields[10])\",\"source\":\"\(fields[9])\"}"
        fields[8] = SHA256.hash(data: Data(canonical.utf8)).map { String(format: "%02x", $0) }.joined()
        return Data((fields.joined(separator: "\n") + "\n").utf8)
    }
    func testBoundSummary() throws {
        let result = try ApprovalMessage.parse(message(),audience: audience,actor: 7,credential: credential,now: 1000)
        XCTAssertEqual(result.amount,"10.00");XCTAssertEqual(result.phase,"REVIEW")
        XCTAssertTrue(result.summary.contains(result.destination))
    }
    func testForeignActorDeviceAndExpiryAreRejected() throws {
        let bytes = message()
        XCTAssertThrowsError(try ApprovalMessage.parse(bytes,audience: audience,actor: 8,credential: credential,now: 1000))
        XCTAssertThrowsError(try ApprovalMessage.parse(bytes,audience: UUID(),actor: 7,credential: credential,now: 1000))
        XCTAssertThrowsError(try ApprovalMessage.parse(bytes,audience: audience,actor: 7,credential: UUID(),now: 1000))
        XCTAssertThrowsError(try ApprovalMessage.parse(bytes,audience: audience,actor: 7,credential: credential,now: 1120))
    }
    func testNoDocumentOrArbitraryMessageSigning() throws {
        for bytes in [Data("hello".utf8),message()+Data([10]),Data(repeating: 0,count: 1025)] {
            XCTAssertThrowsError(try ApprovalMessage.parse(bytes,audience: audience,actor: 7,credential: credential,now: 1000))
        }
    }
}
