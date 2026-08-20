[app]
title = Offline Messenger
package.name = offlinemessenger
package.domain = org.offlinemessenger
source.dir = .
# সব ধরনের ফাইল ইনক্লুড করা হয়েছে
source.include_exts = py,png,jpg,kv,atlas,ttf,wav,mp3,db

version = 0.1

# রিকোয়ারমেন্টস গুলো একদম নিখুঁত রাখা হয়েছে
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,android,sqlite3,setuptools

orientation = portrait
fullscreen = 0

# মেসেঞ্জারের জন্য প্রয়োজনীয় সব পারমিশন
android.permissions = INTERNET, BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, CHANGE_WIFI_STATE, ACCESS_WIFI_STATE, NEARBY_WIFI_DEVICES, BLUETOOTH_SCAN, BLUETOOTH_CONNECT, BLUETOOTH_ADVERTISE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True

# আপনার স্ক্রিনশট অনুযায়ী ইমেজের নাম
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/splash.png

# শুধু একটি আর্কিটেকচার দিলে বিল্ড দ্রুত হয়
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
