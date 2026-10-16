#!/usr/bin/env python3
"""Run the production helpers on the JVM with isolated Android service fixtures.
No Android UI, GPU, native loading, or device performance is simulated.
"""
from pathlib import Path
import subprocess,shutil,json
R=Path(__file__).resolve().parents[1];B=R/'build/runtime-tests';SDK=R.parent/'recovered/hotfix2/extracted/XHYN-V-r30-Hotfix2/toolchain/android-ui'
if B.exists():shutil.rmtree(B)
src=B/'src';classes=B/'classes';classes.mkdir(parents=True)
fixtures={
'android/content/SharedPreferences.java':'''package android.content;
public interface SharedPreferences {
 String getString(String k,String d); int getInt(String k,int d);long getLong(String k,long d);boolean getBoolean(String k,boolean d);Editor edit();
 interface Editor {Editor putString(String k,String v);Editor putInt(String k,int v);Editor putLong(String k,long v);Editor putBoolean(String k,boolean v);boolean commit();void apply();}
}''',
'android/content/Context.java':'''package android.content;import java.io.*;import android.content.res.AssetManager;
public abstract class Context {public static final int MODE_PRIVATE=0;public abstract SharedPreferences getSharedPreferences(String n,int m);public abstract File getFilesDir();public abstract AssetManager getAssets();public Context getApplicationContext(){return this;}public String getPackageName(){return "com.xhynph.xhynv.reborn";}public Object getSystemService(String name){return null;}}
''',
'android/content/res/AssetManager.java':'''package android.content.res;import java.io.*;public class AssetManager {private final File dir;public AssetManager(File d){dir=d;}public InputStream open(String name)throws IOException{return new FileInputStream(new File(dir,name));}}''',
'android/os/Build.java':'''package android.os;public class Build {public static String FINGERPRINT="host-fixture",MANUFACTURER="fixture",MODEL="fixture";public static class VERSION {public static String RELEASE="fixture";}}''',
'android/os/SystemClock.java':'''package android.os;public class SystemClock {public static long now;public static long uptimeMillis(){return now;}}''',
'android/os/Process.java':'''package android.os;public class Process {public static int myPid(){return 1234;}}''',
'android/util/Log.java':'''package android.util;public class Log {public static int w(String tag,String msg,Throwable e){return 0;}public static int e(String tag,String msg,Throwable e){return 0;}}''',
'android/system/Os.java':'''package android.system;import java.util.*;public class Os {public static final Map<String,String> env=new HashMap<>();public static void setenv(String k,String v,boolean overwrite){if(overwrite||!env.containsKey(k))env.put(k,v);}public static String getenv(String k){return env.get(k);}public static void unsetenv(String k){env.remove(k);}}''',
'android/app/ApplicationExitInfo.java':'''package android.app;public final class ApplicationExitInfo {private int pid,reason,status;private long time;private String process;public ApplicationExitInfo(int p,int r,int s,long t,String name){pid=p;reason=r;status=s;time=t;process=name;}public int getPid(){return pid;}public int getReason(){return reason;}public int getStatus(){return status;}public long getTimestamp(){return time;}public String getProcessName(){return process;}}''',
'com/gtavsource/android/RuntimeConfig.java':'''package com.gtavsource.android;import java.io.*;import java.util.*;public final class RuntimeConfig {public static File GAME_ROOT;public File root,file,drivers;public final Map<String,String> values=new HashMap<>();public String get(String s,String k,String d){return values.getOrDefault(s+"."+k,d);}public boolean getBoolean(String s,String k,boolean d){return Boolean.parseBoolean(get(s,k,Boolean.toString(d)));}}''',
'com/gtavsource/android/RuntimeAudit.java':r'''package com.gtavsource.android;
import android.content.*;import android.content.res.*;import android.app.*;import android.os.SystemClock;import android.system.Os;import java.io.*;import java.nio.file.*;import java.util.*;
public class RuntimeAudit {
 static int checks;static void check(boolean value,String name){if(!value)throw new AssertionError(name);checks++;System.out.println("PASS "+name);}
 interface Action{void run()throws Exception;}static void rejects(Action a,String name)throws Exception{try{a.run();}catch(Exception e){check(true,name);return;}throw new AssertionError(name);}
 static final class Prefs implements SharedPreferences,SharedPreferences.Editor {
  Map<String,Object> values=new HashMap<>();public String getString(String k,String d){return (String)values.getOrDefault(k,d);}public int getInt(String k,int d){return (Integer)values.getOrDefault(k,d);}public long getLong(String k,long d){return (Long)values.getOrDefault(k,d);}public boolean getBoolean(String k,boolean d){return (Boolean)values.getOrDefault(k,d);}public Editor edit(){return this;}public Editor putString(String k,String v){values.put(k,v);return this;}public Editor putInt(String k,int v){values.put(k,v);return this;}public Editor putLong(String k,long v){values.put(k,v);return this;}public Editor putBoolean(String k,boolean v){values.put(k,v);return this;}public boolean commit(){return true;}public void apply(){}
 }
 static final class C extends Context {final File files,assets;final Prefs prefs=new Prefs();C(File f,File a){files=f;assets=a;files.mkdirs();}public SharedPreferences getSharedPreferences(String n,int m){return prefs;}public File getFilesDir(){return files;}public AssetManager getAssets(){return new AssetManager(assets);}}
 public static void main(String[] args)throws Exception {
  File work=new File(args[0]),assets=new File(args[1]);work.mkdirs();C c=new C(new File(work,"private"),assets);
  RuntimeConfig cfg=new RuntimeConfig();cfg.root=RuntimeConfig.GAME_ROOT=new File(work,"game");cfg.file=new File(cfg.root,"Config/android.ini");cfg.drivers=new File(cfg.root,"Drivers");cfg.drivers.mkdirs();RebornFiles.atomic(cfg.file,"[vulkan]\ndriver=system\n");
  int[] ids={0,1,2,3,4,5,6,7,9,10,11,12,13,1,1,1,1};String[] codes={"zh-TW","en","fr","de","it","ja","ko","pl","pt","ru","es","es-mx","zh","fil","id","tr","vi"};for(int i=0;i<ids.length;i++)check(RebornLocale.gameId(codes[i])==ids[i],"game mapping "+codes[i]);
  Locale.setDefault(new Locale("es","MX"));check(RebornLocale.resolved(c).equals("es-mx")&&RebornLocale.gameId(c)==1,"device menu language keeps game English until explicit choice");
  c.prefs.putString("menu_language","es").commit();RebornLocale.init(c);check(RebornLocale.gameId(c)==11,"explicit menu selection reaches game mapping");check(!RebornLocale.t("Cancel").equals("Cancel"),"real Spanish bundle loads");check(RebornLocale.t("unmapped text").equals("unmapped text"),"unmapped menu text falls back to English");
  c.prefs.putString("menu_language","zh-TW");RebornLocale.init(c);check(RebornLocale.t("Cancel").equals("Cancel"),"absent UI bundle falls back to English");
  check(RebornConfig.effective(c,cfg).contains("dxvk.numCompilerThreads = 2"),"two workers remain the base default");c.prefs.putInt("workers",0);check(RebornConfig.effective(c,cfg).contains("dxvk.numCompilerThreads = 0"),"Auto emits renderer worker value zero");
  String original="dxvk.numCompilerThreads = 4\ndxvk.hud = fps,version\n";RebornConfig.saveEditor(c,original,true);check(RebornConfig.effective(c,cfg).contains(original),"enabled custom document is included after managed workers");
  RebornConfig.saveEditor(c,"dxvk.numCompilerThreads = 6\n",false);check(RebornFiles.read(RebornConfig.snapshot(),65536).equals(original),"disabled snapshot contains the last enabled document");
  RebornConfig.saveEditor(c,"dxvk.numCompilerThreads = 8\n",false);check(RebornFiles.read(RebornConfig.snapshot(),65536).equals(original),"editing while disabled preserves the snapshot");check(!RebornConfig.effective(c,cfg).contains("dxvk.numCompilerThreads = 8"),"disabled document is excluded from effective config");
  rejects(()->RebornConfig.saveEditor(c,"dxvk.numCompilerThreads = 99",true),"out-of-range worker count rejected");check(!c.prefs.getBoolean("conf_enabled",false),"failed edit does not enable custom options");
  check(RebornConfig.validate("dxvk.numCompilerThreads = \"4\"\t# comment").contains("\"4\""),"native quoted worker syntax accepted");
  rejects(()->RebornConfig.validate("d3d9.presentInterval = 1"),"D3D9-only option rejected");rejects(()->RebornConfig.validate("dxvk.gtaAsyncInterop = False"),"uncoordinated interop override rejected");rejects(()->RebornFiles.utf8(new byte[]{(byte)0xc0,(byte)0xaf}),"invalid UTF-8 rejected");
  RebornConfig.prepare(c,cfg);check(Os.env.containsKey("DXVK_CONFIG")&&Os.getenv("DXVK_CONFIG").isEmpty(),"engine hardcoded worker fallback is bypassed");File effective=new File(Os.getenv("DXVK_CONFIG_FILE"));check(effective.isAbsolute()&&effective.isFile(),"effective configuration has a real absolute path");check(Os.getenv("DXVK_LOG_LEVEL").equals("none"),"renderer logging defaults to off");String first=Os.getenv("DXVK_SHADER_CACHE_PATH");check(first.equals(Os.getenv("DXVK_STATE_CACHE_PATH"))&&new File(first).isDirectory(),"persistent renderer cache directories exist");
  cfg.values.put("vulkan.driver","custom");cfg.values.put("vulkan.driver_zip","driver.zip");RebornFiles.atomic(new File(cfg.drivers,"driver.zip"),"first-driver");rejects(()->RebornConfig.prepare(c,cfg),"changing an initialized driver requires a fresh process");RebornConfig.cacheIdentity=null;RebornConfig.pinnedDriver=null;RebornConfig.prepare(c,cfg);String driver1=Os.getenv("DXVK_SHADER_CACHE_PATH");RebornConfig.cacheIdentity=null;RebornConfig.pinnedDriver=null;RebornFiles.atomic(new File(cfg.drivers,"driver.zip"),"second-driver");RebornConfig.prepare(c,cfg);check(!driver1.equals(Os.getenv("DXVK_SHADER_CACHE_PATH")),"different driver bytes get different cache identities");
  RebornConfig.driverReady(c,cfg,"custom ready 0xabcdef012345\nsurface 1");String actual=Os.getenv("DXVK_SHADER_CACHE_PATH");RebornConfig.driverReady(c,cfg,"custom ready 0x123456abcdef\nsurface 2");check(actual.equals(Os.getenv("DXVK_SHADER_CACHE_PATH")),"volatile addresses and status tail do not invalidate renderer cache");RebornConfig.driverReady(c,cfg,"system fallback");check(!actual.equals(Os.getenv("DXVK_SHADER_CACHE_PATH")),"actual system fallback does not share custom driver cache");
  check(RebornDiagnostics.unexpected(3,0,c.getPackageName(),c.getPackageName()),"low-memory exit is reportable");check(RebornDiagnostics.unexpected(2,9,c.getPackageName(),c.getPackageName()),"unexplained SIGKILL is reportable");check(!RebornDiagnostics.unexpected(5,11,c.getPackageName()+":vulkan_probe",c.getPackageName()),"isolated probe failure is excluded");check(!RebornDiagnostics.unexpected(1,0,c.getPackageName(),c.getPackageName()),"normal self exit is excluded");
  check(RebornDiagnostics.intentional(7,2,9,10010,7,10000),"explicit quit marker matches only immediate SIGKILL");check(!RebornDiagnostics.intentional(7,5,11,10010,7,10000),"quit marker cannot hide a native fault");check(!RebornDiagnostics.intentional(7,2,9,30000,7,10000),"stale quit marker cannot hide a later termination");check(!RebornDiagnostics.intentional(8,2,9,10010,7,10000),"different PID is not suppressed");
  c.prefs.putInt("quit_pid",7).putLong("quit_at",10000).putString("quit_reason","cleanup_timeout");check(RebornDiagnostics.isFailure(new ApplicationExitInfo(7,2,9,10010,c.getPackageName())),"automatic cleanup timeout remains reportable");c.prefs.putString("quit_reason","requested_quit");check(!RebornDiagnostics.isFailure(new ApplicationExitInfo(7,2,9,10010,c.getPackageName())),"only an explicit requested quit is suppressed");
  SystemClock.now=0;check(RebornWarmup.accept(0,100,false,true,false),"first preparation state is posted");SystemClock.now=1;check(!RebornWarmup.accept(1,100,false,true,false),"rapid redundant progress is coalesced");check(RebornWarmup.accept(100,100,false,true,false),"completion bypasses throttling");check(RebornWarmup.accept(100,100,false,false,false),"hide/state transition bypasses throttling");
  Path link=new File(work,"link.txt").toPath();Files.createSymbolicLink(link,effective.toPath());rejects(()->RebornFiles.atomic(link.toFile(),"bad"),"atomic write refuses symbolic-link destinations");
  RebornDiagnostics.event("host_fixture","not real device performance");File zip=RebornDiagnostics.export(c);check(zip.isFile()&&zip.length()>0,"bounded local diagnostic export succeeds");
  System.out.println("TOTAL "+checks+" host checks; Android services are fixtures");
 }
}'''
}
for name,contents in fixtures.items():
 p=src/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(contents)
classpath=str(R/'build/helpers/classes')+':'+str(SDK/'json.jar')+':'+str(SDK/'android.jar')
subprocess.run(['java','com.sun.tools.javac.Main','--release','8','-encoding','UTF-8','-cp',classpath,'-d',str(classes)]+list(map(str,src.rglob('*.java'))),check=True)
result=subprocess.run(['java','-cp',str(classes)+':'+classpath,'com.gtavsource.android.RuntimeAudit',str(B/'run'),str(R/'decoded/assets')],capture_output=True,text=True)
(R/'reports/runtime-tests.txt').write_text(result.stdout+result.stderr);print(result.stdout);print(result.stderr);result.check_returncode()
