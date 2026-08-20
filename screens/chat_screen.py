import os
from datetime import datetime
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.app import App
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.clock import Clock

KV_CHAT = '''
<ChatScreen>:
    name: 'chat'
    canvas.before:
        Color:
            rgba: 0.04, 0.07, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'

        # --- Top Header Bar ---
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            padding: [10, 8, 10, 8]
            spacing: 12
            canvas.before:
                Color:
                    rgba: 0.12, 0.17, 0.2, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                text: '<'
                font_size: '22sp'
                size_hint_x: None
                width: '35dp'
                background_normal: ''
                background_color: 0, 0, 0, 0
                color: 0.0, 0.75, 0.65, 1
                bold: True
                on_release: root.manager.current = 'chats'

            BoxLayout:
                id: header_profile_box
                spacing: 10

        # --- Scrollable Messages ---
        ScrollView:
            id: scroll_view
            do_scroll_x: False
            BoxLayout:
                id: chat_logs
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 12
                padding: [12, 15, 12, 15]

        # --- Bottom Input Bar ---
        BoxLayout:
            size_hint_y: None
            height: '62dp'
            padding: [10, 8, 10, 8]
            spacing: 8
            canvas.before:
                Color:
                    rgba: 0.12, 0.17, 0.2, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                text: '+'
                font_size: '22sp'
                size_hint_x: None
                width: '42dp'
                background_normal: ''
                background_color: 0.18, 0.24, 0.28, 1
                color: 0.0, 0.75, 0.65, 1
                bold: True
                on_release: root.manager.current = 'file_transfer'

            TextInput:
                id: txt_input
                hint_text: 'Type a message...'
                hint_text_color: 0.5, 0.6, 0.65, 1
                multiline: False
                foreground_color: 1, 1, 1, 1
                background_normal: ''
                background_color: 0.18, 0.24, 0.28, 1
                padding: [14, 12, 14, 12]
                cursor_color: 0.0, 0.75, 0.65, 1
                on_text_validate: root.send_text()

            Button:
                text: 'Send'
                size_hint_x: None
                width: '70dp'
                background_normal: ''
                background_color: 0.0, 0.6, 0.5, 1
                color: 1, 1, 1, 1
                bold: True
                on_release: root.send_text()
'''

Builder.load_string(KV_CHAT)


