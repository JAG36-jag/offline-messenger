import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle
from theme.theme_manager import theme

class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical', padding=[24, 20, 24, 20], spacing=20)

        with self.layout.canvas.before:
            Color(*theme.BACKGROUND)
            self.rect = RoundedRectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        # Header Title
        lbl_top = Label(
            text="[b]Welcome[/b]",
            markup=True,
            font_size='22sp',
            color=theme.TEXT_PRIMARY,
            size_hint_y=None,
            height='30dp'
        )

        # Assets Path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        welcome_img_path = os.path.join(base_dir, 'assets', 'welcome_illustration.png')

        welcome_img = Image(
            source=welcome_img_path if os.path.exists(welcome_img_path) else '',
            size_hint=(1, 0.48),
            fit_mode="contain"
        )

        # Text Content
        content_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.25)
        
        lbl_title = Label(
            text="[b]Stay Connected\nOffline[/b]",
            markup=True,
            font_size='24sp',
            color=theme.TEXT_PRIMARY,
            halign='center',
            valign='middle'
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))
        
        lbl_sub = Label(
            text="Chat with people nearby using\nBluetooth or Hotspot.",
            font_size='14sp',
            color=theme.TEXT_SECONDARY,
            halign='center',
            valign='top'
        )
        lbl_sub.bind(size=lbl_sub.setter('text_size'))

        content_box.add_widget(lbl_title)
        content_box.add_widget(lbl_sub)

        # Bottom Action Layout (Only Get Started Button)
        action_box = BoxLayout(orientation='vertical', size_hint_y=None, height='50dp')

        self.btn_start = Button(
            text="Get Started",
            size_hint=(1, None),
            height='50dp',
            bold=True,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        with self.btn_start.canvas.before:
            Color(*theme.PRIMARY)
            self.btn_start.bg_rect = RoundedRectangle(size=self.btn_start.size, pos=self.btn_start.pos, radius=[14])
        self.btn_start.bind(size=self._update_btn_bg, pos=self._update_btn_bg)
        
        # Click action -> Register Screen
        self.btn_start.bind(on_release=self.open_register_screen)

        action_box.add_widget(self.btn_start)

        # Adding widgets to main layout
        self.layout.add_widget(lbl_top)
        self.layout.add_widget(welcome_img)
        self.layout.add_widget(content_box)
        self.layout.add_widget(action_box)

        self.add_widget(self.layout)

    def open_register_screen(self, *args):
        if self.manager:
            self.manager.current = 'register'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_btn_bg(self, instance, value):
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size