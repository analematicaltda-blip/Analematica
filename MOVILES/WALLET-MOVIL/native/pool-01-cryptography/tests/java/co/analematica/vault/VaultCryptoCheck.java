package co.analematica.vault;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.UUID;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/** Software keys below are public test vectors, never a native-provider fallback. */
public final class VaultCryptoCheck {
    private static int checks=0;
    private static final byte[] KEY=new byte[32];
    private static final String SCOPE=VaultEnvelope.context(new UUID(0,1),new UUID(0,2),new UUID(0,3));
    private static final String KEY_ID="public-test-vector";
    private static void expect(boolean condition) { checks++; if (!condition) throw new AssertionError("Crypto contract failed"); }
    private static byte[] seal(byte[] plaintext) throws Exception {
        byte[] nonce=new byte[12]; new SecureRandom().nextBytes(nonce);
        byte[] header=VaultEnvelope.header(1,SCOPE,KEY_ID,new byte[0],nonce,plaintext.length+16);
        Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE,new SecretKeySpec(KEY,"AES"),new GCMParameterSpec(128,nonce));
        cipher.updateAAD(header); return VaultEnvelope.join(header,cipher.doFinal(plaintext));
    }
    private static byte[] open(byte[] encrypted,String context,String keyId) throws Exception {
        VaultEnvelope.Parsed parsed=VaultEnvelope.parse(encrypted,1,context,keyId);
        Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE,new SecretKeySpec(KEY,"AES"),new GCMParameterSpec(128,parsed.nonce()));
        cipher.updateAAD(parsed.header()); return cipher.doFinal(parsed.ciphertext());
    }
    private static String hex(byte[] data) {
        StringBuilder result=new StringBuilder(); for(byte b:data) result.append(String.format("%02x",b&255)); return result.toString();
    }
    public static void main(String[] args) throws Exception {
        Cipher nist=Cipher.getInstance("AES/GCM/NoPadding");
        nist.init(Cipher.ENCRYPT_MODE,new SecretKeySpec(KEY,"AES"),new GCMParameterSpec(128,new byte[12]));
        expect(hex(nist.doFinal(new byte[16])).equals("cea7403d4d606b6e074ec5d3baf39d18d0d1c8a799996bf0265b98b5d48ab919"));
        byte[] document="public synthetic identity document".getBytes(StandardCharsets.UTF_8);
        byte[] encrypted=seal(document);
        expect(Arrays.equals(open(encrypted,SCOPE,KEY_ID),document));
        expect(!Arrays.equals(encrypted,seal(document)));
        expect(open(seal(new byte[0]),SCOPE,KEY_ID).length==0);
        for(int i=0;i<encrypted.length;i++) {
            byte[] changed=encrypted.clone(); changed[i]^=1;
            boolean rejected=false; try { open(changed,SCOPE,KEY_ID); } catch(java.security.GeneralSecurityException|IllegalArgumentException expected) { rejected=true; }
            expect(rejected);
        }
        for(int size:new int[]{0,1,8,30,encrypted.length-1}) {
            boolean rejected=false;try { open(Arrays.copyOf(encrypted,size),SCOPE,KEY_ID); } catch(Exception expected) { rejected=true; }expect(rejected);
        }
        boolean rejected=false;try { open(encrypted,SCOPE+"other",KEY_ID); }catch(IllegalArgumentException expected){rejected=true;}expect(rejected);
        rejected=false;try { open(encrypted,SCOPE,"other-key"); }catch(IllegalArgumentException expected){rejected=true;}expect(rejected);
        rejected=false;try { open(Arrays.copyOf(encrypted,encrypted.length+1),SCOPE,KEY_ID); }catch(IllegalArgumentException expected){rejected=true;}expect(rejected);
        rejected=false;try { VaultEnvelope.header(1,SCOPE,KEY_ID,new byte[0],new byte[12],VaultEnvelope.MAX_DOCUMENT+17); }catch(IllegalArgumentException expected){rejected=true;}expect(rejected);
        rejected=false;try { PasswordKdf.derive("123456".toCharArray(),new byte[16]); }catch(IllegalArgumentException expected){rejected=true;}expect(rejected);
        byte[] salt=new byte[16];for(int i=0;i<16;i++)salt[i]=(byte)i;
        byte[] derived=PasswordKdf.derive("integration-passphrase".toCharArray(),salt);
        Files.write(Path.of(args[0]),encrypted);Files.write(Path.of(args[1]),derived);
        Arrays.fill(derived,(byte)0);
        System.out.println("JVM cryptographic assertions passed: "+checks);
    }
}
