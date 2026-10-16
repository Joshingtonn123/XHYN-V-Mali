#!/usr/bin/env python3
"""Guarded integrations for the exact decoded launcher. Run once per fresh decode."""
from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parents[1];D=R/'decoded';S=D/'smali/com/gtavsource/android'
METHOD=re.compile(r'^\.method .*?\n.*?^\.end method',re.M|re.S)
def once(t,a,b):
    assert t.count(a)==1,(a[:140],t.count(a));return t.replace(a,b,1)
def edit(name,sig,fn):
    p=S/(name+'.smali');t=p.read_text();matches=[m for m in METHOD.finditer(t) if m[0].splitlines()[0].split()[-1]==sig]
    assert len(matches)==1,(name,sig,len(matches));m=matches[0];p.write_text(t[:m.start()]+fn(m[0])+t[m.end():])
def before(name,sig,needle,added):edit(name,sig,lambda t:once(t,needle,added+'\n'+needle))
assert not (D/'reborn-hooks.json').exists(),'Do not apply these hooks twice'
P='Lcom/gtavsource/android/'
before('GameMenuActivity','onCreate(Landroid/os/Bundle;)V','    .line 78',f'    invoke-static {{p0}}, {P}RebornLocale;->init(Landroid/content/Context;)Z\n\n    invoke-static {{p0}}, {P}RebornDiagnostics;->init(Landroid/content/Context;)V\n')
edit('GameMenuActivity','onResume()V',lambda t:once(t,'    invoke-super {p0}, Landroid/app/Activity;->onResume()V','    invoke-super {p0}, Landroid/app/Activity;->onResume()V\n\n    invoke-static {p0}, '+P+'RebornLocale;->resume(Landroid/app/Activity;)V'))
before('GameMenuActivity','showPage(I)V','    .line 236',f'    iget-object v2, v0, {P}GameMenuActivity;->content:Landroid/widget/LinearLayout;\n\n    invoke-static {{v0, v2}}, {P}RebornMenu;->attach(Landroid/app/Activity;Landroid/widget/LinearLayout;)V\n')
before('GameMenuActivity','launch()V','    .line 1012',f'    invoke-static {{p0}}, {P}RebornSession;->guard(Landroid/app/Activity;)Z\n\n    move-result v0\n\n    if-eqz v0, :reborn_launch\n\n    return-void\n\n    :reborn_launch\n')
edit('GTAVActivity','loadLibraries()V',lambda t:once(t,'    invoke-super {p0}, Lorg/libsdl/app/SDLActivity;->loadLibraries()V','    invoke-super {p0}, Lorg/libsdl/app/SDLActivity;->loadLibraries()V\n\n    invoke-static {p0}, '+P+'RebornSession;->afterLibraries(Landroid/app/Activity;)V'))
edit('GTAVActivity','enableHighRefreshRate()V',lambda t:'.method private enableHighRefreshRate()V\n    .locals 0\n    invoke-static {p0}, '+P+'RebornDisplay;->apply(Landroid/app/Activity;)V\n    return-void\n.end method')
edit('GTAVActivity','onResume()V',lambda t:once(t,'    invoke-super {p0}, Lorg/libsdl/app/SDLActivity;->onResume()V','    invoke-super {p0}, Lorg/libsdl/app/SDLActivity;->onResume()V\n\n    invoke-static {p0}, '+P+'RebornDisplay;->apply(Landroid/app/Activity;)V'))
before('GTAVActivity','onDestroy()V','    .line 626','    invoke-static {p0}, '+P+'RebornSession;->arm(Landroid/app/Activity;)V\n')
edit('GTAVActivity','onDestroy()V',lambda t:once(t,'    invoke-super {p0}, Lorg/libsdl/app/SDLActivity;->onDestroy()V','    invoke-super {p0}, Lorg/libsdl/app/SDLActivity;->onDestroy()V\n\n    invoke-static {}, '+P+'RebornSession;->closed()V'))
before('GTAVActivity','setShaderPreparationPhase(IIZZZ)V','    .line 648','    invoke-static {p1, p2, p3, p4, p5}, '+P+'RebornWarmup;->accept(IIZZZ)Z\n\n    move-result v0\n\n    if-nez v0, :reborn_progress\n\n    return-void\n\n    :reborn_progress\n')
edit('DriverManager','prepare(Landroid/content/Context;Lcom/gtavsource/android/RuntimeConfig;)Ljava/lang/String;',lambda t:once(t,'    :try_start_0','    :try_start_0\n    invoke-static {p0, p1}, '+P+'RebornConfig;->prepare(Landroid/content/Context;Lcom/gtavsource/android/RuntimeConfig;)V\n'))
edit('DriverManager','prepare(Landroid/content/Context;Lcom/gtavsource/android/RuntimeConfig;)Ljava/lang/String;',lambda t:once(t,'    move-result-object p0','    move-result-object v1\n\n    invoke-static {p0, p1, v1}, '+P+'RebornConfig;->driverReady(Landroid/content/Context;Lcom/gtavsource/android/RuntimeConfig;Ljava/lang/String;)V\n\n    move-object p0, v1'))
before('GameDiagnostics','collectExitInfo(Landroid/content/Context;Ljava/io/File;)Ljava/lang/String;','    .locals 34','    # Reborn exit classification\n')
edit('GameDiagnostics','collectExitInfo(Landroid/content/Context;Ljava/io/File;)Ljava/lang/String;',lambda t:once(t,'    .locals 34','    .locals 34\n\n    invoke-static/range {p0 .. p0}, '+P+'RebornDiagnostics;->init(Landroid/content/Context;)V'))
edit('GameDiagnostics','collectExitInfo(Landroid/content/Context;Ljava/io/File;)Ljava/lang/String;',lambda t:once(t,'    invoke-static {v0, v1, v2, v6}, '+P+'CrashReportArchive;->isCrash(IILjava/lang/String;Ljava/lang/String;)Z','    invoke-static/range {v26 .. v26}, '+P+'RebornDiagnostics;->isFailure(Landroid/app/ApplicationExitInfo;)Z'))
edit('GameDiagnostics','reasonName(I)Ljava/lang/String;',lambda t:'.method private static reasonName(I)Ljava/lang/String;\n    .locals 1\n    invoke-static {p0}, '+P+'RebornDiagnostics;->reasonName(I)Ljava/lang/String;\n    move-result-object v0\n    return-object v0\n.end method')
edit('CrashReportArchive','isCrash(IILjava/lang/String;Ljava/lang/String;)Z',lambda t:'.method static isCrash(IILjava/lang/String;Ljava/lang/String;)Z\n    .locals 1\n    invoke-static {p0, p1, p2, p3}, '+P+'RebornDiagnostics;->unexpected(IILjava/lang/String;Ljava/lang/String;)Z\n    move-result v0\n    return v0\n.end method')
p=S/'GameTelemetry.smali';p.write_text(p.read_text()+'\n.method public static rebornFrameCount()J\n    .locals 2\n    invoke-static {}, '+P+'GameTelemetry;->nativeFrameCount()J\n    move-result-wide v0\n    return-wide v0\n.end method\n')
p=D/'smali/org/libsdl/app/SDLMain.smali';t=p.read_text();p.write_text(once(t,'    invoke-static {v0, v1, v2}, Lorg/libsdl/app/SDLActivity;->nativeRunMain(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;)I','    invoke-static {v0, v1, v2}, Lorg/libsdl/app/SDLActivity;->nativeRunMain(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;)I\n\n    move-result v4\n\n    invoke-static {v4}, '+P+'RebornSession;->mainResult(I)V'))
p=D/'smali/org/libsdl/app/SDLActivity.smali';t=p.read_text();p.write_text(once(t,'    invoke-virtual {v0}, Ljava/lang/Thread;->join()V','    invoke-static {p0, v0}, '+P+'RebornSession;->join(Landroid/app/Activity;Ljava/lang/Thread;)Z\n\n    move-result v2\n\n    if-nez v2, :reborn_sdl_joined\n\n    invoke-super {p0}, Landroid/app/Activity;->onDestroy()V\n\n    return-void\n\n    :reborn_sdl_joined'))

