[app]
title = Offline Messenger
package.name = offlinemessenger
package.domain = org.offlinemessenger
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,wav,mp3,db
version = 0.1

# hostpython3 সরিয়ে দেওয়া হয়েছে যাতে বিল্ড হালকা হয়
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,android,pyjnius

orientation = portrait
fullscreen = 0

# অ্যান্ড্রয়েড সেটিংস (API 31 এবং NDK 25b বর্তমানে সবচেয়ে কম মেমোরি নেয়)
android.api = 31
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.enable_androidx = True

icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/splash.png

android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
