package co.analematica.vault;

import android.app.Activity;
import co.analematica.protection.AndroidSensitiveScreen;
import co.analematica.integrity.AndroidIntegrityGuard;
import android.app.KeyguardManager;
import android.content.Context;
import android.hardware.biometrics.BiometricManager;
import android.hardware.biometrics.BiometricPrompt;
import android.os.CancellationSignal;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyInfo;
import android.security.keystore.KeyProperties;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.channels.FileLock;
import java.nio.channels.OverlappingFileLockException;
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.UUID;
import java.util.concurrent.Executor;
import java.util.concurrent.atomic.AtomicBoolean;

/** Android 12+: no software-key fallback; biometric authorization is per operation. */
public final class AndroidDocumentVault {
    public enum HardwarePolicy { STRONGBOX_REQUIRED, TRUSTED_HARDWARE }
    public interface Result {
        void success(byte[] value);
        void failure(String code); // Stable codes only: never log keys or document bytes.
    }
    private final AndroidIntegrityGuard integrity;
    private final String alias;
    private final HardwarePolicy policy;
    private final UUID tenant, account;
    private final KeyStore store;

    public AndroidDocumentVault(UUID tenant, UUID account, int keyVersion, HardwarePolicy policy, AndroidIntegrityGuard integrity) throws Exception {
        if (tenant == null || account == null || keyVersion < 1 || policy == null || integrity == null) throw new IllegalArgumentException("Invalid key scope");
        byte[] digest=MessageDigest.getInstance("SHA-256").digest((tenant+"/"+account+"/"+keyVersion).getBytes(StandardCharsets.UTF_8));
        StringBuilder name=new StringBuilder("sgacd.vault.");
        for (byte b:digest) name.append(String.format(java.util.Locale.ROOT,"%02x",b & 255));
        this.integrity=integrity; this.alias=name.toString(); this.policy=policy; this.tenant=tenant; this.account=account;
        store=KeyStore.getInstance("AndroidKeyStore"); store.load(null);
    }
    public String keyId() { return alias; }
    public String documentContext(UUID document) { return VaultEnvelope.context(tenant,account,document); }

    /** Explicit enrollment only. Never called automatically while decrypting. */
    public void createKey(Context context) throws GeneralSecurityException {
        integrity.requireSensitiveOperation(context);
        synchronized (AndroidDocumentVault.class) {
            File path=new File(context.getNoBackupFilesDir(),alias+".enrollment.lock");
            try (FileOutputStream stream=new FileOutputStream(path,true); FileLock lock=stream.getChannel().tryLock()) {
                if(lock==null)throw new GeneralSecurityException("ENROLLMENT_BUSY");
                createKeyLocked(context);
            } catch(IOException | OverlappingFileLockException exception) { throw new GeneralSecurityException("ENROLLMENT_LOCK_UNAVAILABLE"); }
        }
    }

