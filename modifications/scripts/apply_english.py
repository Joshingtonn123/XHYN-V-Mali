#!/usr/bin/env python3
"""Apply the English test patch to an untouched Apktool decode of the 845 base."""
from pathlib import Path
import collections
import json
import re
import shutil
import xml.etree.ElementTree as ET

R = Path(__file__).resolve().parents[1]
D = R / 'decoded'
S = D / 'smali/com/gtavsource/android'
OLD = R.parent / 'recovered/hotfix2/extracted/XHYN-V-r30-Hotfix2'
EARLIER = R.parent / 'recovered/vulkan-test3/extracted/test2/test1'
CJK = re.compile('[\u3400-\u9fff\uf900-\ufaff]')
STR = re.compile(r'^(\s*const-string(?:/jumbo)?\s+[vp]\d+,\s*)("(?:[^"\\]|\\.)*")(\s*)$', re.M)
METHOD = re.compile(r'^\.method .*?\n.*?^\.end method', re.M | re.S)

def unquote(value):
    return json.loads(value.replace("\\'", "'"))

def once(text, old, new):
    assert text.count(old) == 1, (old[:120], text.count(old))
    return text.replace(old, new, 1)

def edit_method(file, signature, transform):
    text = file.read_text()
    matches = [m for m in METHOD.finditer(text) if m.group().splitlines()[0].split()[-1] == signature]
    assert len(matches) == 1, (file, signature, len(matches))
    m = matches[0]
    text = text[:m.start()] + transform(m.group()) + text[m.end():]
    file.write_text(text)

assert not (D / 'english-test-patched.json').exists(), 'Decode the original APK again before reapplying'
mapping = json.loads((R / 'translation-complete.json').read_text())
mapping = {k: v.replace('Flashlight / special scope', 'Flashlight / scope').replace('Weapon names & selection hints', 'Weapon info & hints') for k, v in mapping.items()}
assert all(not CJK.search(v) for v in mapping.values())
counts = collections.Counter()

for p in (D / 'smali').rglob('*.smali'):
    text = p.read_text()
    def replace(m):
        value = unquote(m.group(2))
        if not CJK.search(value):
            return m.group()
        assert value in mapping, (p, value)
        counts['smali_strings'] += 1
        return m.group(1) + json.dumps(mapping[value], ensure_ascii=True) + m.group(3)
    new = STR.sub(replace, text)
    if new != text:
        p.write_text(new)
        counts['smali_files'] += 1

tokens = sorted(mapping, key=len, reverse=True)
def asset_text(value):
    if value in mapping:
        counts['asset_strings'] += 1
        return mapping[value]
    if CJK.search(value):
        original = value
        for key in tokens:
            if CJK.search(key):
                value = value.replace(key, mapping[key])
        value = value.translate(str.maketrans({'：': ': ', '；': '; ', '（': ' (', '）': ')', '，': ', ', '。': '.'}))
        assert not CJK.search(value), (original, value)
        counts['asset_strings'] += 1
    return value

def walk(value):
    if isinstance(value, dict):
        return {k: walk(v) for k, v in value.items()}
    if isinstance(value, list):
        return [walk(v) for v in value]
    if isinstance(value, str):
        return asset_text(value)
    return value

for p in (D / 'assets/touch-layouts').rglob('*.json'):
    obj = json.loads(p.read_text())
    result = walk(obj)
    if result != obj:
        p.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        counts['asset_files'] += 1

shutil.copyfile(EARLIER / 'default-android.ini', D / 'assets/default-android.ini')
shutil.copyfile(EARLIER / 'ffmpeg-build-notes.md', D / 'assets/licenses/ffmpeg-build-notes.md')

