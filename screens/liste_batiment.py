"""
screens/liste_batiment.py - Liste membres par batiment avec photos rondes
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.metrics import dp
import os
import db_manager as db


def get_asset_path(filename):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in [filename, filename.lower(), filename.upper()]:
        p = os.path.join(base, 'assets', name)
        if os.path.exists(p):
            return p
    return os.path.join(base, 'assets', filename)


COLORS = ['#1565C0', '#1B5E20', '#4A148C', '#BF360C', '#006064', '#37474F',
          '#0277BD', '#558B2F', '#6A1B9A', '#E65100']


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))


class ListeBatimentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._built = False

    def on_enter(self):
        if not self._built:
            self._build_ui()
            self._built = True
        else:
            self._load_data()

    def _build_ui(self):
        with self.canvas.before:
            Color(0.05, 0.07, 0.22, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.bg, 'size', self.size),
                  pos=lambda *a: setattr(self.bg, 'pos', self.pos))

        main = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # Header avec icone
        header = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10))
        with header.canvas.before:
            Color(0.04, 0.05, 0.18, 1)
            h_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda *a: setattr(h_rect, 'size', header.size),
                    pos=lambda *a: setattr(h_rect, 'pos', header.pos))

        back_btn = Button(text="< Retour", size_hint=(None, 1), width=dp(80),
                          background_color=(0.15, 0.25, 0.6, 1), background_normal='',
                          font_size=dp(12), color=(1, 1, 1, 1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        header.add_widget(back_btn)

        # Icone batiment
        icon_path = get_asset_path('icons/ic_batiment.png')
        if os.path.exists(icon_path):
            header.add_widget(Image(source=icon_path, size_hint=(None, 1),
                                    width=dp(32), allow_stretch=True, keep_ratio=True))

        header.add_widget(Label(text="[b]LISTE PAR BATIMENT[/b]", markup=True,
                                font_size=dp(15), color=(1, 0.85, 0.1, 1)))
        main.add_widget(header)

        scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', spacing=dp(10),
                                  size_hint_y=None, padding=(0, dp(5)))
        self.content.bind(minimum_height=self.content.setter('height'))
        scroll.add_widget(self.content)
        main.add_widget(scroll)
        self.add_widget(main)
        self._load_data()

    def _load_data(self):
        self.content.clear_widgets()
        conn = db.get_connection()
        rows = conn.execute(
            "SELECT batiment, COUNT(*) as total FROM membres GROUP BY batiment ORDER BY batiment"
        ).fetchall()
        conn.close()
        batiments = [dict(r) for r in rows]

        for i, row in enumerate(batiments):
            name = row['batiment'] or 'Non defini'
            total = row['total']
            color = COLORS[i % len(COLORS)]
            self.content.add_widget(BatimentSection(name, total, color))


class BatimentSection(BoxLayout):
    def __init__(self, batiment_name, total, color_hex, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, spacing=dp(3), **kwargs)
        r, g, b = hex_rgb(color_hex)

        # En-tete
        header = BoxLayout(size_hint_y=None, height=dp(52), padding=(dp(12), 0))
        with header.canvas.before:
            Color(r, g, b, 0.9)
            h_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda *a: setattr(h_rect, 'size', header.size),
                    pos=lambda *a: setattr(h_rect, 'pos', header.pos))

        header.add_widget(Label(
            text="[b]{}[/b]  ({} membre{})".format(
                batiment_name, total, 's' if total > 1 else ''),
            markup=True, font_size=dp(14), color=(1, 1, 1, 1), halign='left'
        ))
        self.add_widget(header)

        # Membres
        conn = db.get_connection()
        rows = conn.execute(
            "SELECT nom, sexe, niveau, promotion, etablissement, photo FROM membres WHERE batiment=? ORDER BY nom",
            (batiment_name,)
        ).fetchall()
        conn.close()
        membres = [dict(m) for m in rows]

        for m in membres:
            self.add_widget(MemberRowCircle(m, r, g, b))

        self.height = dp(52) + len(membres) * dp(56) + dp(8)


class MemberRowCircle(BoxLayout):
    def __init__(self, membre, r, g, b, **kwargs):
        super().__init__(size_hint_y=None, height=dp(56),
                         padding=(dp(10), dp(6)), spacing=dp(10), **kwargs)
        with self.canvas.before:
            Color(r*0.25, g*0.25, b*0.25+0.08, 0.85)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(6)])
        self.bind(size=lambda *a: setattr(self._rect, 'size', self.size),
                  pos=lambda *a: setattr(self._rect, 'pos', self.pos))

        # Photo ronde
        self.add_widget(RoundPhoto(membre))

        # Info
        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(
            text=membre['nom'], font_size=dp(13), bold=True,
            color=(1, 1, 1, 1), halign='left', text_size=(dp(170), None)
        ))
        info.add_widget(Label(
            text="{} | {}".format(membre['etablissement'] or '', membre['promotion'] or ''),
            font_size=dp(10), color=(0.7, 0.85, 1, 0.8),
            halign='left', text_size=(dp(170), None)
        ))
        self.add_widget(info)

        # Badge niveau
        self.add_widget(Label(
            text="[b]{}[/b]".format(membre['niveau'] or ''), markup=True,
            size_hint=(None, 1), width=dp(36),
            font_size=dp(11), color=(1, 0.85, 0.1, 1), bold=True
        ))


class RoundPhoto(BoxLayout):
    """Photo avec cercle colore ou initiale."""
    def __init__(self, membre, size_dp=40, **kwargs):
        super().__init__(size_hint=(None, None),
                         size=(dp(size_dp), dp(size_dp)), **kwargs)
        photo = membre.get('photo', '') or ''
        nom = membre.get('nom', '?')
        sexe = membre.get('sexe', 'M')
        sexe_color = (0.25, 0.6, 1, 1) if sexe == 'M' else (1, 0.45, 0.75, 1)

        with self.canvas:
            Color(*sexe_color)
            self._ell = Ellipse(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self._ell, 'size', self.size),
                  pos=lambda *a: setattr(self._ell, 'pos', self.pos))

        if photo and os.path.exists(photo):
            img = Image(source=photo, allow_stretch=True, keep_ratio=True,
                        size_hint=(None, None), size=(dp(size_dp), dp(size_dp)),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5})
            self.add_widget(img)
        else:
            self.add_widget(Label(
                text="[b]{}[/b]".format(nom[0].upper()), markup=True,
                font_size=dp(size_dp * 0.45), color=(1, 1, 1, 1),
                halign='center', valign='middle'
            ))
