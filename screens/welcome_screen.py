import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'welcome'

        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))

        with layout.canvas.before:
            Color(0.08, 0.08, 0.12, 1)  # Dark Background
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_rect, pos=self._update_rect)

        # লোগো/টাইটেল সেকশন
        lbl_title = Label(
            text="[b]Welcome to\nOffline P2P Messenger[/b]",
            markup=True,
            font_size='26sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))

        lbl_subtitle = Label(
            text="Connect and chat with nearby devices without internet connection.",
            font_size='14sp',
            color=(0.7, 0.7, 0.8, 1),
            halign='center',
            valign='middle'
        )
        lbl_subtitle.bind(size=lbl_subtitle.setter('text_size'))

        # গেট স্টার্টেড বাটন
        btn_start = Button(
            text="Get Started",
            size_hint=(1, None),
            height=dp(50),
            bold=True,
            font_size='16sp',
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        with btn_start.canvas.before:
            Color(0.4, 0.3, 0.9, 1)  # Primary Color
            btn_start.bg_rect = RoundedRectangle(size=btn_start.size, pos=btn_start.pos, radius=[dp(12)])
        btn_start.bind(size=self._update_btn_bg, pos=self._update_btn_bg)
        btn_start.bind(on_release=self.go_next)

        layout.add_widget(BoxLayout(size_hint_y=0.2))  # Top Spacer
        layout.add_widget(lbl_title)
        layout.add_widget(lbl_subtitle)
        layout.add_widget(BoxLayout(size_hint_y=0.3))  # Middle Spacer
        layout.add_widget(btn_start)

        self.add_widget(layout)

    def go_next(self, *args):
        if self.manager:
            app = self.manager.get_screen('welcome').app if hasattr(self.manager.get_screen('welcome'), 'app') else None
            # ইউজার রেজিস্টার্ড থাকলে সরাসরি ডিসকভারিং (স্ক্যানিং)-এ যাবে, না থাকলে রেজিস্টার স্ক্রিনে
            self.manager.current = 'register'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_btn_bg(self, instance, value):
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size