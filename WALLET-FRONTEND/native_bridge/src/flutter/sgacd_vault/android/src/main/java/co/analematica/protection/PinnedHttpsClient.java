package co.analematica.protection;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.URI;
import java.security.KeyStore;
import java.security.GeneralSecurityException;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;

/** TLS system trust + SPKI pin inside handshake, before HTTP headers/body leave.
 * Dedicated bounded JSON requests only. Redirects and HTTP errors fail closed.
 */
public final class PinnedHttpsClient {
    private final OriginPinPolicy policy;
    private final SSLContext tls;
    public PinnedHttpsClient(OriginPinPolicy policy) throws GeneralSecurityException {
        if(policy==null)throw new IllegalArgumentException("NETWORK_POLICY_REQUIRED");this.policy=policy;
        TrustManagerFactory factory=TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());factory.init((KeyStore)null);
        X509TrustManager system=null;for(TrustManager manager:factory.getTrustManagers())if(manager instanceof X509TrustManager)system=(X509TrustManager)manager;
        if(system==null)throw new GeneralSecurityException("SYSTEM_TLS_UNAVAILABLE");
        final X509TrustManager trusted=system;
        X509TrustManager pinned=new X509TrustManager() {
            public X509Certificate[] getAcceptedIssuers(){return trusted.getAcceptedIssuers();}
            public void checkClientTrusted(X509Certificate[] chain,String authType) throws CertificateException {throw new CertificateException("CLIENT_CERT_UNSUPPORTED");}
            public void checkServerTrusted(X509Certificate[] chain,String authType) throws CertificateException {
                trusted.checkServerTrusted(chain,authType); // Never replace PKI validation with a pin.
                try {
                    if(chain==null || chain.length==0 || chain.length>10)throw new GeneralSecurityException();
                    for(X509Certificate cert:chain)if(policy.acceptsSpki(cert.getPublicKey().getEncoded(),System.currentTimeMillis()/1000))return;
                } catch(GeneralSecurityException error){throw new CertificateException("TLS_PIN_REJECTED");}
                throw new CertificateException("TLS_PIN_REJECTED");
            }
        };
        tls=SSLContext.getInstance("TLSv1.2");tls.init(null,new TrustManager[]{pinned},null);
    }
    public byte[] request(URI uri,byte[] json,String bearer) throws Exception {
        policy.requireOrigin(uri,System.currentTimeMillis()/1000);
        if(java.net.CookieHandler.getDefault()!=null || java.net.Authenticator.getDefault()!=null)throw new GeneralSecurityException("GLOBAL_CREDENTIAL_HANDLER_UNSUPPORTED");
        if(json!=null && json.length>65536)throw new IllegalArgumentException("REQUEST_LIMIT");
        if(bearer!=null && (bearer.isEmpty() || bearer.length()>4096 || !bearer.matches("[A-Za-z0-9._~+/-]+=*")))throw new IllegalArgumentException("INVALID_TOKEN");
        HttpsURLConnection connection=(HttpsURLConnection)uri.toURL().openConnection();
        connection.setSSLSocketFactory(tls.getSocketFactory());
        connection.setHostnameVerifier(HttpsURLConnection.getDefaultHostnameVerifier());
        connection.setInstanceFollowRedirects(false);connection.setConnectTimeout(10000);connection.setReadTimeout(10000);connection.setUseCaches(false);
        connection.setRequestMethod(json==null?"GET":"POST");connection.setRequestProperty("Accept","application/json");connection.setRequestProperty("Cache-Control","no-store");
        if(bearer!=null)connection.setRequestProperty("Authorization","Bearer "+bearer);
        try {
            if(json!=null){connection.setDoOutput(true);connection.setFixedLengthStreamingMode(json.length);connection.setRequestProperty("Content-Type","application/json");try(java.io.OutputStream output=connection.getOutputStream()){output.write(json);}}
            int status=connection.getResponseCode();if(status<200 || status>=300)throw new GeneralSecurityException("HTTP_RESPONSE_REJECTED");
            try(InputStream input=connection.getInputStream();ByteArrayOutputStream bytes=new ByteArrayOutputStream()) {
                byte[] buffer=new byte[8192];int count;
                while((count=input.read(buffer))!=-1){if(bytes.size()+count>1048576)throw new GeneralSecurityException("RESPONSE_LIMIT");bytes.write(buffer,0,count);}
                policy.requireOrigin(uri,System.currentTimeMillis()/1000);return bytes.toByteArray();
            }
        } finally {connection.disconnect();}
    }
}
