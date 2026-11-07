package co.analematica.vault;

import android.content.Context;
import android.util.AtomicFile;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.ByteArrayOutputStream;
import java.util.UUID;

/** Writes only bounded encrypted envelopes, in app-private storage excluded from backup. */
public final class EncryptedDocumentStore {
    private final File directory;
    private final String keyId;
    private final AndroidDocumentVault vault;
    public EncryptedDocumentStore(Context context, AndroidDocumentVault vault) throws IOException {
        String keyId=vault.keyId(); this.vault=vault;
        if (!keyId.matches("sgacd\\.vault\\.[0-9a-f]{64}")) throw new IllegalArgumentException("Invalid key ID");
        this.keyId=keyId;
        directory=new File(context.getNoBackupFilesDir(),keyId);
        if (!directory.isDirectory() && !directory.mkdirs()) throw new IOException("PRIVATE_STORAGE_UNAVAILABLE");
    }
    public synchronized void write(UUID documentId,byte[] encrypted) throws IOException {
        VaultEnvelope.parse(encrypted,VaultEnvelope.ANDROID,vault.documentContext(documentId),keyId);
        AtomicFile file=new AtomicFile(new File(directory,documentId.toString()+".vault"));
        if (file.getBaseFile().exists()) throw new IOException("DOCUMENT_ALREADY_EXISTS_USE_NEW_UUID");
        FileOutputStream output=null;
        try { output=file.startWrite(); output.write(encrypted); file.finishWrite(output); }
        catch (IOException exception) { if (output!=null) file.failWrite(output); throw new IOException("ENCRYPTED_STORAGE_FAILED"); }
    }
    public synchronized byte[] read(UUID documentId) throws IOException {
        AtomicFile file=new AtomicFile(new File(directory,documentId.toString()+".vault"));
        long size=file.getBaseFile().length();
        if (size<31 || size>VaultEnvelope.MAX_DOCUMENT+2048) throw new IOException("INVALID_ENCRYPTED_FILE");
        byte[] encrypted;
        try (InputStream input=file.openRead(); ByteArrayOutputStream bytes=new ByteArrayOutputStream()) {
            byte[] block=new byte[8192]; int count;
            while ((count=input.read(block))!=-1) {
                if (bytes.size()+count>VaultEnvelope.MAX_DOCUMENT+2048) throw new IOException("ENCRYPTED_FILE_TOO_LARGE");
                bytes.write(block,0,count);
            }
            encrypted=bytes.toByteArray();
        }
        VaultEnvelope.parse(encrypted,VaultEnvelope.ANDROID,vault.documentContext(documentId),keyId);
        return encrypted;
    }
}
