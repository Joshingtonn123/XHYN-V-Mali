package com.gtavsource.android;
import java.io.*;
public final class RuntimeConfig {
 public static File GAME_ROOT; public File root,file,drivers;
 public static RuntimeConfig load(File root)throws IOException{return null;}
 public String get(String section,String key,String fallback){return fallback;}
 public boolean getBoolean(String section,String key,boolean fallback){return fallback;}
 public void put(String section,String key,String value){} public void save()throws IOException{}
}
