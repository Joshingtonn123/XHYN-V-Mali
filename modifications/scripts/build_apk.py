#!/usr/bin/env python3
"""Build and sign XHYN-R from a decoded, user-supplied Android APK workspace."""
from pathlib import Path
import subprocess
import json
import hashlib
import struct
import zipfile
import secrets
import os

R = Path(__file__).resolve().parents[1]
D = R / "decoded"
OUT = R / "dist"
REPORTS = R / "reports"
SDK = R.parent / "recovered/hotfix2/extracted/XHYN-V-r30-Hotfix2/toolchain/android-ui"
APKTOOL = R.parent / "tools/apktool.jar"

OUT.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

if not (D / "AndroidManifest.xml").is_file():
    raise SystemExit(
        "Missing modifications/decoded/AndroidManifest.xml. "
        "Add your lawful base APK under original-apk/*.apk so Method 2 can decode it, "
        "or commit a complete decoded workspace."
    )

native_dir = D / "lib/arm64-v8a"
if not native_dir.is_dir():
    raise SystemExit("Missing modifications/decoded/lib/arm64-v8a native libraries.")
native_files = sorted(native_dir.glob("*.so"))
if not native_files:
    raise SystemExit("No ARM64 .so libraries found under modifications/decoded/lib/arm64-v8a.")
if not APKTOOL.is_file():
    raise SystemExit("Missing tools/apktool.jar. Method 2 downloads Apktool for the fallback build.")
if not (SDK / "apksigner.jar").is_file():
    raise SystemExit("Missing Android apksigner.jar. Run the Android SDK setup/fallback method.")

# A decoded APK may not contain an assets directory; create it before writing metadata.
(D / "assets").mkdir(parents=True, exist_ok=True)

sign = R / "signing"
sign.mkdir(parents=True, exist_ok=True)
os.chmod(sign, 0o700)
key = sign / "xhyn-v-reborn.p12"
password = sign / "password.txt"
if not key.exists():
    password.write_text(secrets.token_urlsafe(40) + "\n")
    os.chmod(password, 0o600)
    subprocess.run([
        "java", "sun.security.tools.keytool.Main", "-genkeypair",
        "-keystore", str(key), "-storetype", "PKCS12",
        "-storepass:file", str(password), "-keypass:file", str(password),
        "-alias", "xhyn-v-reborn", "-keyalg", "RSA", "-keysize", "3072",
        "-validity", "10000", "-dname", "CN=XHYN R, O=XHYN, C=IQ",
    ], check=True)
    os.chmod(key, 0o600)

fingerprints = {
    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
    for p in native_files
}
(D / "assets/reborn-binary-fingerprints.json").write_text(
    json.dumps(fingerprints, sort_keys=True, indent=2) + "\n"
)

unsigned = OUT / "XHYN-R-unsigned.apk"
final = OUT / "XHYN-R.apk"
subprocess.run([
    "java", "-jar", str(APKTOOL), "b", str(D), "-o", str(unsigned)
], check=True)

# Let apksigner write alignment metadata before calculating the APK signature.
subprocess.run([
    "java", "-jar", str(SDK / "apksigner.jar"), "sign",
    "--ks", str(key), "--ks-key-alias", "xhyn-v-reborn",
    "--ks-pass", "file:" + str(password),
    "--v4-signing-enabled", "false",
    "--alignment-preserved", "false",
    "--lib-page-alignment", "16384",
    "--out", str(final), str(unsigned),
], check=True)

verified = subprocess.run([
    "java", "-jar", str(SDK / "apksigner.jar"), "verify",
    "--verbose", "--print-certs", str(final),
], check=True, text=True, capture_output=True)
(REPORTS / "signature-verification.txt").write_text(verified.stdout + verified.stderr)
print(verified.stdout)

with zipfile.ZipFile(final) as z, final.open("rb") as stream:
    assert z.testzip() is None, "APK ZIP verification failed"
    for entry in z.infolist():
        if entry.compress_type != zipfile.ZIP_STORED:
            continue
        stream.seek(entry.header_offset)
        header = stream.read(30)
        name_len, extra_len = struct.unpack_from("<HH", header, 26)
        data_offset = entry.header_offset + 30 + name_len + extra_len
        alignment = 16384 if entry.filename.startswith("lib/") and entry.filename.endswith(".so") else 4
        assert data_offset % alignment == 0, (entry.filename, data_offset)
    assert z.read("classes.dex").startswith(b"dex\n"), "APK classes.dex is invalid"
    for name, digest in fingerprints.items():
        assert hashlib.sha256(z.read("lib/arm64-v8a/" + name)).hexdigest() == digest
    names = z.namelist()
    assert "lib/arm64-v8a/libc.so" not in names
    assert "lib/arm64-v8a/libdl.so" not in names

result = {
    "file": final.name,
    "bytes": final.stat().st_size,
    "sha256": hashlib.sha256(final.read_bytes()).hexdigest(),
    "signature_verified": True,
    "stored_native_libraries_aligned_to": 16384,
    "native_fingerprints": fingerprints,
    "device_gameplay_tested": False,
}
(REPORTS / "apk-verification.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "native_fingerprints"}, indent=2))