# Translate at display boundaries without modifying registers containing IDs,
# configuration values, trainer commands, or EditText input.
counts={}
for p in S.rglob('*.smali'):
    if p.name.startswith('Reborn'):continue
    t=p.read_text();old=t
    def replace(m):
        ins,args,owner,method,signature=m.groups();new=None
        if owner in ['Landroid/widget/'+x+';' for x in ['TextView','Button','CheckBox','RadioButton','Switch','ToggleButton','EditText']]:
            if method=='setText' and signature=='(Ljava/lang/CharSequence;)V':new=('text','(Landroid/widget/TextView;Ljava/lang/CharSequence;)V')
            if method=='setHint' and signature=='(Ljava/lang/CharSequence;)V':new=('hint','(Landroid/widget/TextView;Ljava/lang/CharSequence;)V')
        if method=='setContentDescription' and signature=='(Ljava/lang/CharSequence;)V':new=('description','(Landroid/view/View;Ljava/lang/CharSequence;)V')
        if owner=='Landroid/app/ProgressDialog;' and method=='setMessage' and signature=='(Ljava/lang/CharSequence;)V':new=('progress','(Landroid/app/ProgressDialog;Ljava/lang/CharSequence;)V')
        if owner in ['Landroid/app/AlertDialog$Builder;',P+'MenuDialogBuilder;']:
            names={'setTitle':'title','setMessage':'message','setPositiveButton':'positive','setNegativeButton':'negative','setNeutralButton':'neutral','setItems':'items','setSingleChoiceItems':'single','setMultiChoiceItems':'multi'}
            if method in names and signature.startswith(('(Ljava/lang/CharSequence;','([Ljava/lang/CharSequence;')):
                new=(names[method],'(Landroid/app/AlertDialog$Builder;'+signature[1:])
        if not new:return m[0]
        counts[new[0]]=counts.get(new[0],0)+1
        return 'invoke-static'+('/range' if '/range' in ins else '')+' '+args+', '+P+'RebornLocale;->'+new[0]+new[1]
    t=re.sub(r'(invoke-virtual(?:/range)?) (\{[^}]*\}), (L[^;]+;)->(\w+)(\([^\n]+)',replace,t)
    t=t.replace('Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;',P+'RebornLocale;->toast(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;')
    if t!=old:p.write_text(t)
(D/'reborn-hooks.json').write_text(json.dumps({'boundary_hooks':counts},indent=2)+'\n')
fingerprints={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((D/'lib/arm64-v8a').glob('*.so'))}
(D/'assets/reborn-binary-fingerprints.json').write_text(json.dumps(fingerprints,sort_keys=True,indent=2)+'\n')
print(json.dumps(counts,indent=2))
