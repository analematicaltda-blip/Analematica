package co.analematica.approval;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.charset.StandardCharsets;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.Signature;
import java.security.interfaces.ECPublicKey;
import java.security.spec.ECGenParameterSpec;
import java.util.UUID;

/** CPU interoperability fixture only: does not represent a trusted hardware key. */
public final class ApprovalCheck {
    private static int checks=0;
    private static void expect(boolean value) { checks++;if(!value)throw new AssertionError("Approval contract failed"); }
    public static void main(String[] args) throws Exception {
        byte[] message=Files.readAllBytes(Path.of(args[0]));String[] f=new String(message,StandardCharsets.US_ASCII).split("\n",-1);
        UUID audience=UUID.fromString(f[1]),credential=UUID.fromString(f[3]);long actor=Long.parseLong(f[2]);long now=System.currentTimeMillis()/1000;
        ApprovalMessage parsed=ApprovalMessage.parse(message,audience,actor,credential,now);
        expect(parsed.amount.equals("12.30"));expect(parsed.currency.equals("COP"));expect(parsed.summary().contains(parsed.destination));
        for(int test=0;test<6;test++) {
            boolean rejected=false;
            try {
                switch(test) {
                    case 0:ApprovalMessage.parse(message,UUID.randomUUID(),actor,credential,now);break;
                    case 1:ApprovalMessage.parse(message,audience,actor+1,credential,now);break;
                    case 2:ApprovalMessage.parse(message,audience,actor,UUID.randomUUID(),now);break;
                    case 3:ApprovalMessage.parse(message,audience,actor,credential,now+300);break;
                    case 4:ApprovalMessage.parse("sign this arbitrary document".getBytes(StandardCharsets.US_ASCII),audience,actor,credential,now);break;
                    default:ApprovalMessage.parse((new String(message,StandardCharsets.US_ASCII)+"\n").getBytes(StandardCharsets.US_ASCII),audience,actor,credential,now);
                }
            } catch(IllegalArgumentException expected) { rejected=true; }
            expect(rejected);
        }
        KeyPairGenerator generator=KeyPairGenerator.getInstance("EC");generator.initialize(new ECGenParameterSpec("secp256r1"));KeyPair key=generator.generateKeyPair();
        Signature signature=Signature.getInstance("SHA256withECDSA");signature.initSign(key.getPrivate());signature.update(message);byte[] proof=signature.sign();
        ECPublicKey publicKey=(ECPublicKey)key.getPublic();byte[] raw=new byte[65];raw[0]=4;
        for(int index=0;index<2;index++) {
            byte[] coordinate=(index==0?publicKey.getW().getAffineX():publicKey.getW().getAffineY()).toByteArray();int size=Math.min(32,coordinate.length);
            System.arraycopy(coordinate,coordinate.length-size,raw,1+32*index+32-size,size);
        }
        Files.write(Path.of(args[1]),raw);Files.write(Path.of(args[2]),proof);
        System.out.println("Approval message assertions passed: "+checks);
    }
}
