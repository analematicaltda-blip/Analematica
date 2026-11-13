package co.analematica.protection;
import java.net.URI;
import java.security.MessageDigest;
import java.security.GeneralSecurityException;
import java.util.Base64;
import java.util.Set;

/** Exact HTTPS origin and two independent SPKI pins. No default domains/pins. */
public final class OriginPinPolicy {
    private final String host;
    private final Set<String> pins;
    private final long validUntil;
    public OriginPinPolicy(String host,Set<String> pins,long validUntil) {
        if(host==null || host.length()>253 || !host.matches("[a-z0-9]+(?:[a-z0-9-]*[a-z0-9])?(?:\\.[a-z0-9]+(?:[a-z0-9-]*[a-z0-9])?)+") || pins==null || pins.size()<2 || pins.size()>4 || validUntil<=0)throw new IllegalArgumentException("NETWORK_POLICY_REQUIRED");
        for(String pin:pins) {
            try { if(pin==null || !pin.startsWith("sha256/") || !Base64.getEncoder().encodeToString(Base64.getDecoder().decode(pin.substring(7))).equals(pin.substring(7)) || Base64.getDecoder().decode(pin.substring(7)).length!=32)throw new IllegalArgumentException(); }
            catch(IllegalArgumentException error) { throw new IllegalArgumentException("INVALID_SPKI_PIN"); }
        }
        this.host=host;this.pins=Set.copyOf(pins);this.validUntil=validUntil;
    }
    public void requireOrigin(URI uri,long now) throws GeneralSecurityException {
        if(now>=validUntil)throw new GeneralSecurityException("NETWORK_POLICY_EXPIRED");
        String authority=uri==null?null:uri.getRawAuthority();
        if(uri==null || !"https".equals(uri.getScheme()) || !host.equals(uri.getHost()) || uri.getRawUserInfo()!=null || uri.getRawFragment()!=null || !(host.equals(authority) || (host+":443").equals(authority)) || uri.toString().chars().anyMatch(c->c<=32 || c>=127 || c=='\\'))throw new GeneralSecurityException("UNAPPROVED_ORIGIN");
    }
    public boolean acceptsSpki(byte[] spki,long now) throws GeneralSecurityException {
        if(now>=validUntil)throw new GeneralSecurityException("NETWORK_POLICY_EXPIRED");
        return pins.contains("sha256/"+Base64.getEncoder().encodeToString(MessageDigest.getInstance("SHA-256").digest(spki)));
    }
}
