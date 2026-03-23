[app]
title = CENAD
package.name = cenad
package.domain = org.cenad
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,db,csv
version = 1.0.0

# Sans pandas/numpy/matplotlib/scipy
requirements = python3,kivy==2.3.0,sqlite3,pillow,android

orientation = portrait

# ICONE APK - placez logo.png 512x512px dans assets/
# icon.filename = %(source.dir)s/assets/logo.png

# SPLASH - decommenter si voulu
# presplash.filename = %(source.dir)s/assets/logo.png

# PERMISSIONS ANDROID
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,CALL_PHONE,SEND_SMS,INTERNET

# SDK
android.minapi = 21
android.api = 33
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
