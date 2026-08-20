[app]
title = Offline Messenger
package.name = offlinemessenger
package.domain = org.offlinemessenger
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,wav,mp3,db
version = 0.1

# রিকোয়ারমেন্টস একদম স্টেবল রাখা হয়েছে
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,android,pyjnius,setuptools

orientation = portrait
fullscreen = 0

# অ্যান্ড্রয়েড কনফিগারেশন (বুক ফুলিয়ে এগুলো দিন, এরর হবে না)
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
