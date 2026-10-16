package com.gtavsource.android;
import android.app.Activity;
import android.view.*;

public final class RebornDisplay {
 public static void apply(Activity a){
  try{Display display=a.getWindowManager().getDefaultDisplay();Display.Mode current=display.getMode();
   String policy=RebornLocale.prefs(a).getString("refresh","auto");WindowManager.LayoutParams p=a.getWindow().getAttributes();
   if(policy.equals("auto")){p.preferredDisplayModeId=0;p.preferredRefreshRate=0;}
   else{Display.Mode best=current;
    for(Display.Mode m:display.getSupportedModes()){
     if(m.getPhysicalWidth()!=current.getPhysicalWidth()||m.getPhysicalHeight()!=current.getPhysicalHeight())continue;
     if(policy.equals("high")?m.getRefreshRate()>best.getRefreshRate():Math.abs(m.getRefreshRate()-60)<Math.abs(best.getRefreshRate()-60))best=m;
    }p.preferredDisplayModeId=best.getModeId();p.preferredRefreshRate=best.getRefreshRate();
   }a.getWindow().setAttributes(p);
  }catch(RuntimeException e){android.util.Log.w("XHYN-V","Display mode request was not accepted",e);}
 }
}
