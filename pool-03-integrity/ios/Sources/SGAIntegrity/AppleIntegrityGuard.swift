import Foundation
import Darwin

/// Read-only signals; distribution signature enforcement remains the responsibility
/// of iOS. Bundle metadata alone does not verify a signing team or app integrity.
public final class AppleIntegrityGuard {
    private let policy: IntegrityPolicy
    public init(policy: IntegrityPolicy) { self.policy=policy }
    public func inspect() -> Set<IntegrityFinding> {
        #if os(iOS) && !targetEnvironment(simulator)
        let supported=true
        #else
        let supported=false
        #endif
        #if DEBUG
        let debugBuild=true
        #else
        let debugBuild=_isDebugAssertConfiguration()
        #endif
        var info=kinfo_proc()
        var size=MemoryLayout<kinfo_proc>.stride
        var mib: [Int32]=[CTL_KERN, KERN_PROC, KERN_PROC_PID, getpid()]
        let status=mib.withUnsafeMutableBufferPointer { sysctl($0.baseAddress, u_int($0.count), &info, &size, nil, 0) }
        let traced=status == 0 && (info.kp_proc.p_flag & P_TRACED) != 0
        var jailbreak=false
        #if os(iOS)
        for path in ["/Applications/Cydia.app", "/Library/MobileSubstrate/MobileSubstrate.dylib", "/usr/sbin/sshd", "/bin/bash", "/var/jb"] {
            jailbreak = FileManager.default.fileExists(atPath: path) || jailbreak
        }
        #endif
        let raw=Bundle.main.object(forInfoDictionaryKey: "CFBundleVersion") as? String
        let version=raw.flatMap(Int64.init)
        return policy.evaluate(IntegrityObservation(bundleID: Bundle.main.bundleIdentifier, version: version,
            debugBuild: debugBuild, debugger: traced, jailbreakSignal: jailbreak, supported: supported, complete: status == 0))
    }
    public func requireSensitiveOperation() throws {
        guard inspect().isEmpty else { throw IntegrityError.sensitiveOperationBlocked }
    }
}
