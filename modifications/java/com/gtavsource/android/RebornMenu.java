package com.gtavsource.android;
import android.app.*;
import android.content.*;
import android.graphics.Typeface;
import android.os.*;
import android.text.*;
import android.view.*;
import android.widget.*;
import java.io.*;

/** Launcher-only settings. Editing never mutates a running renderer or game language. */
public final class RebornMenu {
 static void error(Activity a,Throwable e){if(!a.isFinishing()&&!a.isDestroyed())new MenuDialogBuilder(a).setTitle(RebornLocale.t("Cannot complete this action")).setMessage(e.getMessage()==null?e.toString():e.getMessage()).setPositiveButton(RebornLocale.t("Close"),null).show();}
 static void notice(Activity a,String title,String message){new MenuDialogBuilder(a).setTitle(RebornLocale.t(title)).setMessage(RebornLocale.t(message)).setPositiveButton(RebornLocale.t("Close"),null).show();}
 static void work(Activity a,String title,java.util.concurrent.Callable<String> task){
  ProgressDialog progress=new ProgressDialog(a);progress.setMessage(RebornLocale.t(title));progress.setIndeterminate(true);progress.setCancelable(false);progress.show();
  new Thread(()->{String answer=null;Exception failure=null;try{answer=task.call();}catch(Exception e){failure=e;}final String text=answer;final Exception problem=failure;
   a.runOnUiThread(()->{if(a.isDestroyed()||a.isFinishing())return;progress.dismiss();if(problem!=null)error(a,problem);else notice(a,title,text);});},"Reborn-action").start();
 }
 public static void attach(Activity a,LinearLayout content){
  RebornLocale.init(a);RebornDiagnostics.init(a);
  LinearLayout row=new LinearLayout(a);row.setOrientation(LinearLayout.HORIZONTAL);
  Button language=new Button(a);language.setText(RebornLocale.t("Language"));language.setAllCaps(false);language.setOnClickListener(v->RebornLocale.choose(a));
  Button settings=new Button(a);settings.setText("XHYN V");settings.setAllCaps(false);settings.setOnClickListener(v->show(a));
  row.addView(language,new LinearLayout.LayoutParams(0,-2,1));row.addView(settings,new LinearLayout.LayoutParams(0,-2,1));content.addView(row,0);
  android.content.SharedPreferences p=RebornLocale.prefs(a);int result=p.getInt("native_main_result",0);long time=p.getLong("native_main_result_at",0);
  if(result!=0&&time>p.getLong("native_main_result_shown",0)){p.edit().putLong("native_main_result_shown",time).apply();row.post(()->notice(a,"Game stopped","The engine returned code "+result+". Open XHYN V settings and export diagnostics before retrying."));}
 }
 static void show(Activity a){
  android.content.SharedPreferences p=RebornLocale.prefs(a);int workers=p.getInt("workers",2);String[] labels={"Menu and game language","DXVK configuration: "+(p.getBoolean("conf_enabled",false)?"On":"Off"),"Compiler workers: "+(workers==0?"Auto":workers),"Refresh rate: "+p.getString("refresh","auto"),"Measure the next 10-minute session","Export diagnostics","Renderer logs: "+(p.getBoolean("renderer_logs",false)?"On":"Off"),"Renderer options","Queue the built-in benchmark","Close XHYN V"};
  for(int i=0;i<labels.length;i++)labels[i]=RebornLocale.t(labels[i]);
  new MenuDialogBuilder(a).setTitle("XHYN V").setItems(labels,(d,n)->{
   switch(n){case 0:RebornLocale.choose(a);break;case 1:editor(a);break;case 2:workers(a);break;case 3:refresh(a);break;
    case 4:p.edit().putBoolean("benchmark_next",true).commit();notice(a,"Comparison session","The next launch will record memory, swap, thermal status and native frame counts for at least 10 minutes. Repeat the same route and graphics settings when comparing builds. Detailed frame times come from the game's existing benchmark/performance capture.");break;
    case 5:work(a,"Export diagnostics",()->"Saved to "+RebornDiagnostics.export(a).getAbsolutePath());break;
    case 6:p.edit().putBoolean("renderer_logs",!p.getBoolean("renderer_logs",false)).commit();notice(a,"Saved","Applies after closing XHYN V and opening it again.");break;
    case 7:renderer(a);break;
    case 8:work(a,"Benchmark queued",()->{RuntimeConfig config=RuntimeConfig.load(RuntimeConfig.GAME_ROOT);config.put("benchmark","enabled","true");config.put("benchmark","pass","-1");config.put("benchmark","iterations","3");config.put("benchmark","frame_times","true");config.save();p.edit().putBoolean("benchmark_next",true).commit();return "The next full game launch will run the existing benchmark with three iterations and frame capture. Use the same graphics settings for comparisons. After a game session, close XHYN V and reopen it first.";});break;
    case 9:new MenuDialogBuilder(a).setTitle(RebornLocale.t("Close XHYN V?")).setMessage(RebornLocale.t("Save your game before closing. Unsaved progress will be lost.")).setPositiveButton(RebornLocale.t("Close XHYN V"),(x,w)->RebornSession.quit(a,"requested_quit")).setNegativeButton(RebornLocale.t("Cancel"),null).show();break;
   }
  }).setNegativeButton(RebornLocale.t("Close"),null).show();
 }
 static void workers(Activity a){String[] names={"Auto","1","2 (base default)","3","4","6","8"};int[] values={0,1,2,3,4,6,8};int current=RebornLocale.prefs(a).getInt("workers",2),selected=2;for(int i=0;i<values.length;i++)if(values[i]==current)selected=i;
  new MenuDialogBuilder(a).setTitle(RebornLocale.t("Compiler workers")).setSingleChoiceItems(names,selected,(d,n)->{RebornLocale.prefs(a).edit().putInt("workers",values[n]).commit();d.dismiss();notice(a,"Saved","Applies on the next full launch. Enabled custom DXVK options can override this selection.");}).setNegativeButton(RebornLocale.t("Cancel"),null).show();
 }
 static void renderer(Activity a){try{RuntimeConfig config=RuntimeConfig.load(RuntimeConfig.GAME_ROOT);String[] keys={"dxvk_async_interop","dxvk_descriptor_cache","dxvk_descriptor_cache_stats"};boolean[] values={config.getBoolean("vulkan",keys[0],true),config.getBoolean("vulkan",keys[1],false),config.getBoolean("vulkan",keys[2],false)};String[] labels={"Ordered async handoff (base default: On)","Descriptor reuse (experimental; base default: Off)","Cache statistics (diagnostics; base default: Off)"};
  new MenuDialogBuilder(a).setTitle(RebornLocale.t("Renderer options")).setMultiChoiceItems(labels,values,(d,n,on)->values[n]=on).setPositiveButton(RebornLocale.t("Save"),(d,n)->work(a,"Saved",()->{RuntimeConfig fresh=RuntimeConfig.load(RuntimeConfig.GAME_ROOT);for(int i=0;i<keys.length;i++)fresh.put("vulkan",keys[i],Boolean.toString(values[i]));fresh.save();return "Applies on the next full game launch. These are existing renderer features; compare the same scene before keeping experimental changes.";})).setNegativeButton(RebornLocale.t("Cancel"),null).show();
 }catch(Exception e){error(a,e);}}
 static void refresh(Activity a){String[] codes={"auto","60","high"};String[] names={"Auto (Android decides)","60 Hz (nearest available)","Highest at current resolution"};String selected=RebornLocale.prefs(a).getString("refresh","auto");int index=java.util.Arrays.asList(codes).indexOf(selected);
  new MenuDialogBuilder(a).setTitle(RebornLocale.t("Refresh rate")).setSingleChoiceItems(names,Math.max(0,index),(d,n)->{RebornLocale.prefs(a).edit().putString("refresh",codes[n]).commit();d.dismiss();notice(a,"Saved","The display request applies when the game resumes. Android may choose a different rate.");}).setNegativeButton(RebornLocale.t("Cancel"),null).show();
 }
 static void editor(Activity a){
  try{
   LinearLayout box=new LinearLayout(a);box.setOrientation(LinearLayout.VERTICAL);int padding=(int)(16*a.getResources().getDisplayMetrics().density);box.setPadding(padding,padding,padding,padding);
   CheckBox enabled=new CheckBox(a);enabled.setText(RebornLocale.t("Enable custom DXVK configuration"));enabled.setChecked(RebornLocale.prefs(a).getBoolean("conf_enabled",false));box.addView(enabled);
   TextView help=new TextView(a);help.setText(RebornLocale.t("Saved options apply on the next full launch. Turning the switch off preserves the last enabled document as a separate snapshot. Supported DXVK keys are required; unknown keys may be ignored."));box.addView(help);
   EditText input=new EditText(a);input.setTypeface(Typeface.MONOSPACE);input.setTextSize(13);input.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_FLAG_MULTI_LINE|android.text.InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);input.setSingleLine(false);input.setMinLines(7);input.setMaxLines(10);input.setGravity(Gravity.TOP);input.setFilters(new InputFilter[]{new InputFilter.LengthFilter(65536)});input.setText(RebornConfig.readCustom());
   ScrollView scroll=new ScrollView(a);scroll.addView(input);box.addView(scroll);
   AlertDialog dialog=new MenuDialogBuilder(a).setTitle(RebornLocale.t("DXVK configuration")).setView(box).setPositiveButton(RebornLocale.t("Save"),null).setNegativeButton(RebornLocale.t("Cancel"),null).setNeutralButton(RebornLocale.t("Restore disabled snapshot"),null).create();
   dialog.setOnShowListener(v->{dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(button->{try{RebornConfig.saveEditor(a,input.getText().toString(),enabled.isChecked());dialog.dismiss();notice(a,"Saved","Applies after closing XHYN V and opening it again.");}catch(Exception e){error(a,e);}});
    dialog.getButton(AlertDialog.BUTTON_NEUTRAL).setOnClickListener(button->{try{if(!RebornConfig.snapshot().isFile())throw new IOException("No disabled snapshot has been saved yet.");input.setText(RebornFiles.read(RebornConfig.snapshot(),65536));}catch(Exception e){error(a,e);}});
   });dialog.show();
  }catch(Exception e){error(a,e);}
 }
}
