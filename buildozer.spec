[app]
title = CENAD
package.name = cenad
package.domain = org.cenad
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,csv
version = 1.0.0

# IMPORTANT : plus de pandas, numpy, matplotlib, scipy
requirements = python3,kivy==2.3.0,sqlite3,pillow,android

# Orientation portrait uniquement
orientation = portrait

# Permissions Android
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,CALL_PHONE,SEND_SMS,INTERNET

# SDK Android
android.minapi = 21
android.api = 33
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a, armeabi-v7a

# Icone et splash (placer vos fichiers dans assets/)
# icon.filename = %(source.dir)s/assets/logo.png
# presplash.filename = %(source.dir)s/assets/logo.png

android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
