package co.analematica.vault.bridge;

import android.app.Activity;
import co.analematica.integrity.AndroidIntegrityGuard;
import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.CancellationSignal;
import android.os.Handler;
import android.os.Looper;
import co.analematica.vault.AndroidDocumentVault;
import co.analematica.vault.EncryptedDocumentStore;
import co.analematica.vault.VaultEnvelope;
import io.flutter.embedding.engine.plugins.FlutterPlugin;
import io.flutter.embedding.engine.plugins.activity.ActivityAware;
import io.flutter.embedding.engine.plugins.activity.ActivityPluginBinding;
import io.flutter.plugin.common.MethodCall;
import io.flutter.plugin.common.MethodChannel;
import io.flutter.plugin.common.PluginRegistry;
import java.io.InputStream;
import java.io.File;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.atomic.AtomicInteger;

/** The channel never accepts or returns document bytes, paths, names or keys. */
public final class SGAVaultPlugin implements FlutterPlugin,ActivityAware,MethodChannel.MethodCallHandler,PluginRegistry.ActivityResultListener {
    private final AtomicInteger pickerSequence=new AtomicInteger(39417);
    private final Map<Integer,Operation> pickers=new HashMap<>();
    private final Handler main=new Handler(Looper.getMainLooper());
    private static final ExecutorService io=Executors.newSingleThreadExecutor(task -> { Thread thread=new Thread(task,"sgacd-vault-io");thread.setDaemon(true);return thread; });
    private final AtomicReference<Operation> active=new AtomicReference<>();
    private MethodChannel channel;
    private Context context;
    private Activity activity;
    private ActivityPluginBinding binding;
    private static final class Operation {
        final UUID request;
        final MethodChannel.Result result;
        final AndroidDocumentVault vault;
        final CancellationSignal cancellation=new CancellationSignal();
        int pickerCode=-1;
        Operation(UUID request,MethodChannel.Result result,AndroidDocumentVault vault) { this.request=request;this.result=result;this.vault=vault; }
    }
    @Override public void onAttachedToEngine(FlutterPluginBinding binding) {
        context=binding.getApplicationContext();
        channel=new MethodChannel(binding.getBinaryMessenger(),"co.analematica/sgacd_vault/v1");channel.setMethodCallHandler(this);
    }
    @Override public void onDetachedFromEngine(FlutterPluginBinding binding) { cancelActive();channel.setMethodCallHandler(null); }
    @Override public void onAttachedToActivity(ActivityPluginBinding binding) { this.binding=binding;activity=binding.getActivity();binding.addActivityResultListener(this); }
    @Override public void onReattachedToActivityForConfigChanges(ActivityPluginBinding binding) { onAttachedToActivity(binding); }
    @Override public void onDetachedFromActivityForConfigChanges() { detachActivity(); }
    @Override public void onDetachedFromActivity() { detachActivity(); }
    private void detachActivity() { cancelActive();if(binding!=null)binding.removeActivityResultListener(this);binding=null;activity=null; }
    private void cancelActive() {
        Operation operation=active.getAndSet(null);
        if(operation!=null) { operation.cancellation.cancel();operation.result.error("CANCELLED",null,null); }
    }
    private static UUID uuid(Object value) {
        if(!(value instanceof String))throw new IllegalArgumentException();
        UUID result=UUID.fromString((String)value);
        if(!result.toString().equals(value))throw new IllegalArgumentException();return result;
    }
    private static String code(Exception exception) {
        String message=exception.getMessage();return Arrays.asList("KEY_ALREADY_EXISTS","STRONG_BIOMETRICS_REQUIRED","ENROLLMENT_BUSY","ENROLLMENT_LOCK_UNAVAILABLE","HARDWARE_POLICY_MISMATCH","KEY_MISSING").contains(message)?message:"NATIVE_OPERATION_FAILED";
    }
    private void fail(Operation operation,String code) {
        main.post(()-> { if(active.compareAndSet(operation,null))operation.result.error(code,null,null); });
    }
    private void success(Operation operation,String status,Map<String,Object> fields) {
        try { AndroidIntegrityGuard.fromApplication(context).requireSensitiveOperation(context); }
        catch(Exception exception) { fail(operation,"CLIENT_INTEGRITY_BLOCKED");return; }
        Map<String,Object> reply=new HashMap<>(fields);reply.put("ok",true);reply.put("protocol",1);reply.put("status",status);
        main.post(()-> { if(active.compareAndSet(operation,null))operation.result.success(reply); });
    }
    @Override public void onMethodCall(MethodCall call,MethodChannel.Result result) {
        if(call.method.equals("cancel")) {
            try {
                UUID id=uuid(call.argument("request_id"));Operation op=active.get();
                if(op!=null && op.request.equals(id)) { cancelActive();if(activity!=null && op.pickerCode>=0)activity.finishActivity(op.pickerCode); }
                result.success(null);
            } catch(RuntimeException exception) { result.error("INVALID_ARGUMENTS",null,null); }
            return;
        }
        if(!Arrays.asList("provision","import_document","verify_document","list_documents").contains(call.method)) { result.notImplemented();return; }
        try { AndroidIntegrityGuard.fromApplication(context).requireSensitiveOperation(context); }
        catch(Exception exception) { result.error("CLIENT_INTEGRITY_BLOCKED",null,null);return; }
        Operation operation;
        try {
            if(!(call.arguments instanceof Map))throw new IllegalArgumentException();
            for(Object key:((Map<?,?>)call.arguments).keySet()) if(!Arrays.asList("tenant","account","version","hardware","request_id","document_id").contains(key))throw new IllegalArgumentException();
            UUID tenant=uuid(call.argument("tenant")),account=uuid(call.argument("account")),request=uuid(call.argument("request_id"));
            int version=Integer.parseInt(call.argument("version"));
            AndroidDocumentVault.HardwarePolicy hardware=AndroidDocumentVault.HardwarePolicy.valueOf(call.argument("hardware"));
            operation=new Operation(request,result,new AndroidDocumentVault(tenant,account,version,hardware,AndroidIntegrityGuard.fromApplication(context)));
        } catch(Exception exception) { result.error("INVALID_ARGUMENTS_OR_UNAVAILABLE",null,null);return; }
        if(activity==null || activity.isFinishing() || activity.isDestroyed()) { result.error("ACTIVITY_UNAVAILABLE",null,null);return; }
        if(!active.compareAndSet(null,operation)) { result.error("BUSY",null,null);return; }
        switch(call.method) {
            case "provision":
                try { new AlertDialog.Builder(activity).setTitle("Crear llave local protegida")
                    .setMessage("Se creará una llave nueva para esta cuenta. No se borrará ni reemplazará una llave existente.")
                    .setPositiveButton("Crear llave",(dialog,which)->io.execute(()-> {
                        if(active.get()!=operation)return;
                        try { operation.vault.createKey(context);success(operation,"provisioned",new HashMap<>()); }
                        catch(Exception exception) { fail(operation,code(exception)); }
                    })).setNegativeButton("Cancelar",(dialog,which)->fail(operation,"CANCELLED"))
                    .setOnCancelListener(dialog->fail(operation,"CANCELLED")).show(); }
                catch(RuntimeException exception) { fail(operation,"ACTIVITY_UNAVAILABLE"); }
                break;
            case "import_document":
                Intent picker=new Intent(Intent.ACTION_OPEN_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE).setType("*/*")
                    .putExtra(Intent.EXTRA_MIME_TYPES,new String[]{"application/pdf","image/jpeg","image/png"});
                try {
                    if(pickers.size()>=128)throw new IllegalStateException();
                    operation.pickerCode=pickerSequence.getAndUpdate(value->(value+1)&65535);
                    pickers.put(operation.pickerCode,operation);
                    activity.startActivityForResult(picker,operation.pickerCode);
                }
                catch(RuntimeException exception) { fail(operation,"PICKER_UNAVAILABLE"); }
                break;
            case "verify_document":
                final UUID document;
                try { document=uuid(call.argument("document_id")); }
                catch(RuntimeException exception) { fail(operation,"INVALID_ARGUMENTS");break; }
                io.execute(()-> {
                    try {
                        byte[] envelope=new EncryptedDocumentStore(context,operation.vault).read(document);
                        main.post(()-> { if(active.get()!=operation || activity==null)return;
                            operation.vault.decrypt(activity,document,envelope,operation.cancellation,io,new AndroidDocumentVault.Result() {
                                @Override public void success(byte[] plaintext) { Arrays.fill(plaintext,(byte)0);Map<String,Object> data=new HashMap<>();data.put("document_id",document.toString());SGAVaultPlugin.this.success(operation,"verified",data); }
                                @Override public void failure(String code) { fail(operation,code); }
                            });
                        });
                    } catch(Exception exception) { fail(operation,code(exception)); }
                });break;
            case "list_documents":
                io.execute(()-> {
                    File folder=new File(context.getNoBackupFilesDir(),operation.vault.keyId());
                    String[] files=folder.list((dir,name)->name.matches("[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\\.vault"));
                    if(files==null)files=new String[0];Arrays.sort(files);
                    ArrayList<String> ids=new ArrayList<>();for(int i=0;i<Math.min(64,files.length);i++)ids.add(files[i].substring(0,36));
                    Map<String,Object> data=new HashMap<>();data.put("documents",ids);data.put("has_more",files.length>64);success(operation,"listed",data);
                });break;
            default:fail(operation,"UNSUPPORTED_METHOD");
        }
    }
    @Override public boolean onActivityResult(int requestCode,int resultCode,Intent data) {
        Operation operation=pickers.remove(requestCode);
        if(operation==null)return false;
        if(active.get()!=operation)return true;
        Uri uri=data==null?null:data.getData();
        if(resultCode!=Activity.RESULT_OK || uri==null) { fail(operation,"CANCELLED");return true; }
        if(!"content".equals(uri.getScheme())) { fail(operation,"INVALID_DOCUMENT_SOURCE");return true; }
        UUID document=UUID.randomUUID();
        io.execute(()-> {
            byte[] plaintext=null;
            try {
                try(InputStream stream=context.getContentResolver().openInputStream(uri)) {
                    if(stream==null)throw new IllegalArgumentException();
                    byte[] buffer=new byte[VaultEnvelope.MAX_DOCUMENT+1];int total=0;
                    try {
                        while(total<buffer.length) { int count=stream.read(buffer,total,buffer.length-total);if(count<0)break;if(count==0)throw new IllegalArgumentException();total+=count; }
                        if(total>VaultEnvelope.MAX_DOCUMENT)throw new IllegalArgumentException();
                        plaintext=Arrays.copyOf(buffer,total);
                    } finally { Arrays.fill(buffer,(byte)0); }
                }
                final byte[] bytes=plaintext;
                main.post(()-> {
                    if(active.get()!=operation || activity==null) { Arrays.fill(bytes,(byte)0);return; }
                    try { operation.vault.encrypt(activity,document,bytes,operation.cancellation,io,new AndroidDocumentVault.Result() {
                        @Override public void success(byte[] encrypted) {
                            if(active.get()!=operation)return;
                            try { new EncryptedDocumentStore(context,operation.vault).write(document,encrypted);Map<String,Object> reply=new HashMap<>();reply.put("document_id",document.toString());SGAVaultPlugin.this.success(operation,"stored",reply); }
                            catch(Exception exception) { fail(operation,code(exception)); }
                        }
                        @Override public void failure(String code) { fail(operation,code); }
                    }); } finally { Arrays.fill(bytes,(byte)0); }
                });
            } catch(Exception exception) { if(plaintext!=null)Arrays.fill(plaintext,(byte)0);fail(operation,"DOCUMENT_IMPORT_FAILED"); }
        });return true;
    }
}
