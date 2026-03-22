"""
screens/historique.py - Historique CENAD avec photos presidents
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


def get_asset_path(filename):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in [filename, filename.lower(), filename.upper()]:
        p = os.path.join(base, 'assets', name)
        if os.path.exists(p):
            return p
    return os.path.join(base, 'assets', filename)


def get_president_photo(nom):
    """Cherche la photo du president dans la base de donnees membres."""
    if not nom:
        return ''
    try:
        import db_manager as db
        conn = db.get_connection()
        # Chercher par nom exact ou partiel
        row = conn.execute(
            "SELECT photo FROM membres WHERE nom LIKE ? LIMIT 1",
            ('%' + nom.split()[0] + '%',)
        ).fetchone()
        conn.close()
        if row:
            photo = dict(row).get('photo', '')
            if photo and os.path.exists(photo):
                return photo
    except Exception:
        pass
    # Sinon chercher dans assets/presidents/
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pres_dir = os.path.join(base, 'assets', 'presidents')
    os.makedirs(pres_dir, exist_ok=True)
    safe = nom.replace(' ', '_')
    for ext in ['jpg', 'jpeg', 'png', 'JPG', 'PNG']:
        p = os.path.join(pres_dir, '{}.{}'.format(safe, ext))
        if os.path.exists(p):
            return p
    return ''



PRESIDENTS = [
    ("", "2012 - 2013", ""),
    ("", "2013 - 2014", ""),
    ("", "2014 - 2015", ""),
    ("", "2015 - 2016", ""),
    ("", "2016 - 2018", ""),
    ("", "2018 - 2020", ""),
    ("JIMMY Richard", "2020 - 2022", "Gestion de la periode COVID-19, resilience associative."),
    ("", "2022 - 2023", ""),
    ("RALAHADY Fanios", "2023 - 2024", ""),
    ("Mysco Flobert", "2024 - 2025", ""),
    ("BEVITA Casmir", "2025 - present", ""),
]

HISTORIQUE_TEXT = """La CENAD (Communaute des Etudiants Natifs d'Andapa a Antsiranana) a ete fondee en 2012 par un groupe d'etudiants originaires d'Andapa et des communes environnantes.

OBJECTIFS FONDATEURS
- Favoriser l'entraide mutuelle entre etudiants
- Faciliter l'integration des nouveaux arrivants
- Promouvoir l'excellence academique
- Preserver les valeurs culturelles communes
- Creer un reseau professionnel durable

MISSION ACTUELLE
L'association organise regulierement des activites academiques, culturelles et sportives."""


class HistoriqueScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        with self.canvas.before:
            Color(0.05, 0.07, 0.22, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.bg, 'size', self.size),
                  pos=lambda *a: setattr(self.bg, 'pos', self.pos))

        main = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # Header
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

        icon_path = get_asset_path('icons/ic_historique.png')
        if os.path.exists(icon_path):
            header.add_widget(Image(source=icon_path, size_hint=(None, 1),
                                    width=dp(32), allow_stretch=True, keep_ratio=True))

        header.add_widget(Label(text="[b]HISTORIQUE CENAD[/b]", markup=True,
                                font_size=dp(15), color=(1, 0.85, 0.1, 1)))
        main.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(10),
                             size_hint_y=None, padding=(dp(5), dp(5)))
        content.bind(minimum_height=content.setter('height'))

        # Carte fondation
        fond = BoxLayout(size_hint_y=None, height=dp(55), padding=(dp(14), dp(5)))
        with fond.canvas.before:
            Color(0.09, 0.40, 0.78, 0.85)
            f_rect = Rectangle(size=fond.size, pos=fond.pos)
        fond.bind(size=lambda *a: setattr(f_rect, 'size', fond.size),
                  pos=lambda *a: setattr(f_rect, 'pos', fond.pos))
        fond.add_widget(Label(
            text="[b]Fondee en 2012[/b]  |  Antsiranana, Madagascar",
            markup=True, font_size=dp(13), color=(1, 1, 1, 1), halign='left'
        ))
        content.add_widget(fond)

        # Texte
        hist_lbl = Label(
            text=HISTORIQUE_TEXT, font_size=dp(12),
            color=(0.85, 0.9, 1, 0.95), halign='left',
            text_size=(None, None), size_hint_y=None
        )
        hist_lbl.bind(
            width=lambda *x: setattr(hist_lbl, 'text_size', (hist_lbl.width, None)),
            texture_size=lambda *x: setattr(hist_lbl, 'height', hist_lbl.texture_size[1])
        )
        content.add_widget(hist_lbl)

        # Presidents
        content.add_widget(Label(
            text="[b]PRESIDENTS SUCCESSIFS[/b]", markup=True,
            font_size=dp(14), color=(1, 0.85, 0.1, 1),
            size_hint_y=None, height=dp(38)
        ))

        for nom, annees, mission in PRESIDENTS:
            content.add_widget(PresidentCard(nom, annees, mission))



        scroll.add_widget(content)
        main.add_widget(scroll)
        self.add_widget(main)


class PresidentCard(BoxLayout):
    def __init__(self, nom, annees, mission, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None,
                         height=dp(68), spacing=dp(10),
                         padding=(dp(10), dp(8)), **kwargs)
        with self.canvas.before:
            Color(0.10, 0.15, 0.42, 0.8)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(8)])
        self.bind(size=lambda *a: setattr(self._rect, 'size', self.size),
                  pos=lambda *a: setattr(self._rect, 'pos', self.pos))

        # Cercle photo
        circle_box = BoxLayout(size_hint=(None, 1), width=dp(50))
        clr = (1, 0.85, 0.1, 1) if nom else (0.3, 0.35, 0.55, 0.6)
        with circle_box.canvas:
            Color(*clr)
            self._ell = Ellipse(size=(dp(44), dp(44)), pos=circle_box.pos)
        circle_box.bind(pos=lambda *a: setattr(
            self._ell, 'pos',
            (circle_box.x + dp(3), circle_box.y + (circle_box.height - dp(44))/2)
        ))

        photo_path = get_president_photo(nom)
        if photo_path:
            circle_box.add_widget(Image(
                source=photo_path, allow_stretch=True, keep_ratio=False,
                size_hint=(None, None), size=(dp(44), dp(44))
            ))
        else:
            initiale = nom[0].upper() if nom else '?'
            circle_box.add_widget(Label(
                text="[b]{}[/b]".format(initiale), markup=True,
                font_size=dp(20),
                color=(0.05, 0.05, 0.15, 1) if nom else (0.5, 0.55, 0.75, 0.8),
                halign='center', valign='middle'
            ))
        self.add_widget(circle_box)

        # Texte
        info = BoxLayout(orientation='vertical')
        nom_txt = nom if nom else "( Inconnu )"
        nom_clr = (1, 0.85, 0.1, 1) if nom else (0.5, 0.6, 0.7, 0.7)
        info.add_widget(Label(
            text="[b]{}[/b]".format(nom_txt), markup=True,
            font_size=dp(13), color=nom_clr, halign='left',
            size_hint_y=None, height=dp(22), text_size=(dp(215), None)
        ))
        info.add_widget(Label(
            text="{}".format(annees), font_size=dp(11),
            color=(0.6, 0.8, 1, 1), halign='left',
            size_hint_y=None, height=dp(18), text_size=(dp(215), None)
        ))
        if mission:
            info.add_widget(Label(
                text=mission, font_size=dp(10),
                color=(0.75, 0.85, 1, 0.85), halign='left',
                size_hint_y=None, height=dp(16), text_size=(dp(215), None)
            ))
        self.add_widget(info)