# Translate native trainer JSON at its display boundary, without changing IDs/commands.
dictionary = dict(mapping)
dictionary.update(json.loads((OLD / 'assets/xhyn-trainer-en.json').read_text()))
(D / 'assets/xhyn-trainer-en.json').write_text(json.dumps(dictionary, ensure_ascii=False, indent=2) + '\n')
helper = (OLD / 'baseline-smali/com/gtavsource/android/XhynTrainerText.smali').read_text()
def init_english(text):
    start = text.index('    invoke-static {p0}, Lcom/gtavsource/android/XhynConfig;->prefs')
    end = text.index('    .line 14', start)
    text = text[:start] + '    const/4 v1, 0x0\n\n    sput-boolean v1, Lcom/gtavsource/android/XhynTrainerText;->keepChinese:Z\n\n' + text[end:]
    return text.replace('Lcom/gtavsource/android/XhynConfig;->readText', 'Lcom/gtavsource/android/XhynTrainerText;->readText')
helper = METHOD.sub(lambda m: init_english(m.group()) if ' init(' in m.group().splitlines()[0] else m.group(), helper)
helper = once(helper, '    invoke-static {v0}, Lcom/gtavsource/android/XhynLocale;->t(Ljava/lang/String;)Ljava/lang/String;\n\n    move-result-object p0', '    move-object p0, v0')
helper += '\n' + (EARLIER / 'trainer-helper-methods.smali').read_text()
assert 'XhynConfig;' not in helper and 'XhynLocale;' not in helper
(S / 'XhynTrainerText.smali').write_text(helper)
shutil.copyfile(OLD / 'baseline-smali/com/gtavsource/android/XhynLabels.smali', S / 'XhynLabels.smali')
shutil.copyfile(EARLIER / 'XhynVulkanFiles.smali', S / 'XhynVulkanFiles.smali')

edit_method(S / 'GameMenuActivity.smali', 'onCreate(Landroid/os/Bundle;)V', lambda t: once(t,
    '    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V',
    '    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V\n\n    invoke-static {p0}, Lcom/gtavsource/android/XhynTrainerText;->prepare(Landroid/content/Context;)V'))
edit_method(S / 'ControlProfile.smali', 'checkedText(Ljava/lang/String;I)Ljava/lang/String;', lambda t: once(t,
    '    .line 384',
    '    invoke-static {p0, p1}, Lcom/gtavsource/android/XhynTrainerText;->label(Ljava/lang/String;I)Ljava/lang/String;\n\n    move-result-object p0\n\n    .line 384'))
edit_method(S / 'TrainerBridge$CatalogItem.smali', '<init>(Lorg/json/JSONObject;)V', lambda t: once(t,
    '    invoke-direct {p0}, Ljava/lang/Object;-><init>()V',
    '    invoke-direct {p0}, Ljava/lang/Object;-><init>()V\n\n    invoke-static {p1}, Lcom/gtavsource/android/XhynTrainerText;->item(Lorg/json/JSONObject;)V'))
edit_method(S / 'TrainerBridge$Snapshot.smali', '<init>(Ljava/lang/String;)V', lambda t: once(t,
    '    iput-object p1, p0, Lcom/gtavsource/android/TrainerBridge$Snapshot;->message:Ljava/lang/String;',
    '    invoke-static {p1}, Lcom/gtavsource/android/XhynTrainerText;->message(Ljava/lang/String;)Ljava/lang/String;\n\n    move-result-object p1\n\n    iput-object p1, p0, Lcom/gtavsource/android/TrainerBridge$Snapshot;->message:Ljava/lang/String;'))
edit_method(S / 'GameErrorDialog.smali', 'show(Ljava/lang/String;Z)Z', lambda t: once(t,
    '    .locals 7',
    '    .locals 7\n\n    invoke-static {p1}, Lcom/gtavsource/android/XhynTrainerText;->report(Ljava/lang/String;)Ljava/lang/String;\n\n    move-result-object p1'))

