import json
import os

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.toast import toast


def display_cap(text):
    """Ko'rsatish uchun birinchi harfni katta qiladi, qolganiga tegmaydi."""
    if not text:
        return text
    return text[0].upper() + text[1:]


KV = """
MDBoxLayout:
    orientation: 'vertical'

    MDTopAppBar:
        title: "Smart Lug'at"
        elevation: 4
        left_action_items: [["book-alphabet", lambda x: None]]

    MDBoxLayout:
        orientation: 'vertical'
        spacing: "10dp"
        padding: "12dp"

        # 1. So'z qo'shish qismi
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: "8dp"
            size_hint_y: None
            height: "56dp"

            MDTextField:
                id: word_input
                hint_text: "Kalit (so'z)"
                mode: "rectangle"

            MDTextField:
                id: trans_input
                hint_text: "Tarjima"
                mode: "rectangle"

        MDRaisedButton:
            text: "QO'SHISH"
            icon: "plus"
            size_hint_x: 1
            pos_hint: {"center_x": .5}
            on_release: app.add_word()

        # 2. Saralash tugmalari
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: "8dp"
            size_hint_y: None
            height: "40dp"

            MDFlatButton:
                text: "Kalit bo'yicha"
                size_hint_x: 0.5
                on_release: app.load_data(sort_by="key")

            MDFlatButton:
                text: "Tarjima bo'yicha"
                size_hint_x: 0.5
                on_release: app.load_data(sort_by="value")

        # 3. Qidiruv
        MDTextField:
            id: search_input
            hint_text: "Qidirish..."
            mode: "fill"
            icon_left: "magnify"
            size_hint_y: None
            height: "48dp"
            on_text: app.search_words(self.text)

        MDLabel:
            id: count_label
            text: "0 ta so'z"
            theme_text_color: "Secondary"
            font_style: "Caption"
            size_hint_y: None
            height: "20dp"

        # 4. Natijalar ro'yxati (scroll bilan)
        MDScrollView:
            do_scroll_x: False
            MDBoxLayout:
                id: word_list
                orientation: 'vertical'
                spacing: "6dp"
                padding: "2dp"
                adaptive_height: True
"""