    private void createKeyLocked(Context context) throws GeneralSecurityException {
        if (store.containsAlias(alias)) throw new GeneralSecurityException("KEY_ALREADY_EXISTS");
        KeyguardManager lock=context.getSystemService(KeyguardManager.class);
        BiometricManager biometrics=context.getSystemService(BiometricManager.class);
        if (lock==null || !lock.isDeviceSecure() || biometrics==null || biometrics.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)!=BiometricManager.BIOMETRIC_SUCCESS)
            throw new GeneralSecurityException("STRONG_BIOMETRICS_REQUIRED");
        KeyGenParameterSpec.Builder spec=new KeyGenParameterSpec.Builder(alias,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT)
            .setKeySize(256).setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setRandomizedEncryptionRequired(true).setUserAuthenticationRequired(true)
            .setUserAuthenticationParameters(0,KeyProperties.AUTH_BIOMETRIC_STRONG)
            .setInvalidatedByBiometricEnrollment(true).setUnlockedDeviceRequired(true)
            .setIsStrongBoxBacked(policy==HardwarePolicy.STRONGBOX_REQUIRED);
        KeyGenerator generator=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
        generator.init(spec.build()); generator.generateKey();
        existingKey(); // Reject an unexpected provider/security level. Never export it.
    }

    private SecretKey existingKey() throws GeneralSecurityException {
        SecretKey key=(SecretKey)store.getKey(alias,null);
        if (key==null) throw new GeneralSecurityException("KEY_MISSING");
        KeyInfo info=(KeyInfo)SecretKeyFactory.getInstance("AES","AndroidKeyStore").getKeySpec(key,KeyInfo.class);
        int level=info.getSecurityLevel();
        boolean hardware=level==KeyProperties.SECURITY_LEVEL_STRONGBOX || level==KeyProperties.SECURITY_LEVEL_TRUSTED_ENVIRONMENT;
        if (!hardware || (policy==HardwarePolicy.STRONGBOX_REQUIRED && level!=KeyProperties.SECURITY_LEVEL_STRONGBOX)
                || info.getKeySize()!=256 || !info.isUserAuthenticationRequired()
                || info.getUserAuthenticationType()!=KeyProperties.AUTH_BIOMETRIC_STRONG
                || (info.getUserAuthenticationValidityDurationSeconds()!=0 && info.getUserAuthenticationValidityDurationSeconds()!=-1)
                || !info.isInvalidatedByBiometricEnrollment()) throw new GeneralSecurityException("HARDWARE_POLICY_MISMATCH");
        return key;
    }

    public void encrypt(Activity activity, UUID documentId, byte[] document, CancellationSignal cancellation, Executor executor, Result result) {
        if (document==null || document.length>VaultEnvelope.MAX_DOCUMENT) { result.failure("DOCUMENT_SIZE"); return; }
        byte[] privateCopy=document.clone();
        try {
            AndroidSensitiveScreen.protect(activity);
            integrity.requireSensitiveOperation(activity);
            Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding"); cipher.init(Cipher.ENCRYPT_MODE,existingKey());
            byte[] header=VaultEnvelope.header(VaultEnvelope.ANDROID,documentContext(documentId),alias,new byte[0],cipher.getIV(),privateCopy.length+16);
            authenticate(activity,cipher,cancellation,executor,result,privateCopy,header,true);
        } catch (GeneralSecurityException | RuntimeException exception) { Arrays.fill(privateCopy,(byte)0); result.failure("KEY_OR_ENCRYPTION_UNAVAILABLE"); }
    }

    public void decrypt(Activity activity, UUID documentId, byte[] encrypted, CancellationSignal cancellation, Executor executor, Result result) {
        try {
            AndroidSensitiveScreen.protect(activity);
            integrity.requireSensitiveOperation(activity);
            VaultEnvelope.Parsed envelope=VaultEnvelope.parse(encrypted,VaultEnvelope.ANDROID,documentContext(documentId),alias);
            Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
            cipher.init(Cipher.DECRYPT_MODE,existingKey(),new GCMParameterSpec(128,envelope.nonce()));
            authenticate(activity,cipher,cancellation,executor,result,envelope.ciphertext(),envelope.header(),false);
        } catch (GeneralSecurityException | RuntimeException exception) { result.failure("INVALID_DOCUMENT_OR_KEY_UNAVAILABLE"); }
    }

    private void authenticate(Activity activity, Cipher cipher, CancellationSignal cancellation, Executor executor, Result result, byte[] input, byte[] header, boolean encrypting) {
        AtomicBoolean completed=new AtomicBoolean(false);
        BiometricPrompt.AuthenticationCallback callback=new BiometricPrompt.AuthenticationCallback() {
            @Override public void onAuthenticationSucceeded(BiometricPrompt.AuthenticationResult authentication) {
                if (!completed.compareAndSet(false,true)) return;
                byte[] value=null;
                try {
                    // The exact cipher initialized above must be the hardware-authorized operation.
                    if (authentication.getCryptoObject()==null || authentication.getCryptoObject().getCipher()!=cipher) throw new GeneralSecurityException("AUTH_OPERATION_MISMATCH");
                    integrity.requireSensitiveOperation(activity);
                    cipher.updateAAD(header);
                    value=cipher.doFinal(input); // AEAD tag is verified before any plaintext is returned.
                    integrity.requireSensitiveOperation(activity);
                } catch (GeneralSecurityException | RuntimeException exception) { if(value!=null)Arrays.fill(value,(byte)0);value=null;result.failure("AUTHENTICATION_OR_INTEGRITY_FAILED"); }
                finally { Arrays.fill(input,(byte)0); }
                if (value!=null) result.success(encrypting?VaultEnvelope.join(header,value):value);
            }
            @Override public void onAuthenticationError(int errorCode, CharSequence message) {
                if (completed.compareAndSet(false,true)) { Arrays.fill(input,(byte)0); result.failure("BIOMETRIC_CANCELLED_OR_UNAVAILABLE"); }
            }
        };
        try {
            BiometricPrompt prompt=new BiometricPrompt.Builder(activity).setTitle("Autorizar acceso al documento")
                .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                .setNegativeButton("Cancelar",executor,(dialog,which)-> { if (completed.compareAndSet(false,true)) { Arrays.fill(input,(byte)0); result.failure("BIOMETRIC_CANCELLED"); } })
                .build();
            prompt.authenticate(new BiometricPrompt.CryptoObject(cipher),cancellation,executor,callback);
        } catch (RuntimeException exception) {
            if (completed.compareAndSet(false,true)) { Arrays.fill(input,(byte)0); result.failure("BIOMETRIC_UNAVAILABLE"); }
        }
    }
}
