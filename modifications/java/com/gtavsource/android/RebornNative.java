package com.gtavsource.android;

/** Called only after SDL has loaded libgtav, and before nativeRunMain. */
public final class RebornNative {
    private static boolean loaded;
    static int applied=1;
    static boolean fallback;
    public static synchronized void language(int id) {
        // The packaged engine already uses English; its default needs no runtime
        // code permissions or additional shared library.
        if(id==1){applied=1;return;}
        if (!loaded) {try{System.loadLibrary("xhyn_locale");loaded=true;}catch(LinkageError e){fallback=true;RebornDiagnostics.event("language_fallback",e.toString());return;}}
        int result = configure(id);
        if(result==-3||result==-4){fallback=true;RebornDiagnostics.event("language_fallback","Language bridge unavailable: "+result);return;}
        if (result != 0) throw new UnsatisfiedLinkError("Language setup failed ("+result+"). Close XHYN V completely, then reopen it. Use this APK with its bundled engine.");
        applied=id;
    }
    private static native int configure(int language);
}
