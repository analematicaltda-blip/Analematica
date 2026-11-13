package co.analematica.integrity;

import java.util.HashSet;
import java.util.Set;

/** Local risk gate only. An allowed decision is NOT remote hardware attestation. */
public final class IntegrityPolicy {
    public enum Finding { IDENTITY, SIGNER, VERSION, DEBUG_BUILD, DEBUGGER, ROOT_SIGNAL, UNKNOWN }
    public static final class Observation {
        public final String packageName;
        public final long version;
        public final Set<String> signerDigests;
        public final boolean debugBuild, debugger, rootSignal, complete;
        public Observation(String packageName,long version,Set<String> signerDigests,boolean debugBuild,boolean debugger,boolean rootSignal,boolean complete) {
            this.packageName=packageName;this.version=version;
            this.signerDigests=signerDigests==null?Set.of():Set.copyOf(signerDigests);
            this.debugBuild=debugBuild;this.debugger=debugger;this.rootSignal=rootSignal;this.complete=complete;
        }
    }
    private final String expectedPackage;
    private final Set<String> allowedSigners;
    private final long minimumVersion;
    public IntegrityPolicy(String expectedPackage,Set<String> allowedSigners,long minimumVersion) {
        if(expectedPackage==null || !expectedPackage.matches("[A-Za-z][A-Za-z0-9_]*(\\.[A-Za-z][A-Za-z0-9_]*)+") || minimumVersion<1 || allowedSigners==null || allowedSigners.isEmpty() || allowedSigners.size()>4)
            throw new IllegalArgumentException("INTEGRITY_CONFIGURATION_REQUIRED");
        for(String pin:allowedSigners)if(pin==null || !pin.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("INVALID_SIGNER_PIN");
        this.expectedPackage=expectedPackage;this.allowedSigners=Set.copyOf(allowedSigners);this.minimumVersion=minimumVersion;
    }
    public Set<Finding> evaluate(Observation observation) {
        if(observation==null)return Set.of(Finding.UNKNOWN);
        Set<Finding> findings=new HashSet<>();
        if(!observation.complete)findings.add(Finding.UNKNOWN);
        if(!expectedPackage.equals(observation.packageName))findings.add(Finding.IDENTITY);
        if(observation.signerDigests.isEmpty() || !allowedSigners.containsAll(observation.signerDigests))findings.add(Finding.SIGNER);
        if(observation.version<minimumVersion)findings.add(Finding.VERSION);
        if(observation.debugBuild)findings.add(Finding.DEBUG_BUILD);
        if(observation.debugger)findings.add(Finding.DEBUGGER);
        if(observation.rootSignal)findings.add(Finding.ROOT_SIGNAL);
        return Set.copyOf(findings);
    }
}
