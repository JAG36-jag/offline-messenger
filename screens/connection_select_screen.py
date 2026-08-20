import os
import sys
import socket
import json
import base64
import threading

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

# থিম সাপোর্ট
try:
    from theme.theme_manager import theme
    BACKGROUND_COLOR = theme.BACKGROUND
    SURFACE_COLOR = theme.SURFACE
    PRIMARY_COLOR = theme.PRIMARY
    TEXT_PRIMARY_COLOR = theme.TEXT_PRIMARY
    TEXT_SECONDARY_COLOR = theme.TEXT_SECONDARY
except ModuleNotFoundError:
    BACKGROUND_COLOR = (0.08, 0.08, 0.12, 1)
    SURFACE_COLOR = (0.14, 0.14, 0.20, 1)
    PRIMARY_COLOR = (0.4, 0.3, 0.9, 1)
    TEXT_PRIMARY_COLOR = (1, 1, 1, 1)
    TEXT_SECONDARY_COLOR = (0.7, 0.7, 0.8, 1)

HOTSPOT_PORT = 50005
HOTSPOT_REQ = b"REAL_HOTSPOT_DISCOVER_REQ"
HOTSPOT_RESP_PREFIX = "REAL_HOTSPOT_USER:"

HOTSPOT_ICON_PATH = os.path.join(PROJECT_ROOT, 'assets', 'hospot.icon.png')
BLUETOOTH_ICON_PATH = os.path.join(PROJECT_ROOT, 'assets', 'blutooth.icon.png')


class ConnectionSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.is_scanning = False
        self.selected_device = None
        self.found_devices = {}
        self.scan_mode = "ALL"

        main_layout = BoxLayout(orientation='vertical')

        with main_layout.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.rect = RoundedRectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_rect, pos=self._update_rect)

        # ১. হেডার বার (Header Bar)
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=[dp(10), dp(5)],
            spacing=dp(10)
        )
        with top_bar.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            self.top_rect = RoundedRectangle(size=top_bar.size, pos=top_bar.pos)
        top_bar.bind(size=self._update_top_rect, pos=self._update_top_rect)

        btn_back = Button(
            text="<",
            font_size='26sp',
            bold=True,
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        btn_back.bind(on_release=self.go_back)

        lbl_title = Label(
            text="[b]Nearby Connections[/b]",
            markup=True,
            font_size='18sp',
            color=TEXT_PRIMARY_COLOR,
            halign='center',
            valign='middle',
            pos_hint={'center_y': 0.5}
        )

        self.btn_scan = Button(
            text="Scan",
            font_size='14sp',
            bold=True,
            size_hint=(None, None),
            size=(dp(60), dp(40)),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=PRIMARY_COLOR
        )
        self.btn_scan.bind(on_release=self.start_mesh_scan)

        top_bar.add_widget(btn_back)
        top_bar.add_widget(lbl_title)
        top_bar.add_widget(self.btn_scan)

        # ২. ট্যাব ফিল্টার (All, Hotspot, Bluetooth)
        tab_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(45),
            padding=[dp(15), dp(5)],
            spacing=dp(15)
        )

        self.btn_tab_all = Button(
            text="All",
            bold=True,
            font_size='13sp',
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        self.btn_tab_all.bind(on_release=lambda x: self.set_scan_mode("ALL"))

        tab_hotspot_box = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint=(1, 1))
        img_hotspot = Image(source=HOTSPOT_ICON_PATH, size_hint=(None, None), size=(dp(18), dp(18)), pos_hint={'center_y': 0.5})
        self.lbl_tab_hotspot = Label(text="Hotspot", bold=True, font_size='13sp', color=TEXT_SECONDARY_COLOR, pos_hint={'center_y': 0.5})
        tab_hotspot_box.add_widget(img_hotspot)
        tab_hotspot_box.add_widget(self.lbl_tab_hotspot)

        tab_bt_box = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint=(1, 1))
        img_bt = Image(source=BLUETOOTH_ICON_PATH, size_hint=(None, None), size=(dp(18), dp(18)), pos_hint={'center_y': 0.5})
        self.lbl_tab_bt = Label(text="Bluetooth", bold=True, font_size='13sp', color=TEXT_SECONDARY_COLOR, pos_hint={'center_y': 0.5})
        tab_bt_box.add_widget(img_bt)
        tab_bt_box.add_widget(self.lbl_tab_bt)

        tab_box.add_widget(self.btn_tab_all)
        tab_box.add_widget(tab_hotspot_box)
        tab_box.add_widget(tab_bt_box)

        tab_hotspot_box.bind(on_touch_down=lambda instance, touch: self._on_tab_click(touch, instance, "HOTSPOT"))
        tab_bt_box.bind(on_touch_down=lambda instance, touch: self._on_tab_click(touch, instance, "BLUETOOTH"))

        # ৩. ডিভাইস লিস্ট / স্ক্যান রেজাল্ট
        scroll = ScrollView(size_hint=(1, 1))
        self.device_list = GridLayout(cols=1, spacing=dp(12), padding=[dp(15), dp(15)], size_hint_y=None)
        self.device_list.bind(minimum_height=self.device_list.setter('height'))
        scroll.add_widget(self.device_list)

        self.lbl_status = Label(
            text="Turn on Hotspot/Bluetooth & tap Scan",
            font_size='12sp',
            color=TEXT_SECONDARY_COLOR,
            size_hint_y=None,
            height=dp(25)
        )

        # ৪. কানেক্ট বাটন ও বটম এরিয়া
        btn_connect = Button(
            text="Select Device & Connect",
            size_hint=(1, None),
            height=dp(50),
            bold=True,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        with btn_connect.canvas.before:
            Color(*PRIMARY_COLOR)
            btn_connect.bg_rect = RoundedRectangle(size=btn_connect.size, pos=btn_connect.pos, radius=[dp(12)])
        btn_connect.bind(size=self._update_btn_rect, pos=self._update_btn_rect)
        btn_connect.bind(on_release=self.connect_to_selected)

        bottom_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(95),
            padding=[dp(15), dp(5)],
            spacing=dp(5)
        )
        bottom_box.add_widget(self.lbl_status)
        bottom_box.add_widget(btn_connect)

        main_layout.add_widget(top_bar)
        main_layout.add_widget(tab_box)
        main_layout.add_widget(scroll)
        main_layout.add_widget(bottom_box)

        self.add_widget(main_layout)

        # ব্যাকগ্রাউন্ড লিসেনার থ্রেড চালু করা
        threading.Thread(target=self._listen_for_hotspot_scans, daemon=True).start()

    # --- ট্যাব ও মোড ফ্লাগ কন্ট্রোল ---
    def _on_tab_click(self, touch, widget, mode):
        if widget.collide_point(*touch.pos):
            self.set_scan_mode(mode)
            return True
        return False

    def set_scan_mode(self, mode):
        self.scan_mode = mode
        self.btn_tab_all.color = (1, 1, 1, 1) if mode == "ALL" else TEXT_SECONDARY_COLOR
        self.lbl_tab_hotspot.color = (1, 1, 1, 1) if mode == "HOTSPOT" else TEXT_SECONDARY_COLOR
        self.lbl_tab_bt.color = (1, 1, 1, 1) if mode == "BLUETOOTH" else TEXT_SECONDARY_COLOR
        self._render_found_devices()

    # --- স্ক্যানিং ব্যাকএন্ড নেটওয়ার্ক লজিক ---
    def start_mesh_scan(self, *args):
        if self.is_scanning:
            return

        self.is_scanning = True
        self.lbl_status.text = "Scanning nearby real devices..."
        self.btn_scan.text = "..."
        self.device_list.clear_widgets()
        self.found_devices.clear()

        threading.Thread(target=self._scan_hotspot_subnet, daemon=True).start()

    def _scan_hotspot_subnet(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2.0)

        try:
            sock.sendto(HOTSPOT_REQ, ('255.255.255.255', HOTSPOT_PORT))
            while True:
                data, addr = sock.recvfrom(4096)
                msg = data.decode('utf-8', errors='ignore')

                if msg.startswith(HOTSPOT_RESP_PREFIX):
                    payload = json.loads(msg.replace(HOTSPOT_RESP_PREFIX, ""))
                    peer_name = payload.get("name", "User")
                    peer_avatar_b64 = payload.get("avatar_b64", None)

                    avatar_file_path = None
                    if peer_avatar_b64:
                        try:
                            avatar_bytes = base64.b64decode(peer_avatar_b64)
                            avatar_file_path = os.path.join(PROJECT_ROOT, f"temp_{addr[0]}.png")
                            with open(avatar_file_path, "wb") as f:
                                f.write(avatar_bytes)
                        except Exception as e:
                            print(f"Error saving avatar: {e}")

                    if addr[0] not in self.found_devices:
                        self.found_devices[addr[0]] = {
                            "name": peer_name,
                            "ip": addr[0],
                            "avatar": avatar_file_path,
                            "type": "HOTSPOT",
                            "icon": HOTSPOT_ICON_PATH
                        }
        except Exception:
            pass
        finally:
            sock.close()

        Clock.schedule_once(lambda dt: self._render_found_devices())

    def _listen_for_hotspot_scans(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            sock.bind(('', HOTSPOT_PORT))
            while True:
                data, addr = sock.recvfrom(1024)
                if data == HOTSPOT_REQ:
                    my_name = "User"
                    my_avatar_b64 = None

                    if self.manager and self.manager.has_screen('chat'):
                        chat_screen = self.manager.get_screen('chat')
                        my_name = getattr(chat_screen, 'my_name', 'User')
                        image_path = getattr(chat_screen, 'image_path', None)
                        if image_path and os.path.exists(image_path):
                            try:
                                with open(image_path, "rb") as f:
                                    my_avatar_b64 = base64.b64encode(f.read()).decode('utf-8')
                            except Exception:
                                pass

                    payload = json.dumps({"name": my_name, "avatar_b64": my_avatar_b64})
                    reply = f"{HOTSPOT_RESP_PREFIX}{payload}".encode('utf-8')
                    sock.sendto(reply, addr)
        except Exception:
            pass

    # --- ডিভাইস রেন্ডারিং ও ইউআই আপডেট ---
    def _render_found_devices(self):
        self.is_scanning = False
        self.btn_scan.text = "Scan"
        self.device_list.clear_widgets()

        filtered_devices = {
            k: v for k, v in self.found_devices.items()
            if self.scan_mode == "ALL" or v["type"] == self.scan_mode
        }

        if not filtered_devices:
            self.lbl_status.text = f"No {self.scan_mode.lower()} device found!"
            return

        self.lbl_status.text = f"Found {len(filtered_devices)} active device(s)"

        for address, dev in filtered_devices.items():
            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(60),
                padding=[dp(12), dp(8)],
                spacing=dp(12)
            )

            with row.canvas.before:
                Color(*SURFACE_COLOR)
                row.rect = RoundedRectangle(size=row.size, pos=row.pos, radius=[dp(10)])
            row.bind(size=self._update_item_rect, pos=self._update_item_rect)

            icon_path = dev['icon'] if os.path.exists(dev['icon']) else HOTSPOT_ICON_PATH
            dev_icon = Image(source=icon_path, size_hint=(None, None), size=(dp(28), dp(28)), pos_hint={'center_y': 0.5})

            lbl_info = Label(
                text=f"[b]{dev['name']}[/b]\n[size=11sp]{dev['ip']}[/size]",
                markup=True,
                halign='left',
                valign='middle',
                color=TEXT_PRIMARY_COLOR
            )
            lbl_info.bind(size=lbl_info.setter('text_size'))

            row.add_widget(dev_icon)
            row.add_widget(lbl_info)

            row.bind(on_touch_down=lambda instance, touch, d=dev: self._handle_item_click(instance, touch, d))
            self.device_list.add_widget(row)

    def _handle_item_click(self, instance, touch, device_data):
        if instance.collide_point(*touch.pos):
            self.selected_device = device_data
            self.lbl_status.text = f"Selected: {device_data['name']}"
            return True
        return False

    def connect_to_selected(self, *args):
        if not self.selected_device:
            self.lbl_status.text = "Select a device first!"
            return

        if self.manager:
            if self.manager.has_screen('chat'):
                chat_screen = self.manager.get_screen('chat')
                if hasattr(chat_screen, 'on_peer_connected'):
                    chat_screen.on_peer_connected(
                        peer_name=self.selected_device['name'],
                        peer_avatar=self.selected_device['avatar']
                    )
            self.manager.current = 'chat'

    def go_back(self, *args):
        if self.manager:
            if self.manager.has_screen('register'):
                self.manager.current = 'register'
            elif self.manager.has_screen('chat'):
                self.manager.current = 'chat'

    # --- ক্যানভাস সাইজ আপডেট হ্যান্ডলার ---
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_top_rect(self, instance, value):
        self.top_rect.pos = instance.pos
        self.top_rect.size = instance.size

    def _update_btn_rect(self, instance, value):
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size

    def _update_item_rect(self, instance, value):
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size