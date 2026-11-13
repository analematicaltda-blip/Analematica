package co.analematica.protection;
import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Bundle;
import java.security.GeneralSecurityException;
import java.util.Arrays;
import java.util.HashSet;

/** Signed host resources; never accepts a pin, domain or bypass from a method channel. */
public final class AndroidPinnedProfile {
    private AndroidPinnedProfile() {}
    public static PinnedHttpsClient fromApplication(Context context) throws GeneralSecurityException {
        try {
            Bundle config=context.getPackageManager().getApplicationInfo(context.getPackageName(),PackageManager.GET_META_DATA).metaData;
            if(config==null)throw new IllegalArgumentException();
            String host=config.getString("co.analematica.network.host"),pins=config.getString("co.analematica.network.pins"),expiry=config.getString("co.analematica.network.validUntil");
            if(pins==null || expiry==null || !expiry.matches("[1-9][0-9]{0,17}"))throw new IllegalArgumentException();
            OriginPinPolicy policy=new OriginPinPolicy(host,new HashSet<>(Arrays.asList(pins.split(",",-1))),Long.parseLong(expiry));
            policy.requireOrigin(java.net.URI.create("https://"+host+"/"),System.currentTimeMillis()/1000);
            return new PinnedHttpsClient(policy);
        } catch(Exception error) {throw new GeneralSecurityException("NETWORK_CONFIGURATION_REQUIRED");}
    }
}
