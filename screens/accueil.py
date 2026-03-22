"""
screens/accueil.py - Ecran d'accueil CENAD
Menu hamburger lateral + photo groupe + boutons icones+texte
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.utils import platform
import os


def get_asset_path(filename):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in [filename, filename.lower(), filename.upper()]:
        p = os.path.join(base, 'assets', name)
        if os.path.exists(p):
            return p
    return os.path.join(base, 'assets', filename)


# Icones en texte Unicode (compatibles Android sans emoji)
NAV_ITEMS = [
    ("  [b]Dashboard[/b]\n  Tableau de bord",     "dashboard",      (0.09, 0.40, 0.78, 1)),
    ("  [b]Batiment[/b]\n  Liste par batiment",    "liste_batiment", (0.11, 0.37, 0.13, 1)),
    ("  [b]Promotion[/b]\n  Liste par promotion",  "liste_promotion",(0.29, 0.08, 0.55, 1)),
    ("  [b]Historique[/b]\n  Historique CENAD",    "historique",     (0.75, 0.21, 0.05, 1)),
    ("  [b]Etablissements[/b]\n  Universites",     "etablissements", (0.00, 0.38, 0.39, 1)),
    ("  [b]Administration[/b]\n  Espace admin",    "admin",          (0.22, 0.28, 0.36, 1)),
]

# Icones SVG-like dessinées avec Canvas (barres colorées à gauche du texte)
ICON_COLORS = [
    (0.25, 0.60, 1.00, 1),   # bleu
    (0.20, 0.75, 0.40, 1),   # vert
    (0.65, 0.35, 1.00, 1),   # violet
    (1.00, 0.45, 0.20, 1),   # orange
    (0.20, 0.80, 0.80, 1),   # cyan
    (0.65, 0.75, 0.85, 1),   # gris-bleu
]

ICON_FILES = [
    'ic_dashboard.png',
    'ic_batiment.png',
    'ic_promotion.png',
    'ic_historique.png',
    'ic_etablissement.png',
    'ic_admin.png',
]


class AccueilScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._menu_open = False
        self.build_ui()

    def build_ui(self):
        # Fond principal
        with self.canvas.before:
            Color(0.07, 0.09, 0.30, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        # FloatLayout pour superposer menu par-dessus
        self.root_layout = FloatLayout()

        # ── CONTENU PRINCIPAL ──
        self.main_content = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )

        # Barre du haut
        topbar = BoxLayout(size_hint_y=None, height=dp(56), padding=(dp(8), dp(6)))
        with topbar.canvas.before:
            Color(0.05, 0.07, 0.22, 1)
            self._topbar_rect = Rectangle(size=topbar.size, pos=topbar.pos)
        topbar.bind(size=lambda *a: setattr(self._topbar_rect, 'size', topbar.size),
                    pos=lambda *a: setattr(self._topbar_rect, 'pos', topbar.pos))

        # Bouton hamburger
        self.hamburger_btn = HamburgerButton()
        self.hamburger_btn.bind(on_release=self._toggle_menu)
        topbar.add_widget(self.hamburger_btn)

        topbar.add_widget(Label(
            text="[b]CENAD[/b]", markup=True,
            font_size=dp(20), color=(1, 0.85, 0.1, 1),
            halign='center'
        ))
        topbar.add_widget(Widget(size_hint_x=None, width=dp(48)))  # équilibre
        self.main_content.add_widget(topbar)

        # Zone scrollable
        scroll = ScrollView()
        inner = BoxLayout(orientation='vertical', size_hint_y=None,
                          padding=(dp(14), dp(10)), spacing=dp(12))
        inner.bind(minimum_height=inner.setter('height'))

        # ── LOGO CENAD ──
        logo_box = BoxLayout(orientation='vertical', size_hint_y=None,
                             height=dp(210), padding=(dp(10), dp(8)), spacing=dp(4))
        with logo_box.canvas.before:
            Color(0.04, 0.06, 0.22, 1)
            self._photo_bg = RoundedRectangle(size=logo_box.size,
                                               pos=logo_box.pos, radius=[dp(14)])
        logo_box.bind(size=lambda *a: setattr(self._photo_bg, 'size', logo_box.size),
                      pos=lambda *a: setattr(self._photo_bg, 'pos', logo_box.pos))

        # Logo cenad.png
        logo_found = False
        for fname in ['cenad.png', 'cenad.PNG', 'logo.PNG', 'logo.png']:
            p = get_asset_path(fname)
            if os.path.exists(p):
                img = Image(source=p, allow_stretch=False, keep_ratio=True,
                            size_hint=(1, 1))
                logo_box.add_widget(img)
                logo_found = True
                break

        if not logo_found:
            logo_box.add_widget(Widget())
            logo_box.add_widget(Label(
                text="[b]CENA-D[/b]", markup=True,
                font_size=dp(38), color=(1, 0.85, 0.1, 1),
                size_hint_y=None, height=dp(55), halign='center'
            ))
            logo_box.add_widget(Widget())

        # Sous-titre sous le logo
        logo_box.add_widget(Label(
            text="COMMUNAUTE DES ETUDIANTS NATIFS D'ANDAPA - DIEGO",
            font_size=dp(10), color=(0.65, 0.80, 1, 0.9),
            size_hint_y=None, height=dp(22), halign='center',
            bold=True
        ))

        inner.add_widget(logo_box)

        # ── SOUS-TITRE ──
        inner.add_widget(Label(
            text="[i]Unis pour la reussite[/i]", markup=True,
            font_size=dp(12), color=(0.5, 0.8, 0.5, 1),
            size_hint_y=None, height=dp(24), halign='center'
        ))

        # ── LABEL MENU ──
        inner.add_widget(Label(
            text="MENU PRINCIPAL",
            font_size=dp(11), color=(0.45, 0.55, 0.80, 1),
            size_hint_y=None, height=dp(22), halign='left',
            bold=True
        ))

        # ── BOUTONS ICONES + TEXTE ──
        for i, (text, screen_name, bg_color) in enumerate(NAV_ITEMS):
            btn = IconTextButton(
                label_text=text,
                screen_name=screen_name,
                bg_color=bg_color,
                icon_file=ICON_FILES[i],
                icon_color=ICON_COLORS[i],
            )
            btn.bind(on_release=self._navigate)
            inner.add_widget(btn)

        # Footer
        inner.add_widget(Label(
            text="(c) CENAD 2024  |  Fondee en 2012",
            font_size=dp(10), color=(0.35, 0.45, 0.65, 0.8),
            size_hint_y=None, height=dp(32), halign='center'
        ))

        scroll.add_widget(inner)
        self.main_content.add_widget(scroll)
        self.root_layout.add_widget(self.main_content)

        # ── OVERLAY SOMBRE (clique pour fermer) ──
        self.overlay = Widget(size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        self.overlay.opacity = 0
        overlay_color = []
        with self.overlay.canvas:
            self._overlay_color = Color(0, 0, 0, 0)
            self._overlay_rect = Rectangle(size=self.overlay.size, pos=self.overlay.pos)
        self.overlay.bind(
            size=lambda *a: setattr(self._overlay_rect, 'size', self.overlay.size),
            pos=lambda *a: setattr(self._overlay_rect, 'pos', self.overlay.pos)
        )
        self.overlay.bind(on_touch_down=self._overlay_touch)
        self.root_layout.add_widget(self.overlay)

        # ── PANNEAU MENU LATERAL ──
        self.side_menu = SideMenuPanel(nav_items=NAV_ITEMS, icon_symbols=ICON_FILES,
                                       icon_colors=ICON_COLORS,
                                       navigate_cb=self._navigate_from_menu,
                                       close_cb=self._close_menu)
        # Départ hors écran à gauche
        self.side_menu.size_hint = (0.78, 1)
        self.side_menu.pos_hint = {'x': -0.78, 'y': 0}
        self.root_layout.add_widget(self.side_menu)

        self.add_widget(self.root_layout)

    def _toggle_menu(self, *args):
        if self._menu_open:
            self._close_menu()
        else:
            self._open_menu()

    def _open_menu(self):
        self._menu_open = True
        self.overlay.opacity = 1
        anim_overlay = Animation(a=0.55, duration=0.25)
        anim_overlay.start(self._overlay_color)
        anim = Animation(pos_hint={'x': 0, 'y': 0}, duration=0.25, t='out_cubic')
        anim.start(self.side_menu)

    def _close_menu(self, *args):
        self._menu_open = False
        anim_overlay = Animation(a=0, duration=0.2)
        anim_overlay.bind(on_complete=lambda *a: setattr(self.overlay, 'opacity', 0))
        anim_overlay.start(self._overlay_color)
        anim = Animation(pos_hint={'x': -0.78, 'y': 0}, duration=0.22, t='in_cubic')
        anim.start(self.side_menu)

    def _overlay_touch(self, widget, touch):
        if self._menu_open:
            self._close_menu()
            return True
        return False

    def _navigate(self, btn):
        self.manager.current = btn.screen_name

    def _navigate_from_menu(self, screen_name):
        self._close_menu()
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', screen_name), 0.25)

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos


# ── HAMBURGER BUTTON ──
class HamburgerButton(Button):
    def __init__(self, **kwargs):
        super().__init__(
            size_hint=(None, None),
            size=(dp(48), dp(44)),
            background_normal='',
            background_color=(0, 0, 0, 0),
            **kwargs
        )
        self._draw_lines()
        self.bind(pos=lambda *a: self._draw_lines(),
                  size=lambda *a: self._draw_lines())

    def _draw_lines(self):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(1, 1, 1, 0.95)
            cx = self.x + self.width / 2
            cy = self.y + self.height / 2
            w = dp(22)
            for offset in [-dp(7), 0, dp(7)]:
                Line(points=[cx - w/2, cy + offset, cx + w/2, cy + offset],
                     width=dp(1.8), cap='round')


# ── BOUTON ICONE + TEXTE ──
class IconTextButton(ButtonBehavior, BoxLayout):
    def __init__(self, label_text, screen_name, bg_color, icon_file, icon_color, **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(62),
            spacing=0,
            **kwargs
        )
        self.screen_name = screen_name
        self._bg_color = bg_color

        with self.canvas.before:
            self._color_inst = Color(*bg_color)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
        self.bind(size=lambda *a: setattr(self._rect, 'size', self.size),
                  pos=lambda *a: setattr(self._rect, 'pos', self.pos))

        # Bande icone à gauche
        icon_box = BoxLayout(size_hint=(None, 1), width=dp(56))
        with icon_box.canvas.before:
            Color(icon_color[0]*0.7, icon_color[1]*0.7, icon_color[2]*0.7, 0.6)
            self._icon_rect = RoundedRectangle(
                size=icon_box.size, pos=icon_box.pos,
                radius=[dp(10), 0, 0, dp(10)]
            )
        icon_box.bind(size=lambda *a: setattr(self._icon_rect, 'size', icon_box.size),
                      pos=lambda *a: setattr(self._icon_rect, 'pos', icon_box.pos))

        icon_path = get_asset_path('icons/' + icon_file)
        if os.path.exists(icon_path):
            icon_img = Image(source=icon_path, size_hint=(None, None),
                             size=(dp(36), dp(36)),
                             pos_hint={'center_x': 0.5, 'center_y': 0.5},
                             allow_stretch=True, keep_ratio=True)
            icon_box.add_widget(icon_img)
        else:
            icon_box.add_widget(Label(text=icon_file[3:4].upper(),
                                      font_size=dp(20), color=(1,1,1,1),
                                      halign='center'))
        self.add_widget(icon_box)

        # Texte
        text_lbl = Label(
            text=label_text, markup=True,
            font_size=dp(13), color=(1, 1, 1, 1),
            halign='left', valign='middle',
            padding_x=dp(14)
        )
        text_lbl.bind(size=lambda *a: setattr(text_lbl, 'text_size', text_lbl.size))
        self.add_widget(text_lbl)

        # Flèche droite
        self.add_widget(Label(
            text="  >", font_size=dp(18),
            color=(1, 1, 1, 0.5),
            size_hint=(None, 1), width=dp(32)
        ))

    def on_press(self):
        self._color_inst.a = 0.7

    def on_release(self):
        self._color_inst.a = 1.0


# ── PANNEAU LATERAL ──
class SideMenuPanel(BoxLayout):
    def __init__(self, nav_items, icon_symbols, icon_colors,
                 navigate_cb, close_cb, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.navigate_cb = navigate_cb

        with self.canvas.before:
            Color(0.04, 0.06, 0.20, 1)
            self._bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self._bg, 'size', self.size),
                  pos=lambda *a: setattr(self._bg, 'pos', self.pos))

        # Header menu
        header = BoxLayout(size_hint_y=None, height=dp(110),
                           orientation='vertical', padding=(dp(16), dp(16)))
        with header.canvas.before:
            Color(0.05, 0.07, 0.25, 1)
            self._h_bg = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda *a: setattr(self._h_bg, 'size', header.size),
                    pos=lambda *a: setattr(self._h_bg, 'pos', header.pos))

        close_btn = Button(
            text="X", size_hint=(None, None), size=(dp(36), dp(36)),
            background_normal='', background_color=(0.2, 0.25, 0.5, 1),
            color=(1, 1, 1, 1), font_size=dp(14), bold=True,
            pos_hint={'right': 1}
        )
        close_btn.bind(on_release=close_cb)
        header.add_widget(close_btn)
        header.add_widget(Label(
            text="[b]CENAD[/b]", markup=True,
            font_size=dp(22), color=(1, 0.85, 0.1, 1),
            halign='left', size_hint_y=None, height=dp(36)
        ))
        self.add_widget(header)

        # Séparateur
        sep = Widget(size_hint_y=None, height=dp(1))
        with sep.canvas:
            Color(0.25, 0.35, 0.65, 0.5)
            Rectangle(size=sep.size, pos=sep.pos)
        sep.bind(size=lambda *a: sep.canvas.clear() or
                 [Color(0.25, 0.35, 0.65, 0.5).__class__ and None,
                  Rectangle(size=sep.size, pos=sep.pos)])
        self.add_widget(sep)

        # Items de menu
        scroll = ScrollView()
        items_box = BoxLayout(orientation='vertical', size_hint_y=None,
                              spacing=dp(4), padding=(dp(8), dp(8)))
        items_box.bind(minimum_height=items_box.setter('height'))

        for i, (text, screen_name, bg_color) in enumerate(nav_items):
            item = SideMenuItem(
                text=text, screen_name=screen_name,
                icon_file=icon_symbols[i], icon_color=icon_colors[i],
                bg_color=bg_color,
                on_press_cb=navigate_cb
            )
            items_box.add_widget(item)

        scroll.add_widget(items_box)
        self.add_widget(scroll)

        # Footer
        footer = Label(
            text="v1.0.0  |  CENAD 2024",
            font_size=dp(10), color=(0.3, 0.4, 0.6, 0.7),
            size_hint_y=None, height=dp(36)
        )
        self.add_widget(footer)


class SideMenuItem(BoxLayout):
    def __init__(self, text, screen_name, icon_file, icon_color, bg_color, on_press_cb, **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None, height=dp(54),
            spacing=dp(0), **kwargs
        )
        self.screen_name = screen_name
        self.on_press_cb = on_press_cb

        with self.canvas.before:
            self._color = Color(bg_color[0], bg_color[1], bg_color[2], 0.0)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(8)])
        self.bind(size=lambda *a: setattr(self._rect, 'size', self.size),
                  pos=lambda *a: setattr(self._rect, 'pos', self.pos))

        # Barre colorée à gauche
        bar = Widget(size_hint=(None, 1), width=dp(4))
        with bar.canvas:
            Color(*icon_color)
            self._bar_rect = RoundedRectangle(size=bar.size, pos=bar.pos, radius=[dp(2)])
        bar.bind(size=lambda *a: setattr(self._bar_rect, 'size', bar.size),
                 pos=lambda *a: setattr(self._bar_rect, 'pos', bar.pos))
        self.add_widget(bar)

        # Icone
        icon_path = get_asset_path('icons/' + icon_file)
        if os.path.exists(icon_path):
            icon_wrap = BoxLayout(size_hint=(None, 1), width=dp(44))
            icon_wrap.add_widget(Image(
                source=icon_path,
                size_hint=(None, None), size=(dp(30), dp(30)),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                allow_stretch=True, keep_ratio=True
            ))
            self.add_widget(icon_wrap)
        else:
            self.add_widget(Label(text=icon_file[3:4].upper(),
                                   font_size=dp(16), color=list(icon_color[:3])+[1],
                                   size_hint=(None,1), width=dp(44)))

        # Texte
        lbl = Label(text=text, markup=True, font_size=dp(12),
                     color=(0.9, 0.93, 1, 1), halign='left', valign='middle')
        lbl.bind(size=lambda *a: setattr(lbl, 'text_size', lbl.size))
        self.add_widget(lbl)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._color.rgba = (0.2, 0.3, 0.7, 0.4)
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self._color.rgba = (0, 0, 0, 0)
        if self.collide_point(*touch.pos):
            self.on_press_cb(self.screen_name)
            return True
        return super().on_touch_up(touch)