class WordCard(MDCard):
    """Bitta so'z uchun karta: matn + tahrirlash + o'chirish tugmalari"""

    def __init__(self, key, value, app, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.value = value
        self.app = app

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(64)
        self.padding = (dp(12), dp(6))
        self.spacing = dp(8)
        self.radius = [12]
        self.elevation = 1
        self.md_bg_color = self.app.theme_cls.bg_light

        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDIconButton

        self.label = MDLabel(
            text=f"[b]{display_cap(key)}[/b]\n{display_cap(value)}",
            markup=True,
            halign="left",
            valign="middle",
        )
        self.add_widget(self.label)

        edit_btn = MDIconButton(icon="pencil", on_release=self.on_edit)
        delete_btn = MDIconButton(
            icon="trash-can-outline",
            theme_text_color="Custom",
            text_color=(0.8, 0.2, 0.2, 1),
            on_release=self.on_delete,
        )
        self.add_widget(edit_btn)
        self.add_widget(delete_btn)

    def on_edit(self, *args):
        self.app.open_edit_dialog(self.key, self.value)

    def on_delete(self, *args):
        self.app.confirm_delete(self.key)


class DictionaryApp(MDApp):
    APP_FOLDER_NAME = "SmartLugat"
    FILE_NAME = "lugat.json"

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        self.dialog = None
        self.file_path = self.get_storage_path()
        return Builder.load_string(KV)

    # ------------------------------------------------------------------
    # Saqlash joyi: Android'da ilovaning alohida papkasi, aks holda uy papkasi
    # ------------------------------------------------------------------
    def get_storage_path(self):
        if platform == "android":
            try:
                from jnius import autoclass

                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                context = PythonActivity.mActivity
                # App-specific external storage — ruxsat so'ramasdan ishlaydi,
                # Android 10+ scoped storage bilan ham mos keladi.
                # Yo'l: /storage/emulated/0/Android/data/<package>/files/SmartLugat
                base_dir = context.getExternalFilesDir(None).getAbsolutePath()
            except Exception:
                base_dir = self.user_data_dir
        else:
            base_dir = os.path.join(os.path.expanduser("~"), self.APP_FOLDER_NAME)

        folder = os.path.join(base_dir, self.APP_FOLDER_NAME) if platform == "android" else base_dir
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, self.FILE_NAME)

    def on_start(self):
        self.ensure_json_exists()
        self.load_data()

    # ------------------------------------------------------------------
    # JSON bilan ishlash
    # ------------------------------------------------------------------
    def ensure_json_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)

    def read_json(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def write_json(self, data):
        sorted_data = dict(sorted(data.items()))
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(sorted_data, f, ensure_ascii=False, indent=4)

    # ------------------------------------------------------------------
    # Ro'yxatni chizish
    # ------------------------------------------------------------------
    def load_data(self, sort_by="key", filter_dict=None, *args):
        container = self.root.ids.word_list
        container.clear_widgets()

        data = filter_dict if filter_dict is not None else self.read_json()

        if sort_by == "key":
            sorted_items = sorted(data.items(), key=lambda x: x[0].lower())
        elif sort_by == "value":
            sorted_items = sorted(data.items(), key=lambda x: x[1].lower())
        else:
            sorted_items = data.items()

        for key, value in sorted_items:
            container.add_widget(WordCard(key, value, self))

        self.root.ids.count_label.text = f"{len(data)} ta so'z"

    # ------------------------------------------------------------------
    # Qo'shish
    # ------------------------------------------------------------------
    def add_word(self):
        word = self.root.ids.word_input.text.strip()
        translation = self.root.ids.trans_input.text.strip()

        if not word or not translation:
            toast("Ikkala maydonni ham to'ldiring")
            return

        data = self.read_json()
        data[word] = translation
        self.write_json(data)

        self.root.ids.word_input.text = ""
        self.root.ids.trans_input.text = ""
        self.root.ids.search_input.text = ""

        self.load_data()
        toast(f"'{word}' qo'shildi")

    # ------------------------------------------------------------------
    # Qidirish
    # ------------------------------------------------------------------
    def search_words(self, text):
        query = text.strip().lower()
        data = self.read_json()

        if not query:
            self.load_data()
            return

        filtered = {
            k: v for k, v in data.items()
            if query in k.lower() or query in v.lower()
        }
        self.load_data(sort_by="none", filter_dict=filtered)

    # ------------------------------------------------------------------
    # Tahrirlash
    # ------------------------------------------------------------------
    def open_edit_dialog(self, old_key, old_value):
        self.edit_key_field = MDTextFieldForDialog(text=old_key, hint_text="Kalit")
        self.edit_value_field = MDTextFieldForDialog(text=old_value, hint_text="Tarjima")

        self._edit_old_key = old_key

        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height="120dp",
        )
        content.add_widget(self.edit_key_field)
        content.add_widget(self.edit_value_field)

        self.dialog = MDDialog(
            title="So'zni tahrirlash",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="BEKOR QILISH", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="SAQLASH", on_release=self.save_edit),
            ],
        )
        self.dialog.open()

    def save_edit(self, *args):
        new_key = self.edit_key_field.text.strip()
        new_value = self.edit_value_field.text.strip()
        old_key = self._edit_old_key

        if not new_key or not new_value:
            toast("Ikkala maydonni ham to'ldiring")
            return

        data = self.read_json()
        if old_key in data:
            del data[old_key]
        data[new_key] = new_value
        self.write_json(data)

        self.dialog.dismiss()
        self.load_data()
        toast("O'zgarishlar saqlandi")

    # ------------------------------------------------------------------
    # O'chirish
    # ------------------------------------------------------------------
    def confirm_delete(self, key):
        self._delete_key = key
        self.dialog = MDDialog(
            title="O'chirishni tasdiqlang",
            text=f"'{key}' so'zini o'chirmoqchimisiz?",
            buttons=[
                MDFlatButton(text="BEKOR QILISH", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(
                    text="O'CHIRISH",
                    theme_text_color="Custom",
                    text_color=(0.8, 0.2, 0.2, 1),
                    on_release=self.do_delete,
                ),
            ],
        )
        self.dialog.open()

    def do_delete(self, *args):
        data = self.read_json()
        data.pop(self._delete_key, None)
        self.write_json(data)
        self.dialog.dismiss()
        self.load_data()
        toast("So'z o'chirildi")


# Dialog ichidagi input maydoni uchun yordamchi klass
from kivymd.uix.textfield import MDTextField


class MDTextFieldForDialog(MDTextField):
    pass


if __name__ == "__main__":
    DictionaryApp().run()
