import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock

KV_FILE_TRANSFER = '''
<FileTransferScreen>:
    name: 'file_transfer'
    canvas.before:
        Color:
            rgba: 0.07, 0.09, 0.15, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: [20, 15, 20, 15]
        spacing: 20

        # --- Header ---
        BoxLayout:
            size_hint_y: None
            height: '50dp'
            Button:
                text: '< Back'
                size_hint_x: None
                width: '80dp'
                background_normal: ''
                background_color: 0, 0, 0, 0
                color: 0.4, 0.7, 1, 1
                bold: True
                on_release: root.go_back_to_chat()
            Label:
                text: 'File Transfer'
                font_size: '20sp'
                bold: True
                color: 1, 1, 1, 1

        # --- Selected Card ---
        BoxLayout:
            orientation: 'vertical'
            padding: 15
            spacing: 10
            canvas.before:
                Color:
                    rgba: 0.12, 0.16, 0.23, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [12,]

            Label:
                id: lbl_selected
                text: 'No file selected'
                color: 0.7, 0.7, 0.8, 1
                font_size: '15sp'

            Button:
                text: 'Choose File'
                size_hint_y: None
                height: '45dp'
                background_normal: ''
                background_color: 0.2, 0.25, 0.35, 1
                color: 1, 1, 1, 1
                bold: True
                on_release: root.open_file_chooser()

        # --- Status Area ---
        Label:
            id: lbl_status
            text: 'Status: Idle'
            color: 0.5, 0.6, 0.7, 1
            font_size: '14sp'

        # --- Send Button ---
        Button:
            id: btn_send
            text: 'Send File Now'
            size_hint_y: None
            height: '50dp'
            background_normal: ''
            background_color: 0.39, 0.4, 0.95, 1
            color: 1, 1, 1, 1
            bold: True
            on_release: root.send_file_action()
'''

Builder.load_string(KV_FILE_TRANSFER)

class FileTransferScreen(Screen):
    selected_file_path = ''

    def open_file_chooser(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        filechooser = FileChooserListView(path=os.path.expanduser('~'))
        
        btn_layout = BoxLayout(size_hint_y=None, height='45dp', spacing=10)
        btn_select = Button(text="Select", background_normal='', background_color=(0.39, 0.4, 0.95, 1), bold=True)
        btn_cancel = Button(text="Cancel", background_normal='', background_color=(0.2, 0.25, 0.35, 1), bold=True)
        
        btn_layout.add_widget(btn_select)
        btn_layout.add_widget(btn_cancel)
        
        content.add_widget(filechooser)
        content.add_widget(btn_layout)
        
        popup = Popup(title="Choose File to Send", content=content, size_hint=(0.9, 0.85))
        
        def _on_select(instance):
            if filechooser.selection:
                self.selected_file_path = filechooser.selection[0]
                filename = os.path.basename(self.selected_file_path)
                size_mb = round(os.path.getsize(self.selected_file_path) / (1024 * 1024), 2)
                self.ids.lbl_selected.text = f"File: {filename}\nSize: {size_mb} MB"
                self.ids.lbl_status.text = "Status: Ready to send"
            popup.dismiss()

        btn_select.bind(on_release=_on_select)
        btn_cancel.bind(on_release=lambda x: popup.dismiss())
        popup.open()

    def send_file_action(self):
        if not self.selected_file_path or not os.path.exists(self.selected_file_path):
            self.ids.lbl_status.text = "Status: Please select a file first!"
            return

        self.ids.lbl_status.text = "Status: Transferring file..."
        self.ids.btn_send.disabled = True

        app = App.get_running_app()
        target_ip = getattr(app, 'current_peer_ip', '127.0.0.1')

        if app.net_service:
            app.net_service.send_file(
                target_ip, 
                self.selected_file_path, 
                callback_on_finish=self._on_transfer_finished
            )
        else:
            self.ids.lbl_status.text = "Status: Network service unavailable!"
            self.ids.btn_send.disabled = False

    def _on_transfer_finished(self, success):
        self.ids.btn_send.disabled = False
        if success:
            self.ids.lbl_status.text = "Status: Transfer complete!"
            Clock.schedule_once(self.go_back_to_chat, 2)
        else:
            self.ids.lbl_status.text = "Status: Transfer failed!"

    def go_back_to_chat(self, *args):
        self.selected_file_path = ''
        self.ids.lbl_selected.text = 'No file selected'
        self.ids.lbl_status.text = 'Status: Idle'
        
        if self.manager and self.manager.has_screen('chat'):
            self.manager.current = 'chat'