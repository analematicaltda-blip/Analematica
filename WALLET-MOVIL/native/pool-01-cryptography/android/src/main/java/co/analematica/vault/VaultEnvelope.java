package co.analematica.vault;

import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.UUID;

/** Bounded, versioned metadata. All header bytes are authenticated as GCM AAD. */
public final class VaultEnvelope {
    private VaultEnvelope() {}
    public static final int MAX_DOCUMENT = 8 * 1024 * 1024;
    private static final byte[] MAGIC = "SGAVLT01".getBytes(StandardCharsets.US_ASCII);
    public static final int ANDROID = 1, IOS = 2;

    public static String context(UUID tenant, UUID account, UUID document) {
        if (tenant == null || account == null || document == null) throw new IllegalArgumentException("Missing scope");
        return "sgacd/v1/" + tenant + "/" + account + "/" + document;
    }

    private static byte[] utf8(String value, int limit) {
        byte[] result = value.getBytes(StandardCharsets.UTF_8);
        if (result.length == 0 || result.length > limit) throw new IllegalArgumentException("Invalid metadata size");
        return result;
    }

    public static byte[] header(int platform, String context, String keyId, byte[] wrapped, byte[] nonce, int ciphertextSize) {
        byte[] scope = utf8(context, 256), key = utf8(keyId, 128);
        if ((platform != ANDROID && platform != IOS) || nonce.length != 12 || wrapped.length > 1024
                || (platform == ANDROID && wrapped.length != 0) || (platform == IOS && wrapped.length == 0)
                || ciphertextSize < 16 || ciphertextSize > MAX_DOCUMENT + 16) throw new IllegalArgumentException("Invalid envelope");
        return ByteBuffer.allocate(31 + scope.length + key.length + wrapped.length)
            .put(MAGIC).put((byte) platform).putShort((short) scope.length).put(scope)
            .putShort((short) key.length).put(key).putShort((short) wrapped.length).put(wrapped)
            .put(nonce).putInt(ciphertextSize).array();
    }

    public static byte[] join(byte[] header, byte[] ciphertext) {
        if (ciphertext.length < 16 || ciphertext.length > MAX_DOCUMENT + 16) throw new IllegalArgumentException("Invalid ciphertext size");
        return ByteBuffer.allocate(header.length + ciphertext.length).put(header).put(ciphertext).array();
    }

    private static byte[] field(ByteBuffer buffer, int maximum, boolean emptyAllowed) {
        int size = Short.toUnsignedInt(buffer.getShort());
        if (size > maximum || (!emptyAllowed && size == 0) || size > buffer.remaining()) throw new IllegalArgumentException("Invalid envelope field");
        byte[] result = new byte[size]; buffer.get(result); return result;
    }

    private static String text(byte[] value) throws CharacterCodingException {
        return StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(value)).toString();
    }

    public static Parsed parse(byte[] encoded, int expectedPlatform, String expectedContext, String expectedKey) {
        if (encoded == null || encoded.length > MAX_DOCUMENT + 2048) throw new IllegalArgumentException("Invalid envelope size");
        try {
            ByteBuffer buffer = ByteBuffer.wrap(encoded);
            byte[] magic = new byte[8]; buffer.get(magic);
            if (!MessageDigest.isEqual(magic, MAGIC) || Byte.toUnsignedInt(buffer.get()) != expectedPlatform) throw new IllegalArgumentException("Unsupported envelope");
            String context = text(field(buffer, 256, false));
            String keyId = text(field(buffer, 128, false));
            byte[] wrapped = field(buffer, 1024, true), nonce = new byte[12]; buffer.get(nonce);
            int size = buffer.getInt(), offset = buffer.position();
            if (size < 16 || size > MAX_DOCUMENT + 16 || size != buffer.remaining()
                    || !MessageDigest.isEqual(context.getBytes(StandardCharsets.UTF_8), utf8(expectedContext, 256))
                    || !MessageDigest.isEqual(keyId.getBytes(StandardCharsets.UTF_8), utf8(expectedKey, 128))) throw new IllegalArgumentException("Envelope scope mismatch");
            if (expectedPlatform == ANDROID ? wrapped.length != 0 : expectedPlatform != IOS || wrapped.length == 0) throw new IllegalArgumentException("Invalid key wrapping");
            byte[] ciphertext = new byte[size]; buffer.get(ciphertext);
            return new Parsed(Arrays.copyOf(encoded, offset), nonce, ciphertext, wrapped);
        } catch (java.nio.BufferUnderflowException | CharacterCodingException exception) {
            throw new IllegalArgumentException("Malformed envelope");
        }
    }

    public static final class Parsed {
        private final byte[] header, nonce, ciphertext, wrapped;
        private Parsed(byte[] header, byte[] nonce, byte[] ciphertext, byte[] wrapped) {
            this.header=header; this.nonce=nonce; this.ciphertext=ciphertext; this.wrapped=wrapped;
        }
        public byte[] header() { return header.clone(); }
        public byte[] nonce() { return nonce.clone(); }
        public byte[] ciphertext() { return ciphertext.clone(); }
        public byte[] wrappedKey() { return wrapped.clone(); }
    }
}
