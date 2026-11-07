package co.analematica.approval;

import java.nio.charset.StandardCharsets;
import java.math.BigDecimal;
import java.util.Arrays;
import java.util.Base64;
import java.util.UUID;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/** A signing operation cannot be used as an arbitrary-message or cross-service oracle. */
public final class ApprovalMessage {
    private final byte[] bytes;
    public final String phase,amount,currency,destination;
    private ApprovalMessage(byte[] bytes,String[] fields) { this.bytes=bytes.clone();phase=fields[6];amount=fields[11];currency=fields[12];destination=fields[10]; }
    private static String uuid(String value) {
        String canonical=UUID.fromString(value).toString();if(!canonical.equals(value))throw new IllegalArgumentException("INVALID_APPROVAL");return canonical;
    }
    public static ApprovalMessage parse(byte[] bytes,UUID audience,long actor,UUID credential,long nowSeconds) {
        if(bytes==null || bytes.length>1024 || actor<1 || audience==null || credential==null)throw new IllegalArgumentException("INVALID_APPROVAL");
        for(byte value:bytes)if(value<0)throw new IllegalArgumentException("INVALID_APPROVAL");
        String[] f=new String(bytes,StandardCharsets.US_ASCII).split("\n",-1);
        if(f.length!=15 || !f[14].isEmpty() || !f[0].equals("SGACD-WALLET-APPROVAL-V1") || !f[1].equals(audience.toString()) || !f[2].equals(Long.toString(actor)) || !f[3].equals(credential.toString()))throw new IllegalArgumentException("APPROVAL_SCOPE_MISMATCH");
        for(int index:new int[]{1,3,4,5,9,10})uuid(f[index]);
        if(!Arrays.asList("REVIEW","EXECUTE").contains(f[6]) || !f[8].matches("[0-9a-f]{64}") || !Arrays.asList("COP","USD","EUR").contains(f[12]) || f[9].equals(f[10]))throw new IllegalArgumentException("INVALID_APPROVAL");
        byte[] nonce=Base64.getDecoder().decode(f[7]);
        if(nonce.length!=32 || !Base64.getEncoder().encodeToString(nonce).equals(f[7]))throw new IllegalArgumentException("INVALID_APPROVAL_NONCE");
        if(!f[11].matches("[0-9]{1,16}\\.[0-9]{2}"))throw new IllegalArgumentException("INVALID_APPROVAL_AMOUNT");
        BigDecimal amount=new BigDecimal(f[11]);
        if(amount.signum()<=0 || !amount.toPlainString().equals(f[11]))throw new IllegalArgumentException("INVALID_APPROVAL_AMOUNT");
        String canonical="{\"amount\":\""+f[11]+"\",\"currency\":\""+f[12]+"\",\"destination\":\""+f[10]+"\",\"source\":\""+f[9]+"\"}";
        try {
            byte[] digest=MessageDigest.getInstance("SHA-256").digest(canonical.getBytes(StandardCharsets.US_ASCII));
            StringBuilder hex=new StringBuilder();for(byte value:digest)hex.append(String.format(java.util.Locale.ROOT,"%02x",value&255));
            if(!hex.toString().equals(f[8]))throw new IllegalArgumentException("APPROVAL_DIGEST_MISMATCH");
        } catch(NoSuchAlgorithmException exception) { throw new IllegalStateException("CRYPTO_UNAVAILABLE"); }
        long expires=Long.parseLong(f[13]);
        if(!Long.toString(expires).equals(f[13]) || expires<=nowSeconds || expires>nowSeconds+180)throw new IllegalArgumentException("APPROVAL_EXPIRED_OR_CLOCK_INVALID");
        return new ApprovalMessage(bytes,f);
    }
    public byte[] bytes() { return bytes.clone(); }
    public String summary() { return (phase.equals("REVIEW")?"Primera autorización":"Segunda autorización")+"\n"+amount+" "+currency+"\nDestino: "+destination; }
}
