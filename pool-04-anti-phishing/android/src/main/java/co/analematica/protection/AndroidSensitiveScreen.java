package co.analematica.protection;
import android.app.Activity;
import android.os.Looper;
import android.view.WindowManager;

/** Conservative Activity-lifetime protection; never clears another operation's flags. */
public final class AndroidSensitiveScreen {
    private AndroidSensitiveScreen() {}
    public static void protect(Activity activity) {
        if(activity==null || activity.isDestroyed() || activity.isFinishing() || Looper.myLooper()!=Looper.getMainLooper())throw new IllegalStateException("SENSITIVE_SCREEN_UNAVAILABLE");
        activity.getWindow().addFlags(WindowManager.LayoutParams.FLAG_SECURE);
        activity.getWindow().setHideOverlayWindows(true);
        activity.getWindow().getDecorView().setFilterTouchesWhenObscured(true);
    }
}