# Convert Java native linkage failures into the existing launcher error dialog.
edit_method(S / 'GameMenuActivity.smali', 'lambda$work$0$com-gtavsource-android-GameMenuActivity(Ljava/util/concurrent/Callable;Landroid/app/ProgressDialog;Ljava/util/function/Consumer;)V', lambda t: once(once(t,
    '    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0',
    '    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0\n    .catch Ljava/lang/LinkageError; {:try_start_0 .. :try_end_0} :catch_linkage'),
    '    :catch_0\n    move-exception p1',
    '    :catch_linkage\n    move-exception p1\n\n    new-instance v0, Ljava/io/IOException;\n\n    invoke-direct {v0, p1}, Ljava/io/IOException;-><init>(Ljava/lang/Throwable;)V\n\n    move-object p1, v0\n\n    goto :report_error\n\n    :catch_0\n    move-exception p1\n\n    :report_error'))

# Validate the extracted game root before rebuilding mods or entering native rendering.
edit_method(S / 'GameMenuActivity.smali', 'lambda$launch$1$com-gtavsource-android-GameMenuActivity()Ljava/lang/String;', lambda t: once(t,
    '    .line 1023',
    '    iget-object v0, p0, Lcom/gtavsource/android/GameMenuActivity;->config:Lcom/gtavsource/android/RuntimeConfig;\n\n    invoke-static {v0}, Lcom/gtavsource/android/XhynVulkanFiles;->check(Lcom/gtavsource/android/RuntimeConfig;)V\n\n    .line 1023'))

# SDL calls Activity.onCreate before loadLibraries. Prepare there so the existing
# LinkageError dialog handles failures without causing SuperNotCalledException.
edit_method(S / 'GTAVActivity.smali', 'onCreate(Landroid/os/Bundle;)V', lambda t: once(t,
    '    invoke-virtual {p0}, Lcom/gtavsource/android/GTAVActivity;->prepareLaunch()V',
    '    # Preparation is performed inside loadLibraries after Activity.onCreate.'))
edit_method(S / 'GTAVActivity.smali', 'loadLibraries()V', lambda t: once(once(t,
    '    :try_start_0',
    '    :try_start_0\n    invoke-static {p0}, Lcom/gtavsource/android/XhynTrainerText;->prepare(Landroid/content/Context;)V\n\n    invoke-virtual {p0}, Lcom/gtavsource/android/GTAVActivity;->prepareLaunch()V\n'),
    '    .catch Ljava/lang/UnsatisfiedLinkError;',
    '    .catch Ljava/lang/LinkageError;'))

android = '{http://schemas.android.com/apk/res/android}'
ET.register_namespace('android', android[1:-1])
manifest = ET.parse(D / 'AndroidManifest.xml')
manifest.getroot().set('package', 'com.xhynph.xhynv.reborn')
manifest.getroot().find('application').set(android + 'label', 'XHYN V')
manifest.write(D / 'AndroidManifest.xml', encoding='utf-8', xml_declaration=True)
yml = (D / 'apktool.yml').read_text()
yml = once(yml, 'versionCode: 25', 'versionCode: 1')
(D / 'apktool.yml').write_text(yml)

(R / 'translation-complete.json').write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + '\n')
(D / 'assets/XHYN-V-TEST-NOTICES.txt').write_text(
    'XHYN V 0.1 — DXVK base\n'
    'Based on the supplied DXVK launcher APK (upstream version 0.1 / 25).\n'
    'English launcher, layouts, trainer display translation and focused launcher error handling by XHYN_PH.\n'
    'Original game engine, native renderer and libraries remain the work of their respective developers.\n'
    'Native language selection changes are documented in the development checkpoint. No original engine source is included.\n'
    'This APK does not contain GTA V game data.\n'
    'This is a test build. Native rendering and device compatibility require gameplay testing.\n'
    'Existing third-party licenses and notices are retained.\n')
result = {'changes': dict(counts), 'dictionary_entries': len(dictionary), 'package': 'com.xhynph.xhynv.reborn', 'version': '0.1'}
(D / 'english-test-patched.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
