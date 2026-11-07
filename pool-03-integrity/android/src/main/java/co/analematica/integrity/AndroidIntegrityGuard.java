package co.analematica.integrity;

import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.os.Build;
import android.os.Debug;
import java.io.File;
import java.security.GeneralSecurityException;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.Set;

/** Read-only observations from Android APIs. No shell, network, key deletion or hook evasion. */
public final class AndroidIntegrityGuard {
    private final IntegrityPolicy policy;
    public AndroidIntegrityGuard(IntegrityPolicy policy) {
        if(policy==null)throw new IllegalArgumentException("INTEGRITY_CONFIGURATION_REQUIRED");
        this.policy=policy;
    }
    public Set<IntegrityPolicy.Finding> inspect(Context context) {
        try {
            String name=context.getPackageName();
            PackageInfo info=context.getPackageManager().getPackageInfo(name,PackageManager.GET_SIGNING_CERTIFICATES);
            if(info.signingInfo==null || info.applicationInfo==null)return Set.of(IntegrityPolicy.Finding.UNKNOWN);
            Signature[] signers=info.signingInfo.getApkContentsSigners();
            if(signers==null || signers.length==0 || signers.length>4)return Set.of(IntegrityPolicy.Finding.UNKNOWN);
            Set<String> pins=new HashSet<>();
            for(Signature signer:signers) {
                byte[] digest=MessageDigest.getInstance("SHA-256").digest(signer.toByteArray());
                StringBuilder pin=new StringBuilder();for(byte value:digest)pin.append(String.format(java.util.Locale.ROOT,"%02x",value&255));pins.add(pin.toString());
            }
            boolean root=Build.TAGS!=null && Build.TAGS.contains("test-keys");
            // Presence is a risk signal, not proof of root. No destructive response.
            for(String path:new String[]{"/system/bin/su","/system/xbin/su","/sbin/su","/data/adb/magisk"})root|=new File(path).exists();
            return policy.evaluate(new IntegrityPolicy.Observation(name,info.getLongVersionCode(),pins,
                (info.applicationInfo.flags & (ApplicationInfo.FLAG_DEBUGGABLE|ApplicationInfo.FLAG_TEST_ONLY))!=0,
                Debug.isDebuggerConnected() || Debug.waitingForDebugger(),root,true));
        } catch(Exception error) { return Set.of(IntegrityPolicy.Finding.UNKNOWN); }
    }
    public void requireSensitiveOperation(Context context) throws GeneralSecurityException {
        if(!inspect(context).isEmpty())throw new GeneralSecurityException("CLIENT_INTEGRITY_BLOCKED");
    }
}
