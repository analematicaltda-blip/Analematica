package co.analematica.approval;

import android.app.Activity;
import co.analematica.integrity.AndroidIntegrityGuard;
import android.app.KeyguardManager;
import android.content.Context;
import android.hardware.biometrics.BiometricManager;
import android.hardware.biometrics.BiometricPrompt;
import android.os.CancellationSignal;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyInfo;
import android.security.keystore.KeyProperties;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.channels.FileLock;
import java.nio.channels.OverlappingFileLockException;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.KeyFactory;
import java.security.KeyPairGenerator;
import java.security.KeyStore;
import java.security.MessageDigest;
import java.security.PrivateKey;
import java.security.Signature;
import java.security.cert.Certificate;
import java.security.interfaces.ECPublicKey;
import java.security.spec.ECGenParameterSpec;
import java.util.Arrays;
import java.util.UUID;
import java.util.concurrent.Executor;
import java.util.concurrent.atomic.AtomicBoolean;

/** Separate hardware signing key: never reuse the document-encryption key. Android 12+. */
public final class AndroidApprovalKey {
    public interface Result { void signed(byte[] derSignature); void failed(String code); }
    private final KeyStore store;
    private final UUID audience,credential;
    private final long actor;
    private final String alias;
    private final boolean requireStrongBox;
    private final AndroidIntegrityGuard integrity;
    public AndroidApprovalKey(UUID audience,long actor,UUID credential,boolean requireStrongBox,AndroidIntegrityGuard integrity) throws Exception {
        if(audience==null || credential==null || actor<1 || integrity==null)throw new IllegalArgumentException("INVALID_IDENTITY");
        this.integrity=integrity;this.audience=audience;this.actor=actor;this.credential=credential;this.requireStrongBox=requireStrongBox;
        byte[] digest=MessageDigest.getInstance("SHA-256").digest((audience+"/"+actor+"/"+credential).getBytes(StandardCharsets.US_ASCII));
        StringBuilder id=new StringBuilder("sgacd.approval.");for(byte b:digest)id.append(String.format(java.util.Locale.ROOT,"%02x",b&255));alias=id.toString();
        store=KeyStore.getInstance("AndroidKeyStore");store.load(null);
    }
    public void createKey(Context context,byte[] enrollmentNonce) throws Exception {
        integrity.requireSensitiveOperation(context);
        if(enrollmentNonce==null || enrollmentNonce.length!=32)throw new GeneralSecurityException("INVALID_ENROLLMENT_CHALLENGE");
        synchronized(AndroidApprovalKey.class) {
            try(FileOutputStream file=new FileOutputStream(new File(context.getNoBackupFilesDir(),alias+".lock"),true);FileLock lock=file.getChannel().tryLock()) {
                if(lock==null)throw new GeneralSecurityException("ENROLLMENT_BUSY");
                if(store.containsAlias(alias))throw new GeneralSecurityException("KEY_ALREADY_EXISTS");
                KeyguardManager screen=context.getSystemService(KeyguardManager.class);BiometricManager bio=context.getSystemService(BiometricManager.class);
                if(screen==null || !screen.isDeviceSecure() || bio==null || bio.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)!=BiometricManager.BIOMETRIC_SUCCESS)throw new GeneralSecurityException("STRONG_BIOMETRICS_REQUIRED");
                KeyPairGenerator generator=KeyPairGenerator.getInstance("EC","AndroidKeyStore");
                generator.initialize(new KeyGenParameterSpec.Builder(alias,KeyProperties.PURPOSE_SIGN|KeyProperties.PURPOSE_VERIFY)
                    .setAlgorithmParameterSpec(new ECGenParameterSpec("secp256r1")).setDigests(KeyProperties.DIGEST_SHA256)
                    .setUserAuthenticationRequired(true).setUserAuthenticationParameters(0,KeyProperties.AUTH_BIOMETRIC_STRONG)
                    .setInvalidatedByBiometricEnrollment(true).setUnlockedDeviceRequired(true).setIsStrongBoxBacked(requireStrongBox)
                    .setAttestationChallenge(enrollmentNonce.clone()).build());
                generator.generateKeyPair();existingKey();
            } catch(IOException|OverlappingFileLockException exception) { throw new GeneralSecurityException("ENROLLMENT_LOCK_UNAVAILABLE"); }
        }
    }
    private PrivateKey existingKey() throws GeneralSecurityException {
        PrivateKey key=(PrivateKey)store.getKey(alias,null);if(key==null)throw new GeneralSecurityException("KEY_MISSING");
        KeyInfo info=KeyFactory.getInstance("EC","AndroidKeyStore").getKeySpec(key,KeyInfo.class);
        int level=info.getSecurityLevel();
        if((level!=KeyProperties.SECURITY_LEVEL_STRONGBOX && level!=KeyProperties.SECURITY_LEVEL_TRUSTED_ENVIRONMENT)
           || (requireStrongBox && level!=KeyProperties.SECURITY_LEVEL_STRONGBOX) || info.getKeySize()!=256 || !"EC".equals(key.getAlgorithm()) || !info.isUserAuthenticationRequired()
           || info.getUserAuthenticationType()!=KeyProperties.AUTH_BIOMETRIC_STRONG || !info.isInvalidatedByBiometricEnrollment()
           || (info.getUserAuthenticationValidityDurationSeconds()!=0 && info.getUserAuthenticationValidityDurationSeconds()!=-1))throw new GeneralSecurityException("HARDWARE_POLICY_MISMATCH");
        return key;
    }
    public byte[] publicKey() throws Exception {
        existingKey();ECPublicKey key=(ECPublicKey)store.getCertificate(alias).getPublicKey();
        byte[] encoded=new byte[65];encoded[0]=4;
        for(int coordinate=0;coordinate<2;coordinate++) {
            byte[] value=(coordinate==0?key.getW().getAffineX():key.getW().getAffineY()).toByteArray();
            int count=Math.min(32,value.length);System.arraycopy(value,value.length-count,encoded,1+32*coordinate+32-count,count);
        }
        return encoded;
    }
    public byte[][] attestationChain() throws Exception {
        existingKey();Certificate[] certificates=store.getCertificateChain(alias);
        if(certificates==null || certificates.length<1 || certificates.length>8)throw new GeneralSecurityException("ATTESTATION_UNAVAILABLE");
        byte[][] result=new byte[certificates.length][];
        for(int i=0;i<result.length;i++) { result[i]=certificates[i].getEncoded();if(result[i].length>16384)throw new GeneralSecurityException("ATTESTATION_SIZE"); }
        return result;
    }
    public void approve(Activity activity,byte[] payload,CancellationSignal cancellation,Executor executor,Result result) {
        try {
            integrity.requireSensitiveOperation(activity);
            ApprovalMessage message=ApprovalMessage.parse(payload,audience,actor,credential,System.currentTimeMillis()/1000);
            Signature signature=Signature.getInstance("SHA256withECDSA");signature.initSign(existingKey());
            AtomicBoolean completed=new AtomicBoolean(false);
            BiometricPrompt.AuthenticationCallback callback=new BiometricPrompt.AuthenticationCallback() {
                @Override public void onAuthenticationSucceeded(BiometricPrompt.AuthenticationResult authentication) {
                    if(!completed.compareAndSet(false,true))return;
                    byte[] proof;
                    try {
                        if(authentication.getCryptoObject()==null || authentication.getCryptoObject().getSignature()!=signature)throw new GeneralSecurityException();
                        // Recheck risk and expiry after the user has completed the prompt.
                        integrity.requireSensitiveOperation(activity);
                        ApprovalMessage.parse(message.bytes(),audience,actor,credential,System.currentTimeMillis()/1000);
                        signature.update(message.bytes());proof=signature.sign();
                    } catch(GeneralSecurityException|RuntimeException exception) { result.failed("APPROVAL_SIGNATURE_FAILED");return; }
                    result.signed(proof);
                }
                @Override public void onAuthenticationError(int code,CharSequence text) { if(completed.compareAndSet(false,true))result.failed("BIOMETRIC_CANCELLED_OR_UNAVAILABLE"); }
            };
            new BiometricPrompt.Builder(activity).setTitle(message.phase.equals("REVIEW")?"1. Revisar transferencia":"2. Autorizar transferencia")
                .setDescription(message.summary()).setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                .setNegativeButton("Cancelar",executor,(dialog,which)-> { if(completed.compareAndSet(false,true))result.failed("CANCELLED"); })
                .build().authenticate(new BiometricPrompt.CryptoObject(signature),cancellation,executor,callback);
        } catch(GeneralSecurityException|RuntimeException exception) { result.failed("APPROVAL_OR_KEY_UNAVAILABLE"); }
    }
}
