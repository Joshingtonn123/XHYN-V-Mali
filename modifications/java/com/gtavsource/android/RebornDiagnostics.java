package com.gtavsource.android;
import android.app.*;
import android.content.*;
import android.os.*;
import org.json.*;
import java.io.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.zip.*;

/** Bounded local session records. Frame-count intervals are not frame-time percentiles. */
public final class RebornDiagnostics {
 private static Context app;
 private static final ArrayDeque<JSONObject> ring=new ArrayDeque<>();
 private static ScheduledExecutorService executor;
 private static JSONObject header=new JSONObject();
 private static long startNanos,lastNanos,lastFrames;
 private static int sampleCount;
 private static boolean benchmark;
 private static boolean archived;
 static synchronized void init(Context c){app=c.getApplicationContext();}
 static File directory()throws IOException{return RebornFiles.directory(RuntimeConfig.GAME_ROOT,"Config/Reborn");}
 static synchronized void prepared(Context c,RuntimeConfig config,String effective,String identity)throws Exception {
  init(c);
  if(!archived){for(String name:new String[]{"launch.json","session.jsonl"}){File previous=new File(directory(),name);if(previous.isFile())RebornFiles.atomic(new File(directory(),"previous-"+name),RebornFiles.read(previous,262144));}archived=true;}
  header=new JSONObject();header.put("format",1).put("build","0.1").put("pid",android.os.Process.myPid())
   .put("device",Build.MANUFACTURER+" "+Build.MODEL).put("android",Build.VERSION.RELEASE).put("fingerprint",Build.FINGERPRINT)
   .put("cache_identity",identity).put("driver",config.get("vulkan","driver","system")).put("driver_zip",config.get("vulkan","driver_zip",""))
   .put("menu_language",RebornLocale.requested(c)).put("game_language",RebornLocale.archive(RebornLocale.gameId(c)))
   .put("previous_stop_reason",RebornLocale.prefs(c).getString("quit_reason","unknown"))
   .put("effective_dxvk",effective).put("frame_measurement","native frame count over five-second intervals; not frame-time percentiles")
   .put("ini",RebornFiles.read(config.file,65536));
  RebornFiles.atomic(new File(directory(),"effective-dxvk.conf"),effective);
  RebornFiles.atomic(new File(directory(),"launch.json"),header.toString(2)+"\n");
 }
 public static synchronized void start(Context c){
  init(c);if(executor!=null)return;
  startNanos=lastNanos=System.nanoTime();lastFrames=-1;sampleCount=0;ring.clear();benchmark=RebornLocale.prefs(c).getBoolean("benchmark_next",false);
  try{header.put("applied_game_language",RebornLocale.archive(RebornNative.applied)).put("language_fallback",RebornNative.fallback);}catch(JSONException ignored){}
  RebornLocale.prefs(c).edit().putBoolean("benchmark_next",false).apply();event("session_start",benchmark?"10-minute comparison requested":"normal launch");
  executor=Executors.newSingleThreadScheduledExecutor(r->{Thread t=new Thread(r,"Reborn-session");t.setDaemon(true);return t;});executor.scheduleAtFixedRate(()->sample(),0,5,TimeUnit.SECONDS);
 }
 private static void readCounters(JSONObject o){
  for(String name:new String[]{"/proc/meminfo","/proc/vmstat","/proc/self/stat"})try{
   String data=RebornFiles.read(new File(name),16384);
   if(name.endsWith("meminfo")){for(String l:data.split("\n"))if(l.startsWith("MemAvailable:")||l.startsWith("SwapFree:")||l.startsWith("SwapTotal:")){String[] p=l.trim().split("\\s+");o.put(p[0].replace(":",""),Long.parseLong(p[1]));}}
   else if(name.endsWith("vmstat")){for(String l:data.split("\n"))if(l.startsWith("pgmajfault ")||l.startsWith("pswpin ")||l.startsWith("pswpout ")){String[] p=l.trim().split("\\s+");o.put(p[0],Long.parseLong(p[1]));}}
   else{int close=data.lastIndexOf(')');if(close>=0){String[] p=data.substring(close+2).trim().split("\\s+");if(p.length>9)o.put("process_major_faults",Long.parseLong(p[9]));}}
  }catch(Exception ignored){}
 }
 private static void sample(){
  try{long now=System.nanoTime();JSONObject o=new JSONObject().put("event","sample").put("elapsed_s",(now-startNanos)/1e9);
   Debug.MemoryInfo memory=new Debug.MemoryInfo();Debug.getMemoryInfo(memory);o.put("pss_kib",memory.getTotalPss()).put("private_dirty_kib",memory.getTotalPrivateDirty());
   PowerManager pm=(PowerManager)app.getSystemService(Context.POWER_SERVICE);if(pm!=null)o.put("thermal_status",pm.getCurrentThermalStatus());readCounters(o);
   try{long frames=GameTelemetry.rebornFrameCount();if(lastFrames>=0&&frames>=lastFrames)o.put("frames_per_second_over_interval",(frames-lastFrames)*1e9/(now-lastNanos));lastFrames=frames;}catch(LinkageError ignored){}
   lastNanos=now;add(o);sampleCount++;
   if(benchmark&&now-startNanos>=600000000000L){benchmark=false;event("comparison_target_reached","600 seconds; repeat the same route and graphics settings for another build");}
   if(sampleCount%3==0)flush();
  }catch(Exception e){android.util.Log.w("XHYN-V","Session sample unavailable",e);}
 }
 private static synchronized void add(JSONObject value){while(ring.size()>=180)ring.removeFirst();ring.addLast(value);}
 static synchronized void event(String name,String detail){try{JSONObject o=new JSONObject().put("event",name).put("time_ms",System.currentTimeMillis()).put("detail",detail);add(o);}catch(JSONException ignored){}}
 static void flush(){try{String snapshot;synchronized(RebornDiagnostics.class){StringBuilder b=new StringBuilder(header.toString()).append('\n');for(JSONObject row:ring)b.append(row.toString()).append('\n');snapshot=b.toString();}if(snapshot.length()>262144)throw new IOException("Session record exceeds its limit");RebornFiles.atomic(new File(directory(),"session.jsonl"),snapshot);}catch(Exception e){android.util.Log.w("XHYN-V","Cannot save the session record",e);}}
 static void stop(){synchronized(RebornDiagnostics.class){if(executor!=null){executor.shutdownNow();executor=null;}}flush();}
 static void nativeReturn(int result){if(app!=null)RebornLocale.prefs(app).edit().putInt("native_main_result",result).putLong("native_main_result_at",System.currentTimeMillis()).commit();flush();}
 public static boolean unexpected(int reason,int status,String process,String packageName){
  if(!packageName.equals(process))return false;
  return reason==ApplicationExitInfo.REASON_LOW_MEMORY||reason==ApplicationExitInfo.REASON_CRASH||reason==ApplicationExitInfo.REASON_CRASH_NATIVE||reason==ApplicationExitInfo.REASON_ANR||reason==ApplicationExitInfo.REASON_SIGNALED||(reason==ApplicationExitInfo.REASON_EXIT_SELF&&status!=0);
 }
 static boolean intentional(int pid,int reason,int status,long time,int savedPid,long savedTime){return reason==ApplicationExitInfo.REASON_SIGNALED&&status==9&&pid>0&&pid==savedPid&&savedTime>0&&time>=savedTime&&time-savedTime<=15000;}
 public static boolean isFailure(ApplicationExitInfo info){
  if(app==null)return false;
  if(!unexpected(info.getReason(),info.getStatus(),info.getProcessName(),app.getPackageName()))return false;
  android.content.SharedPreferences p=RebornLocale.prefs(app);
  String why=p.getString("quit_reason","");boolean requested=why.equals("requested_quit")||why.equals("requested_restart");
  return !(requested&&intentional(info.getPid(),info.getReason(),info.getStatus(),info.getTimestamp(),p.getInt("quit_pid",-1),p.getLong("quit_at",0)));
 }
 public static String reasonName(int reason){switch(reason){case 1:return "Native/main process exit";case 2:return "Process terminated by signal (not proof of a native crash)";case 3:return "System low-memory termination";case 4:return "Java exception";case 5:return "Native code crash";case 6:return "Application not responding";default:return "Process exit (reason "+reason+")";}}
 static File export(Context c)throws Exception {
  flush();File dir=directory(),out=new File(dir,"reborn-report-"+System.currentTimeMillis()+".zip");
  try(ZipOutputStream zip=new ZipOutputStream(new FileOutputStream(out))){
   for(String name:new String[]{"launch.json","session.jsonl","previous-launch.json","previous-session.jsonl","effective-dxvk.conf"}){File f=new File(dir,name);if(f.isFile()){zip.putNextEntry(new ZipEntry(name));copyPrefix(f,zip);zip.closeEntry();}}
   for(String name:new String[]{"driver-status.txt","telemetry-status.txt"}){File f=new File(RuntimeConfig.GAME_ROOT,"Config/"+name);if(f.isFile()){zip.putNextEntry(new ZipEntry(name));copyPrefix(f,zip);zip.closeEntry();}}
   File[] captures=new File(RuntimeConfig.GAME_ROOT,"perf").listFiles(f->f.isFile()&&f.getName().endsWith(".jsonl"));
   if(captures!=null){Arrays.sort(captures,(a,b)->Long.compare(b.lastModified(),a.lastModified()));for(int i=0;i<Math.min(4,captures.length);i++){zip.putNextEntry(new ZipEntry("native-perf/"+captures[i].getName()));copyPrefix(captures[i],zip,2097152);zip.closeEntry();}}
   zip.putNextEntry(new ZipEntry("binary-fingerprints.json"));try(InputStream in=c.getAssets().open("reborn-binary-fingerprints.json")){zip.write(RebornFiles.bytes(in,65536));}zip.closeEntry();
  }return out;
 }
 private static void copyPrefix(File f,OutputStream out)throws IOException {copyPrefix(f,out,262144);}
 private static void copyPrefix(File f,OutputStream out,int maximum)throws IOException {try(InputStream in=new FileInputStream(f)){byte[] b=new byte[8192];int remaining=maximum,n;while(remaining>0&&(n=in.read(b,0,Math.min(b.length,remaining)))!=-1){out.write(b,0,n);remaining-=n;}}}
}
