package com.gtavsource.android;
import android.os.SystemClock;

/** Coalesce progress notifications; always pass state changes and completion. */
public final class RebornWarmup {
 private static long last;private static int flags=-1,lastDone=-1,lastTotal=-1;
 public static synchronized boolean accept(int done,int total,boolean a,boolean b,boolean c){
  int state=(a?1:0)|(b?2:0)|(c?4:0);long now=SystemClock.uptimeMillis();
  boolean terminal=total>0&&done>=total&&(done!=lastDone||total!=lastTotal);
  if(state!=flags||terminal||now-last>=100){flags=state;last=now;lastDone=done;lastTotal=total;return true;}return false;
 }
}
