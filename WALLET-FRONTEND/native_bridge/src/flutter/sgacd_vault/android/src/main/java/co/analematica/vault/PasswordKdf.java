package co.analematica.vault;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.security.GeneralSecurityException;

/** Optional passphrase KDF. Never used as a software fallback for hardware keys. */
public final class PasswordKdf {
    private PasswordKdf() {}
    public static final int ITERATIONS = 600_000;
    public static byte[] derive(char[] passphrase, byte[] salt) throws GeneralSecurityException {
        // A short PIN cannot provide offline security, regardless of the KDF.
        if (passphrase == null || passphrase.length < 12 || passphrase.length > 1024 || salt == null || salt.length != 16)
            throw new IllegalArgumentException("A long passphrase and a random 16-byte salt are required");
        PBEKeySpec spec = new PBEKeySpec(passphrase, salt, ITERATIONS, 256);
        try { return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded(); }
        finally { spec.clearPassword(); }
    }
}
