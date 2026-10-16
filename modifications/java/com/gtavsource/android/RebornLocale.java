package com.gtavsource.android;
import android.app.*;
import android.content.*;
import android.os.*;
import android.widget.*;
import java.util.*;
import org.json.*;

/** Exact display-boundary translations. User text, control IDs and INI keys stay intact. */
public final class RebornLocale {
 static final String[] CODES={"auto","en","fil","es","es-mx","id","pt","ru","fr","de","it","tr","vi","zh","zh-TW","ja","ko","pl"};
 static final String[] NAMES={"Device language","English","Filipino","Español","Español (México)","Bahasa Indonesia","Português (Brasil)","Русский","Français","Deutsch","Italiano","Türkçe","Tiếng Việt","简体中文","繁體中文","日本語","한국어","Polski"};
 private static volatile Map<String,String> words=Collections.emptyMap();
 private static String loaded="";
 static SharedPreferences prefs(Context c){return c.getSharedPreferences("xhyn-reborn",Context.MODE_PRIVATE);}
 static String requested(Context c){String code=prefs(c).getString("menu_language","auto");return Arrays.asList(CODES).contains(code)?code:"auto";}
 static String device(Locale l){String code=l.getLanguage();if(code.equals("tl"))return "fil";if(code.equals("in"))return "id";
  if(code.equals("zh"))return l.getScript().equals("Hant")||Arrays.asList("TW","HK","MO").contains(l.getCountry())?"zh-TW":"zh";
  if(code.equals("es")&&l.getCountry().equals("MX"))return "es-mx";return Arrays.asList(CODES).contains(code)?code:"en";
 }
 static String resolved(Context c){String s=requested(c);return s.equals("auto")?device(Locale.getDefault()):s;}
 public static synchronized boolean init(Context c){String code=resolved(c);if(code.equals(loaded))return false;
  Map<String,String> next=new HashMap<>();String bundle=code.equals("es-mx")?"es":code;
  if(!code.equals("en"))try(java.io.InputStream in=c.getAssets().open("xhyn-locale-"+bundle+".json")){
   JSONObject json=new JSONObject(RebornFiles.utf8(RebornFiles.bytes(in,2*1024*1024)));
   for(Iterator<String> i=json.keys();i.hasNext();){String key=i.next();String v=json.optString(key,"");if(!v.isEmpty())next.put(key,v);}
  }catch(Exception ignored){}words=Collections.unmodifiableMap(next);loaded=code;return true;
 }
 public static String t(String s){if(s==null||words.isEmpty())return s;String value=words.get(s);if(value!=null)return value;
  for(String sep:new String[]{"\n",": "," · "})if(s.contains(sep)){String[] parts=s.split(java.util.regex.Pattern.quote(sep),-1);for(int i=0;i<parts.length;i++)parts[i]=t(parts[i]);return String.join(sep,parts);}return s;
 }
 static CharSequence cs(CharSequence s){return s==null?null:t(s.toString());}
 static CharSequence[] array(CharSequence[] a){if(a==null)return null;CharSequence[] b=a.clone();for(int i=0;i<a.length;i++)b[i]=cs(a[i]);return b;}
 public static void text(TextView view,CharSequence value){view.setText(view instanceof EditText?value:cs(value));}
 public static void hint(TextView view,CharSequence value){view.setHint(cs(value));}
 public static void description(android.view.View view,CharSequence value){view.setContentDescription(cs(value));}
 public static void progress(ProgressDialog dialog,CharSequence value){dialog.setMessage(cs(value));}
 public static Toast toast(Context c,CharSequence value,int time){return Toast.makeText(c,cs(value),time);}
 public static AlertDialog.Builder title(AlertDialog.Builder b,CharSequence v){return b.setTitle(cs(v));}
 public static AlertDialog.Builder message(AlertDialog.Builder b,CharSequence v){return b.setMessage(cs(v));}
 public static AlertDialog.Builder positive(AlertDialog.Builder b,CharSequence v,DialogInterface.OnClickListener l){return b.setPositiveButton(cs(v),l);}
 public static AlertDialog.Builder negative(AlertDialog.Builder b,CharSequence v,DialogInterface.OnClickListener l){return b.setNegativeButton(cs(v),l);}
 public static AlertDialog.Builder neutral(AlertDialog.Builder b,CharSequence v,DialogInterface.OnClickListener l){return b.setNeutralButton(cs(v),l);}
 public static AlertDialog.Builder items(AlertDialog.Builder b,CharSequence[] v,DialogInterface.OnClickListener l){return b.setItems(array(v),l);}
 public static AlertDialog.Builder single(AlertDialog.Builder b,CharSequence[] v,int n,DialogInterface.OnClickListener l){return b.setSingleChoiceItems(array(v),n,l);}
 public static AlertDialog.Builder multi(AlertDialog.Builder b,CharSequence[] v,boolean[] n,DialogInterface.OnMultiChoiceClickListener l){return b.setMultiChoiceItems(array(v),n,l);}
 static String selectedGameCode(Context c){String code=requested(c);return code.equals("auto")?"en":code;}
 static int gameId(Context c){return gameId(selectedGameCode(c));}
 static int gameId(String code){switch(code){case "zh-TW":return 0;case "fr":return 2;case "de":return 3;case "it":return 4;case "ja":return 5;case "ko":return 6;case "pl":return 7;case "pt":return 9;case "ru":return 10;case "es":return 11;case "es-mx":return 12;case "zh":return 13;default:return 1;}}
 static String archive(int id){return new String[]{"chinese","american","french","german","italian","japanese","korean","polish","portuguese","portuguese","russian","spanish","mexican","chinesesimp"}[id];}
 static void choose(Activity a){String current=requested(a);new MenuDialogBuilder(a).setTitle("Menu and game language").setSingleChoiceItems(NAMES,Math.max(0,Arrays.asList(CODES).indexOf(current)),(d,n)->{
   prefs(a).edit().putString("menu_language",CODES[n]).commit();init(a);d.dismiss();a.recreate();
  }).setNeutralButton("About languages",(d,n)->RebornMenu.notice(a,"Menu and game language","Supported game languages follow an explicit menu selection on the next full launch. Device language and unsupported game languages use English in game. Missing menu translations also use English. The corresponding game text and fonts must be installed.")).setNegativeButton(t("Cancel"),null).show();
 }
 public static void resume(Activity a){boolean changed=init(a);if(changed)a.recreate();}
}
