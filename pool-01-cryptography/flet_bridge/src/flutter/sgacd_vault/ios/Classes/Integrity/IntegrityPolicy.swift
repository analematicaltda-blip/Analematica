import Foundation

public enum IntegrityFinding: String, Hashable { case identity, version, debugBuild, debugger, jailbreakSignal, unsupportedPlatform, unknown }
public enum IntegrityError: Error { case configurationRequired, sensitiveOperationBlocked }

/// Local evidence only. It cannot establish Apple's remote attestation or KYC.
public struct IntegrityObservation {
    public let bundleID: String?
    public let version: Int64?
    public let debugBuild, debugger, jailbreakSignal, supported, complete: Bool
    public init(bundleID: String?, version: Int64?, debugBuild: Bool, debugger: Bool, jailbreakSignal: Bool, supported: Bool, complete: Bool) {
        self.bundleID=bundleID; self.version=version; self.debugBuild=debugBuild; self.debugger=debugger
        self.jailbreakSignal=jailbreakSignal; self.supported=supported; self.complete=complete
    }
}
public struct IntegrityPolicy {
    private let expectedBundle: String
    private let minimumVersion: Int64
    public init(expectedBundle: String, minimumVersion: Int64) throws {
        guard expectedBundle.range(of: "^[A-Za-z][A-Za-z0-9_-]*(\\.[A-Za-z][A-Za-z0-9_-]*)+$", options: .regularExpression) != nil, minimumVersion > 0 else { throw IntegrityError.configurationRequired }
        self.expectedBundle=expectedBundle; self.minimumVersion=minimumVersion
    }
    public func evaluate(_ observation: IntegrityObservation?) -> Set<IntegrityFinding> {
        guard let o=observation else { return [.unknown] }
        var findings=Set<IntegrityFinding>()
        if !o.complete { findings.insert(.unknown) }
        if o.bundleID != expectedBundle { findings.insert(.identity) }
        if let version=o.version { if version < minimumVersion { findings.insert(.version) } } else { findings.insert(.version) }
        if o.debugBuild { findings.insert(.debugBuild) }
        if o.debugger { findings.insert(.debugger) }
        if o.jailbreakSignal { findings.insert(.jailbreakSignal) }
        if !o.supported { findings.insert(.unsupportedPlatform) }
        return findings
    }
}
