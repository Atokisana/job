[app]
title = CENAD
package.name = cenad
package.domain = org.cenad
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,db,csv
version = 1.0.0

requirements = python3,kivy==2.3.0,pillow,sqlite3,android

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/assets/logo.png
presplash.filename = %(source.dir)s/assets/logo.png

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,CALL_PHONE,SEND_SMS
android.minapi = 21
android.api = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
