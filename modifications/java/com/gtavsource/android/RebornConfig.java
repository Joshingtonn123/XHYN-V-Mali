package com.gtavsource.android;
import android.app.*;
import android.content.*;
import android.os.Build;
import android.system.Os;
import java.io.*;
import java.util.*;

/** One effective DXVK document, applied before the first driver is initialized. */
public final class RebornConfig {
 static String cacheIdentity;
 static String pinnedDriver;
 static String lastEffective="";
 static File custom(){return new File(RuntimeConfig.GAME_ROOT,"Config/reborn-dxvk.conf");}
 static File snapshot(){return new File(RuntimeConfig.GAME_ROOT,"Config/reborn-dxvk.conf.disabled");}
 static String readCustom()throws IOException{return custom().isFile()?RebornFiles.read(custom(),65536):"# Custom DXVK options; enable the switch to use this document.\n";}
 static String validate(String source)throws IOException{
  if(source.getBytes(java.nio.charset.StandardCharsets.UTF_8).length>65536||source.indexOf('\0')>=0)throw new IOException("DXVK configuration exceeds 64 KiB or contains invalid text");
  int line=0;for(String raw:source.split("\n",-1)){line++;String s=raw.trim();if(s.isEmpty()||s.startsWith("#")||s.startsWith(";"))continue;
   int p=s.indexOf('=');if(p<=0||!s.substring(0,p).trim().matches("[A-Za-z][A-Za-z0-9_.]*")||s.substring(p+1).trim().isEmpty())throw new IOException("DXVK line "+line+": use option.name = value");
   String k=s.substring(0,p).trim(),v=s.substring(p+1).trim();if(k.startsWith("d3d9."))throw new IOException("DXVK line "+line+": this is a D3D11 game; remove "+k);
   if(k.equals("dxvk.gtaAsyncInterop")||k.equals("dxvk.gtaDescriptorCache")||k.equals("dxvk.gtaDescriptorCacheStats"))throw new IOException("DXVK line "+line+": change "+k+" through the coordinated engine settings in android.ini, not this document");
   if(k.equals("dxvk.numCompilerThreads")){String token=v.split("[ \\t#;]",2)[0];if(token.length()>1&&token.startsWith("\"")&&token.endsWith("\""))token=token.substring(1,token.length()-1);try{int n=Integer.parseInt(token);if(n<0||n>8)throw new NumberFormatException();}catch(NumberFormatException e){throw new IOException("DXVK line "+line+": compiler workers must be 0 (Auto) through 8");}}
  }return source.endsWith("\n")?source:source+"\n";
 }
 static void saveCustom(String source)throws IOException {RebornFiles.atomic(custom(),validate(source));}
 static void saveEditor(Context c,String source,boolean on)throws IOException {
  String valid=validate(source);
  if(RebornLocale.prefs(c).getBoolean("conf_enabled",false)&&!on)RebornFiles.atomic(snapshot(),readCustom());
  saveCustom(valid);
  if(!RebornLocale.prefs(c).edit().putBoolean("conf_enabled",on).commit())throw new IOException("Cannot save the DXVK configuration switch");
 }
 static String effective(Context c,RuntimeConfig config)throws IOException{
  int workers=RebornLocale.prefs(c).getInt("workers",2);if(workers<0||workers>8)workers=2;
  StringBuilder out=new StringBuilder("# XHYN V: applied at the next full launch\n");
  out.append("dxvk.numCompilerThreads = ").append(workers).append('\n');
  out.append("dxvk.gtaAsyncInterop = ").append(config.getBoolean("vulkan","dxvk_async_interop",true)?"True":"False").append('\n');
  out.append("dxvk.gtaDescriptorCache = ").append(config.getBoolean("vulkan","dxvk_descriptor_cache",false)?"True":"False").append('\n');
  out.append("dxvk.gtaDescriptorCacheStats = ").append(config.getBoolean("vulkan","dxvk_descriptor_cache_stats",false)?"True":"False").append('\n');
  if(RebornLocale.prefs(c).getBoolean("conf_enabled",false))out.append("\n# Enabled custom options override the settings above\n").append(validate(readCustom()));
  return out.toString();
 }
 static String identity(Context c,RuntimeConfig config)throws Exception {
  String selection=config.get("vulkan","driver","system")+"\n"+config.get("vulkan","driver_zip","");
  if(pinnedDriver!=null&&!pinnedDriver.equals(selection))throw new IOException("The driver is already initialized. Close XHYN V completely and reopen it to change drivers.");
  if(cacheIdentity!=null)return cacheIdentity;
  String bundle;try(InputStream in=c.getAssets().open("reborn-binary-fingerprints.json")){bundle=RebornFiles.utf8(RebornFiles.bytes(in,65536));}
  String driver=config.get("vulkan","driver","system");String key=bundle+"\n"+Build.FINGERPRINT;
  if(driver.equals("custom")){
   String name=config.get("vulkan","driver_zip","");File root=config.drivers.getCanonicalFile(),file=new File(root,name).getCanonicalFile();
   if(!file.getPath().startsWith(root.getPath()+File.separator)||!file.isFile())throw new IOException("Selected driver ZIP is missing or outside Drivers");
   key+="\n"+RebornFiles.sha(file);
  }else key+="\nsystem";
  cacheIdentity=RebornFiles.sha(key);pinnedDriver=selection;return cacheIdentity;
 }
 public static synchronized void prepare(Context c,RuntimeConfig config){
  if(config==null)throw new IllegalStateException("Game configuration is unavailable");
  try{
   String effective=effective(c,config);File target=new File(c.getFilesDir(),"reborn-effective-dxvk.conf");if(!effective.equals(lastEffective)){RebornFiles.atomic(target,effective);lastEffective=effective;}
   // Verified in this engine: a non-null DXVK_CONFIG bypasses all eight hardcoded
   // compiler-thread defaults. DXVK_CONFIG_FILE then supplies the complete file.
   Os.setenv("DXVK_CONFIG","",true);Os.setenv("DXVK_CONFIG_FILE",target.getCanonicalPath(),true);
   File cache=RebornFiles.directory(RebornFiles.directory(c.getFilesDir(),"reborn-cache"),identity(c,config));
   Os.setenv("DXVK_STATE_CACHE_PATH",cache.getCanonicalPath(),true);Os.setenv("DXVK_SHADER_CACHE_PATH",cache.getCanonicalPath(),true);
   Os.setenv("DXVK_WSI_DRIVER","SDL2",true);
   boolean logs=RebornLocale.prefs(c).getBoolean("renderer_logs",false);
   File reports=RebornFiles.directory(config.root,"Config/Reborn");
   Os.setenv("DXVK_LOG_LEVEL",logs?"info":"none",true);Os.setenv("DXVK_LOG_PATH",logs?reports.getCanonicalPath():"none",true);
   RebornDiagnostics.init(c);RebornDiagnostics.prepared(c,config,effective,cacheIdentity);
  }catch(Exception e){throw new IllegalStateException("Cannot prepare the DXVK configuration: "+e.getMessage(),e);}
 }
 public static synchronized void driverReady(Context c,RuntimeConfig config,String status){
  try{String stableStatus=status==null?"unknown":status.split("\n",2)[0].replaceAll("0x[0-9a-fA-F]{10,16}","<address>");String actual=RebornFiles.sha(identity(c,config)+"\n"+stableStatus);File cache=RebornFiles.directory(RebornFiles.directory(c.getFilesDir(),"reborn-cache"),actual);
   Os.setenv("DXVK_STATE_CACHE_PATH",cache.getCanonicalPath(),true);Os.setenv("DXVK_SHADER_CACHE_PATH",cache.getCanonicalPath(),true);
   RebornDiagnostics.prepared(c,config,lastEffective,actual);RebornDiagnostics.event("driver_ready",status);
  }catch(Exception e){throw new IllegalStateException("Cannot finish renderer cache setup: "+e.getMessage(),e);}
 }
}
