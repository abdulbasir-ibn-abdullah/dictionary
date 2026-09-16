[app]

# (str) Title of your application
title = Smart Lug'at

# (str) Package name
package.name = smartlugat

# (str) Package domain (needed for android/ios packaging)
package.domain = org.dasturchi

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf

# (str) Application versioning
version = 1.0

# (list) Application requirements
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pyjnius

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (str) Presplash of the application
presplash.filename = %(source.dir)s/splash.png

# (str) Supported orientation (landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
# App-specific external storage (getExternalFilesDir) uchun maxsus ruxsat kerak emas.
android.permissions =

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 25b

# (str) python-for-android branch/tag to use.
# "master" hozir standart sifatida Python 3.14'ni maqsad qiladi, u esa
# Kivy 2.3.0 bilan mos emas (compile xatolari beradi). Shu sababli
# Python 3.11'ni standart qilib ishlatgan eski, barqaror relizga pin qilamiz.
p4a.branch = 2024.01.21

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) enables Android auto backup feature
android.allow_backup = True

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

# (int) Log level for buildozer (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1


[buildozer]

# (int) Log level for buildozer (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