class CircleAvatar(AnchorLayout):
    def __init__(self, text="U", bg_color=(0.0, 0.6, 0.5, 1), size_dp=38, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (size_dp, size_dp)
        self.anchor_x = 'center'
        self.anchor_y = 'center'

        with self.canvas.before:
            Color(rgba=bg_color)
            self.circle = Ellipse(pos=self.pos, size=self.size)

        self.bind(pos=self._update, size=self._update)

        lbl = Label(
            text=text[0].upper() if text else "U",
            font_size=f'{int(size_dp * 0.45)}sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        self.add_widget(lbl)

    def _update(self, *args):
        self.circle.pos = self.pos
        self.circle.size = self.size


class ChatScreen(Screen):
    peer_name = "User"
    peer_ip = "127.0.0.1"
    net_service = None

    def set_network_service(self, net_service, user_name=None):
        self.net_service = net_service

    def get_my_name(self):
        app = App.get_running_app()
        if hasattr(app, 'user_name') and app.user_name:
            return app.user_name
        return "Me"

    def set_active_peer(self, name, ip):
        self.peer_name = str(name)
        self.peer_ip = str(ip)

        header_box = self.ids.header_profile_box
        header_box.clear_widgets()

        avatar = CircleAvatar(text=self.peer_name, bg_color=(0.2, 0.5, 0.8, 1), size_dp=40)

        info_box = BoxLayout(orientation='vertical', spacing=2)
        lbl_name = Label(
            text=self.peer_name,
            font_size='16sp',
            bold=True,
            color=(0.95, 0.95, 0.95, 1),
            halign='left',
            valign='middle'
        )
        lbl_name.bind(size=lbl_name.setter('text_size'))

        lbl_status = Label(
            text="Online",
            font_size='11sp',
            color=(0.0, 0.75, 0.65, 1),
            halign='left',
            valign='middle'
        )
        lbl_status.bind(size=lbl_status.setter('text_size'))

        info_box.add_widget(lbl_name)
        info_box.add_widget(lbl_status)

        header_box.add_widget(avatar)
        header_box.add_widget(info_box)

        app = App.get_running_app()
        if hasattr(app, 'net_service') and hasattr(app.net_service, 'db'):
            try:
                app.net_service.db.mark_messages_as_seen(self.peer_name)
            except Exception:
                pass

        self.load_history()

    def load_history(self):
        self.ids.chat_logs.clear_widgets()
        app = App.get_running_app()
        my_name = self.get_my_name()

        if hasattr(app, 'net_service') and hasattr(app.net_service, 'db'):
            try:
                messages = app.net_service.db.get_messages_for_peer(self.peer_name)
                for sender, content, msg_type, status, time_str in messages:
                    is_me = (sender == "Me" or sender == my_name)
                    self.add_message_bubble(content, is_me=is_me, sender_name=sender, time_str=time_str, status=status)
            except Exception:
                pass
        self.scroll_to_bottom()

    def add_message_bubble(self, message, is_me=False, sender_name="", time_str="", status="sent"):
        if not time_str:
            time_str = datetime.now().strftime("%I:%M %p")

        status_suffix = " • Seen" if status == "seen" else ""
        meta_text = f"{time_str}{status_suffix if is_me else ''}"

        row_wrapper = BoxLayout(
            size_hint_y=None,
            height='45dp',
            spacing=8
        )

        content_box = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            padding=[12, 8, 12, 6],
            spacing=3
        )

        lbl_msg = Label(
            text=str(message),
            font_size='14sp',
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            halign='left',
            valign='top'
        )

        lbl_meta = Label(
            text=meta_text,
            font_size='10sp',
            color=(0.75, 0.9, 0.85, 1) if is_me else (0.55, 0.65, 0.7, 1),
            size_hint=(None, None),
            halign='right'
        )

        content_box.add_widget(lbl_msg)
        content_box.add_widget(lbl_meta)

        bg_rgba = (0.0, 0.36, 0.29, 1) if is_me else (0.12, 0.17, 0.2, 1)

        def update_rect(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(rgba=bg_rgba)
                RoundedRectangle(
                    pos=instance.pos,
                    size=instance.size,
                    radius=[14, 14, 2 if is_me else 14, 14 if is_me else 2]
                )

        content_box.bind(pos=update_rect, size=update_rect)

        def recalculate_bubble_size(*args):
            screen_w = self.width if self.width > 0 else 360
            max_w = screen_w * 0.70

            lbl_msg.text_size = (None, None)
            lbl_msg.texture_update()
            raw_w = lbl_msg.texture_size[0]

            if raw_w > max_w:
                lbl_msg.text_size = (max_w, None)
                lbl_msg.texture_update()
            else:
                lbl_msg.text_size = (None, None)
                lbl_msg.texture_update()

            lbl_msg.size = lbl_msg.texture_size
            lbl_meta.texture_update()
            lbl_meta.size = lbl_meta.texture_size

            final_w = max(lbl_msg.width, lbl_meta.width) + 24
            final_h = lbl_msg.height + lbl_meta.height + 14

            content_box.size = (final_w, final_h)
            row_wrapper.height = final_h + 4

        recalculate_bubble_size()
        self.bind(width=recalculate_bubble_size)

        if is_me:
            row_wrapper.add_widget(BoxLayout(size_hint_x=1))
            row_wrapper.add_widget(content_box)
        else:
            display_name = sender_name if sender_name else self.peer_name
            avatar_box = AnchorLayout(
                size_hint=(None, None),
                size=('34dp', '34dp'),
                anchor_x='center',
                anchor_y='bottom'
            )
            peer_avatar = CircleAvatar(
                text=display_name,
                bg_color=(0.2, 0.5, 0.8, 1),
                size_dp=32
            )
            avatar_box.add_widget(peer_avatar)
            row_wrapper.add_widget(avatar_box)
            row_wrapper.add_widget(content_box)
            row_wrapper.add_widget(BoxLayout(size_hint_x=1))

        self.ids.chat_logs.add_widget(row_wrapper)
        self.scroll_to_bottom()

    def send_text(self):
        text = self.ids.txt_input.text.strip()
        if not text:
            return

        # ডিবাগ প্রিন্ট যুক্ত করা হয়েছে আইপি চেক করার জন্য
        print(f"DEBUG -> Sending to IP: {self.peer_ip}, Name: {self.peer_name}")

        now_time = datetime.now().strftime("%I:%M %p")
        my_name = self.get_my_name()

        self.ids.txt_input.text = ""
        self.add_message_bubble(text, is_me=True, sender_name=my_name, time_str=now_time, status="sent")

        app = App.get_running_app()
        if hasattr(app, 'net_service') and app.net_service:
            try:
                app.net_service.send_text_message(self.peer_ip, self.peer_name, text)
            except Exception as e:
                print(f"[Send Error Exception]: {e}")

    def on_message_received(self, data):
        def update_ui(dt):
            sender = data.get("sender", "")
            msg = data.get("message", "") if data.get("type") == "text" else f"[File] {data.get('filename')}"
            time_str = datetime.now().strftime("%I:%M %p")

            if self.manager and self.manager.current == 'chat' and sender == self.peer_name:
                self.add_message_bubble(msg, is_me=False, sender_name=sender, time_str=time_str)

        Clock.schedule_once(update_ui, 0)

    def scroll_to_bottom(self, *args):
        def _scroll(dt):
            self.ids.scroll_view.scroll_y = 0
        Clock.schedule_once(_scroll, 0.1)