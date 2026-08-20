[app]
title = Offline Messenger
package.name = offlinemessenger
package.domain = org.offlinemessenger
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,wav,mp3,db
version = 0.1

# রিকোয়ারমেন্টস একদম সিম্পল রাখা হয়েছে
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,android,pyjnius

orientation = portrait
fullscreen = 0

# পারমিশন
android.permissions = INTERNET, BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, CHANGE_WIFI_STATE, ACCESS_WIFI_STATE

android.api = 33
android.minapi = 21
# NDK ভার্সন পরিবর্তন করে ২৩বি করা হয়েছে যা সবচেয়ে স্টেবল
android.ndk = 23b
android.ndk_api = 21
android.accept_sdk_license = True

icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/splash.png

# শুধু একটি আর্কিটেকচার (বিল্ড দ্রুত হবে)
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
