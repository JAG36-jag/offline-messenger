from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.app import App
from kivy.clock import Clock

KV_DISCOVERING = '''
<DiscoveringScreen>:
    name: 'discovering'
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 10
        Label:
            text: 'Discovering Nearby Peers...'
            font_size: '18sp'
            bold: True
            size_hint_y: 0.1
        ScrollView:
            BoxLayout:
                id: peers_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
        Button:
            text: 'Go to Chats'
            size_hint_y: 0.1
            on_release: root.manager.current = 'chats'
'''

Builder.load_string(KV_DISCOVERING)

class DiscoveringScreen(Screen):
    def on_enter(self):
        Clock.schedule_interval(self.refresh_peers, 2)

    def on_leave(self):
        Clock.unschedule(self.refresh_peers)

    def refresh_peers(self, dt):
        app = App.get_running_app()
        if not app.net_service:
            return

        self.ids.peers_list.clear_widgets()
        for peer_name, peer_ip in app.net_service.discovered_peers.items():
            btn = Button(
                text=f"{peer_name} ({peer_ip})",
                size_hint_y=None,
                height=50,
                background_color=(0.2, 0.6, 0.8, 1)
            )
            btn.bind(on_release=lambda x, name=peer_name, ip=peer_ip: self.connect_to_peer(name, ip))
            self.ids.peers_list.add_widget(btn)

    def connect_to_peer(self, name, ip):
        app = App.get_running_app()
        app.current_peer_name = name
        app.current_peer_ip = ip
        if self.manager.has_screen('chat'):
            chat_screen = self.manager.get_screen('chat')
            chat_screen.set_active_peer(name, ip)
            self.manager.current = 'chat'