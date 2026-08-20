import os
import sys

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.metrics import dp

try:
    from theme.theme_manager import theme
except ImportError:
    class DummyTheme:
        BACKGROUND = (0.04, 0.07, 0.1, 1)
        PRIMARY = (0.3, 0.2, 0.8, 1)
        TEXT_PRIMARY = (1, 1, 1, 1)
        TEXT_SECONDARY = (0.7, 0.75, 0.8, 1)
    theme = DummyTheme()


class DeviceCard(Button):
    def __init__(self, name, distance, select_callback, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.size_hint_y = None
        self.height = dp(65)
        self.select_callback = select_callback

        box = BoxLayout(orientation='horizontal', padding=[dp(15), dp(10), dp(15), dp(10)], spacing=dp(15))

        with self.canvas.before:
            self.bg_color = Color(0.12, 0.12, 0.18, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(12)])
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Avatar Icon
        avatar_box = BoxLayout(size_hint=(None, None), size=(dp(45), dp(45)))
        with avatar_box.canvas.before:
            Color(0.2, 0.2, 0.28, 1)
            self.avatar_circle = Ellipse(size=avatar_box.size, pos=avatar_box.pos)
        avatar_box.bind(size=self._update_avatar_bg, pos=self._update_avatar_bg)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        user_icon_path = os.path.join(base_dir, 'assets', 'camera.icon.png')

        img_avatar = Image(
            source=user_icon_path if os.path.exists(user_icon_path) else '',
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            fit_mode="contain"
        )
        avatar_box.add_widget(img_avatar)

        # Device Info
        info_box = BoxLayout(orientation='vertical', spacing=dp(2))
        lbl_name = Label(
            text=f"[b]{name}[/b]",
            markup=True,
            font_size='15sp',
            color=theme.TEXT_PRIMARY,
            halign='left',
            valign='middle'
        )
        lbl_name.bind(size=lbl_name.setter('text_size'))

        lbl_dist = Label(
            text=f"{distance}",
            font_size='12sp',
            color=theme.TEXT_SECONDARY,
            halign='left',
            valign='middle'
        )
        lbl_dist.bind(size=lbl_dist.setter('text_size'))

        info_box.add_widget(lbl_name)
        info_box.add_widget(lbl_dist)

        # Signal Icon
        signal_box = Label(
            text="📶",
            font_size='16sp',
            size_hint_x=None,
            width=dp(30),
            halign='right',
            valign='middle'
        )

        box.add_widget(avatar_box)
        box.add_widget(info_box)
        box.add_widget(signal_box)

        self.add_widget(box)
        self.bind(on_release=lambda instance: self.select_callback(self))

    def set_selected(self, is_selected):
        if is_selected:
            self.bg_color.rgba = (0.3, 0.2, 0.5, 1)
        else:
            self.bg_color.rgba = (0.12, 0.12, 0.18, 1)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_avatar_bg(self, instance, value):
        self.avatar_circle.pos = instance.pos
        self.avatar_circle.size = instance.size


class OnboardingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_card = None

        self.layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(15), dp(20), dp(15)], spacing=dp(15))

        with self.layout.canvas.before:
            Color(*theme.BACKGROUND)
            self.rect = RoundedRectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        # Header Title
        lbl_top = Label(
            text="[b]Nearby Devices[/b]",
            markup=True,
            font_size='20sp',
            color=theme.TEXT_PRIMARY,
            size_hint_y=None,
            height=dp(35),
            halign='center',
            valign='middle'
        )
        lbl_top.bind(size=lbl_top.setter('text_size'))

        # Device List Scroll
        scroll = ScrollView(size_hint=(1, 1))
        self.device_list = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.device_list.bind(minimum_height=self.device_list.setter('height'))

        devices_data = [
            ("Rifat", "32 m"),
            ("Sakib", "68 m"),
            ("Mehedi", "120 m"),
            ("Tomal", "245 m"),
            ("Asif", "320 m"),
            ("Bappy", "450 m")
        ]

        self.cards = []
        for name, dist in devices_data:
            card = DeviceCard(name=name, distance=dist, select_callback=self.select_device)
            self.cards.append(card)
            self.device_list.add_widget(card)

        scroll.add_widget(self.device_list)

        # Bottom Button
        self.btn_start_chat = Button(
            text="Select Device & Connect",
            size_hint=(1, None),
            height=dp(50),
            bold=True,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        with self.btn_start_chat.canvas.before:
            Color(*theme.PRIMARY)
            self.btn_start_chat.bg_rect = RoundedRectangle(size=self.btn_start_chat.size, pos=self.btn_start_chat.pos, radius=[dp(14)])
        self.btn_start_chat.bind(size=self._update_btn_bg, pos=self._update_btn_bg)
        
        self.btn_start_chat.bind(on_release=self.go_to_discovering)

        self.layout.add_widget(lbl_top)
        self.layout.add_widget(scroll)
        self.layout.add_widget(self.btn_start_chat)

        self.add_widget(self.layout)

    def select_device(self, card_instance):
        for card in self.cards:
            card.set_selected(False)
        card_instance.set_selected(True)
        self.selected_card = card_instance

    def go_to_discovering(self, *args):
        if self.manager:
            self.manager.current = 'discovering'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_btn_bg(self, instance, value):
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size