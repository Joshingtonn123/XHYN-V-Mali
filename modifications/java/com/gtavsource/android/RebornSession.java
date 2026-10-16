package com.gtavsource.android;
import android.app.*;
import android.content.*;
import android.os.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** Loaded native libraries are not reused for a second game initialization. */
public final class RebornSession {
 static volatile boolean loaded;
 static Context app;
 private static final AtomicBoolean closing=new AtomicBoolean();
 public static void afterLibraries(Activity a){app=a.getApplicationContext();loaded=true;RebornLocale.init(a);RebornNative.language(RebornLocale.gameId(a));RebornDiagnostics.start(a);if(RebornNative.fallback)a.runOnUiThread(()->android.widget.Toast.makeText(a,"This device could not apply the selected game language. Using English.",android.widget.Toast.LENGTH_LONG).show());}
 public static boolean guard(Activity a){
  if(!loaded||GTAVActivity.isGameRunning())return false;
  new MenuDialogBuilder(a).setTitle(RebornLocale.t("Reopen XHYN V"))
   .setMessage(RebornLocale.t("The previous game used native libraries that remain loaded. Close XHYN V, then open it again before starting another session. Your settings are saved."))
   .setPositiveButton(RebornLocale.t("Close XHYN V"),(d,w)->quit(a,"requested_restart"))
   .setNegativeButton(RebornLocale.t("Cancel"),null).show();return true;
 }
 static boolean mark(Context c,String why){return RebornLocale.prefs(c).edit().putInt("quit_pid",android.os.Process.myPid()).putLong("quit_at",System.currentTimeMillis()).putString("quit_reason",why).commit();}
 static void terminate(Context c,String why){android.content.SharedPreferences p=RebornLocale.prefs(c);boolean requested=p.getInt("quit_pid",-1)==android.os.Process.myPid()&&p.getString("quit_reason","").startsWith("requested_")&&System.currentTimeMillis()-p.getLong("quit_at",0)<=15000;if(!requested)mark(c,why);android.os.Process.killProcess(android.os.Process.myPid());}
 static void quit(Activity a,String why){
  Context c=a.getApplicationContext();if(!mark(c,why)){RebornMenu.error(a,new IllegalStateException("Cannot save the exit marker. Please try again."));return;}
  RebornDiagnostics.event("intentional_quit",why);a.finishAffinity();
  new Handler(Looper.getMainLooper()).postDelayed(()->terminate(c,why),100);
 }
 public static boolean join(Activity a,Thread thread){
  try{thread.join(750);}catch(InterruptedException e){Thread.currentThread().interrupt();}
  if(!thread.isAlive())return true;
  RebornDiagnostics.event("shutdown_timeout","SDL thread still running after 750 ms");
  Context c=a.getApplicationContext();new Handler(Looper.getMainLooper()).postDelayed(()->terminate(c,"shutdown_timeout"),100);return false;
 }
 public static void arm(Activity a){
  if(!loaded)return;Context c=a.getApplicationContext();closing.set(true);
  Thread watchdog=new Thread(()->{try{Thread.sleep(2500);}catch(InterruptedException ignored){}if(closing.get())terminate(c,"cleanup_timeout");},"Reborn-shutdown");watchdog.setDaemon(true);watchdog.start();
 }
 public static void closed(){closing.set(false);Thread stop=new Thread(()->RebornDiagnostics.stop(),"Reborn-session-stop");stop.setDaemon(true);stop.start();}
 public static void mainResult(int code){RebornDiagnostics.event("native_main_return",Integer.toString(code));RebornDiagnostics.nativeReturn(code);}
}
