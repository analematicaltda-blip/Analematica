package co.analematica.integrity;
import java.util.HashSet;
import java.util.Set;

/** Pure policy fixtures, not a rooted-device or APK-signature integration test. */
public final class IntegrityCheck {
    private static int checks;
    private static final String A="a".repeat(64),B="b".repeat(64),C="c".repeat(64);
    private static void expect(boolean condition) {checks++;if(!condition)throw new AssertionError("Integrity policy regression");}
    private static IntegrityPolicy.Observation sample(String app,long version,Set<String> pins,boolean debug,boolean debugger,boolean root,boolean complete) {
        return new IntegrityPolicy.Observation(app,version,pins,debug,debugger,root,complete);
    }
    public static void main(String[] args) {
        Set<String> pins=new HashSet<>(Set.of(A,B));IntegrityPolicy p=new IntegrityPolicy("co.analematica.wallet",pins,10);pins.add(C);
        expect(p.evaluate(sample("co.analematica.wallet",10,Set.of(A),false,false,false,true)).isEmpty());
        expect(p.evaluate(sample("co.analematica.wallet",11,Set.of(B),false,false,false,true)).isEmpty());
        expect(p.evaluate(sample("co.analematica.wallet",11,Set.of(A,B),false,false,false,true)).isEmpty());
        expect(p.evaluate(sample("co.analematica.wallet",10,Set.of(C),false,false,false,true)).contains(IntegrityPolicy.Finding.SIGNER));
        expect(p.evaluate(sample("co.analematica.wallet",10,Set.of(A,C),false,false,false,true)).contains(IntegrityPolicy.Finding.SIGNER));
        expect(p.evaluate(sample("co.analematica.wallet",10,Set.of(),false,false,false,true)).contains(IntegrityPolicy.Finding.SIGNER));
        expect(p.evaluate(sample("co.other.wallet",10,Set.of(A),false,false,false,true)).contains(IntegrityPolicy.Finding.IDENTITY));
        expect(p.evaluate(sample("co.analematica.wallet",9,Set.of(A),false,false,false,true)).contains(IntegrityPolicy.Finding.VERSION));
        expect(p.evaluate(sample("co.analematica.wallet",10,Set.of(A),true,false,false,true)).contains(IntegrityPolicy.Finding.DEBUG_BUILD));
        expect(p.evaluate(sample("co.analematica.wallet",10,Set.of(A),false,true,false,true)).contains(IntegrityPolicy.Finding.DEBUGGER));
        expect(p.evaluate(sample("co.analematica.wallet",10,Set.of(A),false,false,true,true)).contains(IntegrityPolicy.Finding.ROOT_SIGNAL));
        expect(p.evaluate(sample("co.analematica.wallet",10,Set.of(A),false,false,false,false)).contains(IntegrityPolicy.Finding.UNKNOWN));
        expect(p.evaluate(null).contains(IntegrityPolicy.Finding.UNKNOWN));
        expect(p.evaluate(sample("bad",0,Set.of(C),true,true,true,false)).size()==7);
        int rejected=0;
        try {new IntegrityPolicy("co.test",Set.of(),1);}catch(IllegalArgumentException expected){rejected++;}
        try {new IntegrityPolicy("co.test",Set.of(A),0);}catch(IllegalArgumentException expected){rejected++;}
        try {new IntegrityPolicy("bad",Set.of(A),1);}catch(IllegalArgumentException expected){rejected++;}
        try {new IntegrityPolicy("co.test",Set.of("AA"),1);}catch(IllegalArgumentException expected){rejected++;}
        expect(rejected==4);
        boolean immutable=false;try{p.evaluate(null).clear();}catch(UnsupportedOperationException expected){immutable=true;}expect(immutable);
        System.out.println("Local integrity policy assertions passed: "+checks+". No hardware/device claims.");
    }
}
