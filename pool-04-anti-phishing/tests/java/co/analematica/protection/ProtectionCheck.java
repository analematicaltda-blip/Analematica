package co.analematica.protection;
import java.net.URI;
import java.security.MessageDigest;
import java.security.GeneralSecurityException;
import java.util.Base64;
import java.util.Set;

/** CPU contract tests only, no live TLS endpoint or screenshot test. */
public final class ProtectionCheck {
    private static int checks;
    private static void expect(boolean value) {checks++;if(!value)throw new AssertionError("Protection regression");}
    private static String pin(byte[] bytes) throws Exception{return "sha256/"+Base64.getEncoder().encodeToString(MessageDigest.getInstance("SHA-256").digest(bytes));}
    public static void main(String[] args) throws Exception {
        byte[] active={1,2,3},backup={4,5,6};String a=pin(active),b=pin(backup);
        OriginPinPolicy policy=new OriginPinPolicy("wallet.example.test",Set.of(a,b),2000);
        for(String uri:new String[]{"https://wallet.example.test/api/v1/finance/wallet/","https://wallet.example.test:443/","https://wallet.example.test/?q=1"}){policy.requireOrigin(URI.create(uri),1000);expect(true);}
        for(String uri:new String[]{"http://wallet.example.test/","https://wallet.example.test.evil.test/","https://evil.test/wallet.example.test/","https://wallet.example.test@evil.test/","https://user@wallet.example.test/","https://wallet.example.test:8443/","https://wallet.example.test/#secret","https://WALLET.example.test/","https://wallet.example.test./","https://%77allet.example.test/","https://wallet.example.test:0443/","file:///wallet.example.test","//wallet.example.test/"}) {
            boolean rejected=false;try{policy.requireOrigin(URI.create(uri),1000);}catch(GeneralSecurityException expected){rejected=true;}expect(rejected);
        }
        expect(policy.acceptsSpki(active,1000));expect(policy.acceptsSpki(backup,1000));expect(!policy.acceptsSpki(new byte[]{9},1000));
        boolean rejected=false;try{policy.requireOrigin(URI.create("https://wallet.example.test/"),2000);}catch(GeneralSecurityException expected){rejected=true;}expect(rejected);
        rejected=false;try{policy.acceptsSpki(active,2000);}catch(GeneralSecurityException expected){rejected=true;}expect(rejected);
        int invalid=0;
        try{new OriginPinPolicy("wallet.example.test",Set.of(a),2000);}catch(IllegalArgumentException expected){invalid++;}
        try{new OriginPinPolicy("https://wallet.example.test",Set.of(a,b),2000);}catch(IllegalArgumentException expected){invalid++;}
        try{new OriginPinPolicy("wallet.example.test",Set.of(a,"sha256/wrong"),2000);}catch(IllegalArgumentException expected){invalid++;}
        try{new OriginPinPolicy("wallet.example.test",Set.of(a,b),0);}catch(IllegalArgumentException expected){invalid++;}
        expect(invalid==4);
        OriginPinPolicy current=new OriginPinPolicy("wallet.example.test",Set.of(a,b),System.currentTimeMillis()/1000+120);
        PinnedHttpsClient client=new PinnedHttpsClient(current);
        // All rejected BEFORE opening a connection; no test talks to a provider.
        rejected=false;try{client.request(URI.create("http://wallet.example.test/"),null,null);}catch(GeneralSecurityException expected){rejected=true;}expect(rejected);
        rejected=false;try{client.request(URI.create("https://wallet.example.test/"),new byte[65537],null);}catch(IllegalArgumentException expected){rejected=true;}expect(rejected);
        rejected=false;try{client.request(URI.create("https://wallet.example.test/"),null,"abc\r\nInjected: yes");}catch(IllegalArgumentException expected){rejected=true;}expect(rejected);
        java.net.CookieHandler previous=java.net.CookieHandler.getDefault();
        try {
            java.net.CookieHandler.setDefault(new java.net.CookieManager());rejected=false;
            try{client.request(URI.create("https://wallet.example.test/"),null,null);}catch(GeneralSecurityException expected){rejected=true;}expect(rejected);
        } finally {java.net.CookieHandler.setDefault(previous);}
        System.out.println("Network protection assertions passed: "+checks+". No live TLS or device claims.");
    }
}
