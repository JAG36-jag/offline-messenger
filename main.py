import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window

# All Screen Imports
from screens.splash_screen import SplashScreen
from screens.welcome_screen import WelcomeScreen
from screens.register_screen import RegisterScreen
from screens.connection_select_screen import ConnectionSelectScreen
from screens.discovering_screen import DiscoveringScreen
from screens.onboarding_screen import OnboardingScreen
from screens.chat_screen import ChatScreen
from screens.chats_screen import ChatsScreen
from screens.file_transfer_screen import FileTransferScreen

# Network Service Import
try:
    from network.network_manager import NetworkManager as NetworkService
except ImportError:
    try:
        from network.socket_service import NetworkService
    except ImportError:
        NetworkService = None

# Desktop Testing Window Size
Window.size = (400, 680)


class OfflineMessengerApp(App):
    user_name = "User"  # গ্লোবাল ইউজার নেম ভ্যারিয়েবল
    config_data = {}
    net_service = None

    def build(self):
        self.title = "Offline Messenger"
        self.current_peer_ip = "127.0.0.1"

        # ১. সেভ করা প্রোফাইল নেম লোড করা
        self.load_user_profile()

        # ২. নেটওয়ার্ক ব্যাকএন্ড সার্ভিস ইনিশিয়ালাইজ
        self.net_service = None
        if NetworkService:
            try:
                self.net_service = NetworkService()
                if hasattr(self.net_service, 'start_server'):
                    self.net_service.start_server(on_message_callback=self.on_global_message)
                elif hasattr(self.net_service, 'broadcast_presence'):
                    self.net_service.broadcast_presence()
            except Exception as e:
                print(f"[Network Service Warning]: {e}")

        # ৩. স্ক্রিন ম্যানেজার তৈরি (NoTransition সহ)
        sm = ScreenManager(transition=NoTransition())

        # স্ক্রিন ইনস্ট্যান্স তৈরি ও যোগ করা
        self.splash_screen = SplashScreen(name='splash')
        self.welcome_screen = WelcomeScreen(name='welcome')
        self.register_screen = RegisterScreen(name='register')
        self.select_connection_screen = ConnectionSelectScreen(name='connection_select')
        self.onboarding_screen = OnboardingScreen(name='onboarding')
        self.discovering_screen = DiscoveringScreen(name='discovering')
        self.chat_screen = ChatScreen(name='chat')
        self.chats_screen = ChatsScreen(name='chats')
        
        try:
            self.file_transfer_screen = FileTransferScreen(name='file_transfer')
        except Exception:
            self.file_transfer_screen = None

        # চ্যাট স্ক্রিনগুলোতে ব্যাকএন্ড সার্ভিস এবং ইউজার নেম পাস করা
        if self.net_service:
            if hasattr(self.chats_screen, 'set_network_service'):
                self.chats_screen.set_network_service(self.net_service, user_name=self.user_name)
            if hasattr(self.chat_screen, 'set_network_service'):
                self.chat_screen.set_network_service(self.net_service, user_name=self.user_name)

        # স্ক্রিন ম্যানেজারে সব স্ক্রিন যোগ করা
        sm.add_widget(self.splash_screen)
        sm.add_widget(self.welcome_screen)
        sm.add_widget(self.register_screen)
        sm.add_widget(self.select_connection_screen)
        sm.add_widget(self.onboarding_screen)
        sm.add_widget(self.discovering_screen)
        sm.add_widget(self.chat_screen)
        sm.add_widget(self.chats_screen)
        if self.file_transfer_screen:
            sm.add_widget(self.file_transfer_screen)

        sm.current = 'splash'
        return sm

    def load_user_profile(self):
        try:
            if hasattr(self, 'net_service') and hasattr(self.net_service, 'db') and self.net_service.db:
                saved_name = self.net_service.db.get_user_name()
                if saved_name:
                    self.user_name = saved_name
        except Exception:
            pass

    def on_global_message(self, data):
        """ইনকামিং মেসেজ বা ফাইল নোটিফিকেশন হ্যান্ডেল করার জন্য"""
        if hasattr(self, 'chats_screen') and self.chats_screen:
            if hasattr(self.chats_screen, 'on_message_received'):
                self.chats_screen.on_message_received(data)
        if hasattr(self, 'chat_screen') and self.chat_screen:
            if hasattr(self.chat_screen, 'on_message_received'):
                self.chat_screen.on_message_received(data)

    def on_stop(self):
        """অ্যাপ বন্ধ করলে সকেট ক্লোজ করা"""
        if hasattr(self, 'net_service') and self.net_service:
            if hasattr(self.net_service, 'stop'):
                self.net_service.stop()


if __name__ == '__main__':
    OfflineMessengerApp().run()