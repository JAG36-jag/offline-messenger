import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.metrics import dp
from kivy.utils import platform

IS_ANDROID = (platform == 'android')

if IS_ANDROID:
    try:
        from android.permissions import request_permissions, Permission  # type: ignore
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    except ImportError:
        pass

# থিম সাপোর্ট
try:
    from theme.theme_manager import theme
    BACKGROUND_COLOR = theme.BACKGROUND
    PRIMARY_COLOR = theme.PRIMARY
    TEXT_PRIMARY_COLOR = theme.TEXT_PRIMARY
    TEXT_SECONDARY_COLOR = theme.TEXT_SECONDARY
except ModuleNotFoundError:
    BACKGROUND_COLOR = (0.08, 0.08, 0.12, 1)
    PRIMARY_COLOR = (0.4, 0.3, 0.9, 1)
    TEXT_PRIMARY_COLOR = (1, 1, 1, 1)
    TEXT_SECONDARY_COLOR = (0.7, 0.7, 0.8, 1)


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'register'
        self.selected_image_path = None
        self.option_popup = None
        self.gallery_popup = None

        layout = BoxLayout(orientation='vertical', padding=[dp(25), dp(30)], spacing=dp(20))

        with layout.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_rect, pos=self._update_rect)

        lbl_title = Label(
            text="[b]Register[/b]",
            markup=True,
            font_size='26sp',
            color=TEXT_PRIMARY_COLOR,
            size_hint_y=None,
            height=dp(40)
        )

        self.avatar_box = BoxLayout(
            size_hint=(None, None),
            size=(dp(100), dp(100)),
            pos_hint={'center_x': 0.5}
        )

        with self.avatar_box.canvas.before:
            Color(0.2, 0.2, 0.28, 1)
            self.avatar_circle = Ellipse(size=self.avatar_box.size, pos=self.avatar_box.pos)
        self.avatar_box.bind(size=self._update_avatar_circle, pos=self._update_avatar_circle)

        self.img_avatar = Image(
            source='',
            fit_mode="fill"
        )

        self.btn_add_photo = Button(
            text="+",
            font_size='36sp',
            bold=True,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=PRIMARY_COLOR
        )
        self.btn_add_photo.bind(on_release=self.show_photo_options)

        self.avatar_box.add_widget(self.btn_add_photo)

        lbl_name = Label(
            text="Your Name",
            font_size='13sp',
            color=TEXT_SECONDARY_COLOR,
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        lbl_name.bind(size=lbl_name.setter('text_size'))

        self.txt_name = TextInput(
            hint_text="Enter your name",
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            background_normal='',
            background_color=(0.14, 0.14, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[dp(12), dp(12)]
        )

        btn_continue = Button(
            text="Continue",
            size_hint=(1, None),
            height=dp(50),
            bold=True,
            font_size='16sp',
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        with btn_continue.canvas.before:
            Color(*PRIMARY_COLOR)
            btn_continue.bg_rect = RoundedRectangle(size=btn_continue.size, pos=btn_continue.pos, radius=[dp(12)])
        btn_continue.bind(size=self._update_btn_rect, pos=self._update_btn_rect)
        btn_continue.bind(on_release=self.on_register)

        layout.add_widget(lbl_title)
        layout.add_widget(self.avatar_box)
        layout.add_widget(lbl_name)
        layout.add_widget(self.txt_name)
        layout.add_widget(BoxLayout())
        layout.add_widget(btn_continue)

        self.add_widget(layout)

    def show_photo_options(self, *args):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(10), dp(10)])

        btn_default = Button(text="Default Avatar", size_hint_y=None, height=dp(45))
        btn_gallery = Button(text="Choose from Gallery", size_hint_y=None, height=dp(45))
        btn_cancel = Button(text="Cancel", size_hint_y=None, height=dp(45), background_color=(0.5, 0.1, 0.1, 1))

        content.add_widget(btn_default)
        content.add_widget(btn_gallery)
        content.add_widget(btn_cancel)

        self.option_popup = Popup(
            title="Profile Photo Options",
            content=content,
            size_hint=(0.85, 0.4)
        )

        btn_default.bind(on_release=self.set_default_avatar)
        btn_gallery.bind(on_release=self.open_gallery_picker)
        btn_cancel.bind(on_release=self.option_popup.dismiss)

        self.option_popup.open()

    def open_gallery_picker(self, *args):
        if self.option_popup:
            self.option_popup.dismiss()

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(10), dp(10)])

        initial_path = os.path.expanduser('~')
        if IS_ANDROID:
            try:
                from android.storage import primary_external_storage_path  # type: ignore
                initial_path = primary_external_storage_path()
            except ImportError:
                pass

        file_chooser = FileChooserIconView(
            path=initial_path,
            filters=['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG'],
            size_hint=(1, 1)
        )

        btn_layout = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        btn_cancel = Button(text="Cancel", bold=True, background_color=(0.3, 0.3, 0.3, 1))
        btn_select = Button(text="Select Photo", bold=True, background_color=PRIMARY_COLOR)

        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_select)

        content.add_widget(file_chooser)
        content.add_widget(btn_layout)

        self.gallery_popup = Popup(
            title="Select Profile Image",
            content=content,
            size_hint=(0.95, 0.9)
        )

        btn_cancel.bind(on_release=self.gallery_popup.dismiss)
        btn_select.bind(on_release=lambda x: self._on_image_selected(file_chooser.selection))

        self.gallery_popup.open()

    def _on_image_selected(self, selection):
        if not selection:
            return

        image_path = selection[0]
        if os.path.isfile(image_path):
            self.selected_image_path = image_path
            self.img_avatar.source = image_path
            self.avatar_box.clear_widgets()
            self.avatar_box.add_widget(self.img_avatar)

        if self.gallery_popup:
            self.gallery_popup.dismiss()

    def set_default_avatar(self, *args):
        if self.option_popup:
            self.option_popup.dismiss()
        self.selected_image_path = None
        self.avatar_box.clear_widgets()
        self.avatar_box.add_widget(self.btn_add_photo)

    def on_register(self, *args):
        username = self.txt_name.text.strip()
        if username and self.manager:
            if self.manager.has_screen('chat'):
                chat_screen = self.manager.get_screen('chat')
                if hasattr(chat_screen, 'set_my_profile'):
                    chat_screen.set_my_profile(
                        my_name=username,
                        image_path=self.selected_image_path
                    )
                elif hasattr(chat_screen, 'set_profile'):
                    chat_screen.set_profile(
                        name=username,
                        avatar_path=self.selected_image_path
                    )

            if self.manager.has_screen('connection_select'):
                self.manager.current = 'connection_select'
            elif self.manager.has_screen('chat'):
                self.manager.current = 'chat'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_avatar_circle(self, instance, value):
        self.avatar_circle.pos = instance.pos
        self.avatar_circle.size = instance.size

    def _update_btn_rect(self, instance, value):
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size