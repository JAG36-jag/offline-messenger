from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.app import App
from kivy.graphics import Color, RoundedRectangle, Ellipse

KV_CHATS = '''
<ChatsScreen>:
    name: 'chats'
    canvas.before:
        Color:
            rgba: 0.04, 0.07, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'

        # --- Top Header ---
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            padding: [15, 0, 15, 0]
            canvas.before:
                Color:
                    rgba: 0.12, 0.17, 0.2, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Label:
                text: 'Offline Messenger'
                font_size: '18sp'
                bold: True
                color: 0.95, 0.95, 0.95, 1
                halign: 'left'
                valign: 'middle'
                text_size: self.size

        # --- Recent Messages Scroll Area ---
        ScrollView:
            do_scroll_x: False
            BoxLayout:
                id: recent_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 2
                padding: [0, 5, 0, 5]
'''

Builder.load_string(KV_CHATS)


class CircleAvatar(AnchorLayout):
    def __init__(self, text="U", bg_color=(0.2, 0.5, 0.8, 1), size_dp=44, **kwargs):
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


class ChatTile(BoxLayout):
    def __init__(self, peer_name, last_msg, time_str, avatar_color, on_click_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = '72dp'
        self.padding = [15, 10, 15, 10]
        self.spacing = 14

        with self.canvas.before:
            Color(rgba=(0.08, 0.12, 0.15, 1))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0,])

        self.bind(pos=self._update_rect, size=self._update_rect)

        avatar = CircleAvatar(text=peer_name, bg_color=avatar_color, size_dp=46)

        text_box = BoxLayout(orientation='vertical', spacing=4)

        top_row = BoxLayout(orientation='horizontal', size_hint_y=None, height='22dp')
        lbl_name = Label(
            text=peer_name,
            font_size='16sp',
            bold=True,
            color=(0.95, 0.95, 0.95, 1),
            halign='left',
            valign='middle'
        )
        lbl_name.bind(size=lbl_name.setter('text_size'))

        lbl_time = Label(
            text=time_str,
            font_size='11sp',
            color=(0.5, 0.6, 0.65, 1),
            halign='right',
            valign='middle',
            size_hint_x=None,
            width='70dp'
        )
        lbl_time.bind(size=lbl_time.setter('text_size'))

        top_row.add_widget(lbl_name)
        top_row.add_widget(lbl_time)

        lbl_msg = Label(
            text=last_msg,
            font_size='13sp',
            color=(0.6, 0.65, 0.7, 1),
            halign='left',
            valign='middle'
        )
        lbl_msg.bind(size=lbl_msg.setter('text_size'))

        text_box.add_widget(top_row)
        text_box.add_widget(lbl_msg)

        self.add_widget(avatar)
        self.add_widget(text_box)

        self.callback = on_click_callback

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.callback:
                self.callback()
            return True
        return super().on_touch_down(touch)


class ChatsScreen(Screen):

    def on_enter(self):
        self.load_recent_chats()

    def load_recent_chats(self):
        self.ids.recent_list.clear_widgets()
        app = App.get_running_app()

        if hasattr(app, 'net_service') and hasattr(app.net_service, 'db'):
            try:
                chats = app.net_service.db.get_recent_chats()
            except Exception:
                chats = []

            if not chats:
                empty_lbl = Label(
                    text="No conversations yet.\nMessages will appear here.",
                    font_size='14sp',
                    color=(0.5, 0.6, 0.65, 1),
                    halign='center',
                    valign='middle',
                    size_hint_y=None,
                    height='120dp'
                )
                empty_lbl.bind(size=empty_lbl.setter('text_size'))
                self.ids.recent_list.add_widget(empty_lbl)
                return

            colors = [
                (0.2, 0.5, 0.8, 1),
                (0.0, 0.6, 0.5, 1),
                (0.8, 0.3, 0.3, 1),
                (0.6, 0.3, 0.8, 1)
            ]

            for idx, chat in enumerate(chats):
                peer_name = str(chat[0]) if chat[0] is not None else "Unknown"
                last_msg = str(chat[1]) if chat[1] is not None else ""
                time_str = str(chat[2]) if len(chat) > 2 and chat[2] else ""

                avatar_color = colors[idx % len(colors)]
                tile = ChatTile(
                    peer_name=peer_name,
                    last_msg=last_msg,
                    time_str=time_str,
                    avatar_color=avatar_color,
                    on_click_callback=lambda p=peer_name: self.open_chat(p)
                )
                self.ids.recent_list.add_widget(tile)

    def open_chat(self, peer_name):
        chat_screen = self.manager.get_screen('chat')
        app = App.get_running_app()
        peer_ip = "127.0.0.1"

        if hasattr(app, 'net_service') and hasattr(app.net_service, 'active_peers'):
            peer_ip = app.net_service.active_peers.get(str(peer_name), "127.0.0.1")

        chat_screen.set_active_peer(str(peer_name), str(peer_ip))
        self.manager.current = 'chat'