package co.analematica.protection;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.net.URI;
import java.security.KeyStore;
import java.security.cert.CertificateFactory;
import java.util.Set;

/** Local fixture CA only; never a production trust-store configuration. */
public final class LocalTLSCheck {
    public static void main(String[] args) throws Exception {
        if(args[0].equals("store")) {
            KeyStore store=KeyStore.getInstance("PKCS12");store.load(null,"fixture-only".toCharArray());
            try(InputStream input=Files.newInputStream(Path.of(args[1]))) {store.setCertificateEntry("fixture-ca",CertificateFactory.getInstance("X.509").generateCertificate(input));}
            try(OutputStream output=Files.newOutputStream(Path.of(args[2]))) {store.store(output,"fixture-only".toCharArray());}return;
        }
        OriginPinPolicy policy=new OriginPinPolicy("127.0.0.1",Set.of(args[2],args[3]),System.currentTimeMillis()/1000+60);
        PinnedHttpsClient client=new PinnedHttpsClient(policy);
        boolean rejected=false;
        try {
            byte[] reply=client.request(URI.create("https://127.0.0.1"+args[4]),"{}".getBytes(java.nio.charset.StandardCharsets.US_ASCII),"fixture-token");
            if(args[1].equals("pass") && !new String(reply,java.nio.charset.StandardCharsets.US_ASCII).equals("verified"))throw new AssertionError("Response mismatch");
        } catch(Exception expected) {rejected=true;}
        if(rejected != args[1].equals("reject"))throw new AssertionError("TLS acceptance regression: "+args[5]);
    }
}
