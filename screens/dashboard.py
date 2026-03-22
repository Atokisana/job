"""
screens/dashboard.py - Tableau de bord CENAD
Ameliorations : fiche membre, appel direct, recherche multi-criteres
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import platform
import threading
import os

import db_manager as db


def get_base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_downloads_dir():
    if platform == 'android':
        try:
            from android.storage import primary_external_storage_path
            return os.path.join(primary_external_storage_path(), 'Download')
        except Exception:
            return '/sdcard/Download'
    return os.path.expanduser('~/Downloads')

def open_phone(number):
    """Ouvre l'application Telephone du systeme."""
    number = number.strip().replace(' ', '')
    if platform == 'android':
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            intent = Intent(Intent.ACTION_DIAL)
            intent.setData(Uri.parse('tel:' + number))
            PythonActivity.mActivity.startActivity(intent)
        except Exception:
            try:
                import webbrowser
                webbrowser.open('tel:' + number)
            except Exception:
                pass
    else:
        try:
            import webbrowser
            webbrowser.open('tel:' + number)
        except Exception:
            pass


def open_sms(number):
    """Ouvre l'application SMS du systeme."""
    number = number.strip().replace(' ', '')
    if platform == 'android':
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            intent = Intent(Intent.ACTION_SENDTO)
            intent.setData(Uri.parse('smsto:' + number))
            PythonActivity.mActivity.startActivity(intent)
        except Exception:
            try:
                import webbrowser
                webbrowser.open('sms:' + number)
            except Exception:
                pass
    else:
        try:
            import webbrowser
            webbrowser.open('sms:' + number)
        except Exception:
            pass


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._search_event = None
        self.build_ui()

    def build_ui(self):
        with self.canvas.before:
            Color(0.05, 0.07, 0.22, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        main = BoxLayout(orientation='vertical', spacing=0)

        # TOPBAR
        topbar = BoxLayout(size_hint_y=None, height=dp(56), padding=(dp(8), dp(6)))
        with topbar.canvas.before:
            Color(0.04, 0.05, 0.18, 1)
            self._tb = Rectangle(size=topbar.size, pos=topbar.pos)
        topbar.bind(size=lambda *a: setattr(self._tb, 'size', topbar.size),
                    pos=lambda *a: setattr(self._tb, 'pos', topbar.pos))
        back_btn = Button(
            text="< Retour", size_hint=(None, 1), width=dp(80),
            background_color=(0.15, 0.25, 0.6, 1), background_normal='',
            font_size=dp(12), color=(1, 1, 1, 1)
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        topbar.add_widget(back_btn)
        topbar.add_widget(Label(
            text="[b]TABLEAU DE BORD[/b]", markup=True,
            font_size=dp(16), color=(1, 0.85, 0.1, 1)
        ))
        main.add_widget(topbar)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None,
                            padding=dp(10), spacing=dp(10))
        content.bind(minimum_height=content.setter('height'))

        # STATS
        self.stats_grid = GridLayout(cols=3, size_hint_y=None, height=dp(80), spacing=dp(6))
        self.stat_total = StatCard("Total", "0", "#1565C0")
        self.stat_m = StatCard("Hommes", "0", "#1B5E20")
        self.stat_f = StatCard("Femmes", "0", "#880E4F")
        self.stats_grid.add_widget(self.stat_total)
        self.stats_grid.add_widget(self.stat_m)
        self.stats_grid.add_widget(self.stat_f)
        content.add_widget(self.stats_grid)



        # BOUTON MISE A JOUR
        update_card = BoxLayout(orientation='vertical', size_hint_y=None,
                                height=dp(100), spacing=dp(6), padding=(dp(8), dp(8)))
        with update_card.canvas.before:
            Color(0.06, 0.10, 0.28, 1)
            self._uc = RoundedRectangle(size=update_card.size, pos=update_card.pos, radius=[dp(10)])
        update_card.bind(size=lambda *a: setattr(self._uc, 'size', update_card.size),
                         pos=lambda *a: setattr(self._uc, 'pos', update_card.pos))
        btn_update = Button(
            text="Mettre a jour la liste",
            size_hint_y=None, height=dp(50),
            background_color=(0.10, 0.50, 0.28, 1), background_normal='',
            font_size=dp(14), color=(1, 1, 1, 1), bold=True
        )
        btn_update.bind(on_release=self._show_update_options)
        update_card.add_widget(btn_update)
        self.import_status = Label(
            text="", font_size=dp(11), color=(0.5, 1, 0.5, 1),
            size_hint_y=None, height=dp(22), halign='center'
        )
        update_card.add_widget(self.import_status)
        content.add_widget(update_card)

        # GRAPHIQUES NATIFS KIVY
        content.add_widget(Label(
            text="[b]Statistiques[/b]", markup=True,
            font_size=dp(13), color=(0.7, 0.85, 1, 1),
            size_hint_y=None, height=dp(28), halign='left'
        ))
        chart_bar = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        for lbl, field in [("Niveau", "niveau"), ("Batiment", "batiment"), ("Promo", "promotion")]:
            btn = Button(text=lbl, background_color=(0.15, 0.28, 0.72, 1),
                         background_normal='', font_size=dp(12), color=(1, 1, 1, 1))
            btn.field = field
            btn.bind(on_release=self._show_chart)
            chart_bar.add_widget(btn)
        content.add_widget(chart_bar)
        self.chart_area = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(0), spacing=dp(4))
        content.add_widget(self.chart_area)

        # LISTE
        result_header = BoxLayout(size_hint_y=None, height=dp(30))
        result_header.add_widget(Label(
            text="[b]Liste des membres[/b]", markup=True,
            font_size=dp(13), color=(0.7, 0.85, 1, 1), halign='left'
        ))
        self.count_label = Label(text="", font_size=dp(11),
                                  color=(0.5, 0.7, 1, 0.8), halign='right')
        result_header.add_widget(self.count_label)
        content.add_widget(result_header)

        self.result_list = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None)
        self.result_list.bind(minimum_height=self.result_list.setter('height'))
        content.add_widget(self.result_list)

        scroll.add_widget(content)
        main.add_widget(scroll)
        self.add_widget(main)
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._search(), 0.5)

    def on_enter(self):
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._load_stats(), 0.2)
        Clock.schedule_once(lambda dt: self._search(), 0.3)



    def _search(self):
        results = db.search_membres()
        self._update_list(results)

    def _update_list(self, results):
        self.result_list.clear_widgets()
        self.count_label.text = "{} membre(s)".format(len(results))
        if not results:
            self.result_list.add_widget(Label(
                text="Aucun resultat", color=(0.5, 0.6, 0.8, 1),
                size_hint_y=None, height=dp(40), font_size=dp(13)
            ))
            return
        for m in results:
            self.result_list.add_widget(MemberRow(m, on_tap=self._show_member_profile))

    def _load_stats(self):
        def load():
            conn = db.get_connection()
            total = conn.execute("SELECT COUNT(*) FROM membres").fetchone()[0]
            hommes = conn.execute("SELECT COUNT(*) FROM membres WHERE sexe='M'").fetchone()[0]
            femmes = conn.execute("SELECT COUNT(*) FROM membres WHERE sexe='F'").fetchone()[0]
            conn.close()
            Clock.schedule_once(lambda dt: self._display_stats(total, hommes, femmes))
        threading.Thread(target=load, daemon=True).start()

    def _display_stats(self, total, hommes, femmes):
        self.stat_total.value_label.text = str(total)
        self.stat_m.value_label.text = str(hommes)
        self.stat_f.value_label.text = str(femmes)

    def _show_chart(self, btn):
        field = btn.field
        def generate():
            conn = db.get_connection()
            rows = conn.execute(
                "SELECT {}, COUNT(*) as total FROM membres GROUP BY {} ORDER BY total DESC LIMIT 10".format(field, field)
            ).fetchall()
            conn.close()
            data = [(dict(r)[field] or '?', dict(r)['total']) for r in rows]
            Clock.schedule_once(lambda dt: self._display_chart(data, field))
        threading.Thread(target=generate, daemon=True).start()

    def _display_chart(self, data, field):
        self.chart_area.clear_widgets()
        if not data:
            return
        titles = {'niveau': 'Par Niveau', 'batiment': 'Par Batiment', 'promotion': 'Par Promotion'}
        max_val = max(v for _, v in data) or 1
        total_h = dp(30) + len(data) * dp(32) + dp(10)
        self.chart_area.height = total_h

        # Titre
        self.chart_area.add_widget(Label(
            text="[b]{}[/b]".format(titles.get(field, field)), markup=True,
            font_size=dp(12), color=(1, 0.85, 0.1, 1),
            size_hint_y=None, height=dp(26)
        ))

        # Barres
        COLORS = [(0.2,0.5,1,1),(0.1,0.7,0.4,1),(0.7,0.3,0.9,1),(1,0.5,0.1,1),
                  (0.2,0.8,0.8,1),(0.9,0.3,0.3,1),(0.5,0.8,0.2,1),(0.9,0.6,0.1,1)]
        for i, (label, val) in enumerate(data):
            row = BoxLayout(size_hint_y=None, height=dp(28), spacing=dp(6))
            # Label
            row.add_widget(Label(
                text=str(label), font_size=dp(10), color=(0.8,0.9,1,1),
                size_hint=(None,1), width=dp(70), halign='right',
                text_size=(dp(68), None)
            ))
            # Barre
            bar_container = BoxLayout(size_hint=(1, 1))
            bar_w = (val / max_val)
            bar = BoxLayout(size_hint=(bar_w, 0.7), pos_hint={'center_y': 0.5})
            c = COLORS[i % len(COLORS)]
            with bar.canvas.before:
                Color(*c)
                bar._rect = RoundedRectangle(size=bar.size, pos=bar.pos, radius=[dp(3)])
            bar.bind(size=lambda w,*a: setattr(w._rect,'size',w.size),
                     pos=lambda w,*a: setattr(w._rect,'pos',w.pos))
            bar_container.add_widget(bar)
            row.add_widget(bar_container)
            # Valeur
            row.add_widget(Label(
                text=str(val), font_size=dp(10), color=(1,1,1,0.9),
                size_hint=(None,1), width=dp(28)
            ))
            self.chart_area.add_widget(row)

    # FICHE MEMBRE
    def _show_member_profile(self, membre):
        content = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))

        # Header photo + nom
        header = BoxLayout(size_hint_y=None, height=dp(100), spacing=dp(12))
        photo_path = membre.get('photo', '')
        if photo_path and os.path.exists(photo_path):
            header.add_widget(Image(
                source=photo_path, size_hint=(None, 1), width=dp(90),
                allow_stretch=True, keep_ratio=True
            ))
        else:
            sexe_color = (0.25, 0.6, 1, 1) if membre.get('sexe') == 'M' else (1, 0.45, 0.75, 1)
            init_box = BoxLayout(size_hint=(None, 1), width=dp(80))
            init_box.add_widget(Label(
                text="[b]{}[/b]".format(membre.get('nom', '?')[0].upper()),
                markup=True, font_size=dp(38), color=sexe_color,
                halign='center', valign='middle'
            ))
            header.add_widget(init_box)

        info_box = BoxLayout(orientation='vertical')
        info_box.add_widget(Label(
            text="[b]{}[/b]".format(membre.get('nom', '')), markup=True,
            font_size=dp(14), color=(1, 1, 1, 1), halign='left',
            text_size=(dp(185), None), size_hint_y=None, height=dp(26)
        ))
        sexe_txt = "Homme" if membre.get('sexe') == 'M' else "Femme"
        info_box.add_widget(Label(
            text="{} - {}".format(sexe_txt, membre.get('niveau', '')),
            font_size=dp(12), color=(0.7, 0.85, 1, 1), halign='left',
            text_size=(dp(185), None), size_hint_y=None, height=dp(20)
        ))
        info_box.add_widget(Label(
            text=membre.get('etablissement', ''),
            font_size=dp(12), color=(1, 0.85, 0.1, 1), halign='left',
            text_size=(dp(185), None), size_hint_y=None, height=dp(20)
        ))
        header.add_widget(info_box)
        content.add_widget(header)

        # Infos
        def row(label, value, color=(0.85, 0.9, 1, 0.9)):
            if not str(value).strip():
                return
            r = BoxLayout(size_hint_y=None, height=dp(26))
            r.add_widget(Label(text=label, font_size=dp(11), color=(0.5, 0.65, 1, 0.7),
                                size_hint=(None, 1), width=dp(95), halign='left',
                                text_size=(dp(95), None)))
            r.add_widget(Label(text=str(value), font_size=dp(12), color=color,
                                halign='left', text_size=(dp(160), None)))
            content.add_widget(r)

        row("Batiment", membre.get('batiment', ''))
        row("Promotion", membre.get('promotion', ''))
        row("Commune", membre.get('commune_origine', ''))
        row("Telephone", membre.get('telephone', ''), (0.4, 1, 0.65, 1))

        # Boutons appel/SMS
        telephone = str(membre.get('telephone', '')).strip()
        if telephone:
            btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
            btn_appel = Button(
                text="Appeler", background_color=(0.10, 0.55, 0.22, 1),
                background_normal='', font_size=dp(13), color=(1, 1, 1, 1)
            )
            btn_sms = Button(
                text="SMS", background_color=(0.18, 0.35, 0.75, 1),
                background_normal='', font_size=dp(13), color=(1, 1, 1, 1)
            )
            def do_call(*a):
                popup.dismiss()
                open_phone(telephone)
            def do_sms(*a):
                popup.dismiss()
                open_sms(telephone)
            btn_appel.bind(on_release=do_call)
            btn_sms.bind(on_release=do_sms)
            btn_row.add_widget(btn_appel)
            btn_row.add_widget(btn_sms)
            content.add_widget(btn_row)

        btn_close = Button(
            text="Fermer", size_hint_y=None, height=dp(42),
            background_color=(0.3, 0.15, 0.15, 1), background_normal='',
            font_size=dp(13), color=(1, 1, 1, 1)
        )
        content.add_widget(btn_close)

        popup = Popup(title=membre.get('nom', ''), content=content,
                      size_hint=(0.90, 0.70),
                      background_color=(0.06, 0.09, 0.28, 1))
        btn_close.bind(on_release=popup.dismiss)
        popup.open()

    # MISE A JOUR CSV
    def _show_update_options(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(
            text="Ou se trouve le fichier CSV ?",
            color=(0.85, 0.9, 1, 1), font_size=dp(14),
            halign='center', size_hint_y=None, height=dp(32)
        ))
        btn_dl = Button(text="Dossier Telechargements", size_hint_y=None, height=dp(50),
                        background_color=(0.10, 0.45, 0.72, 1), background_normal='',
                        font_size=dp(13), color=(1, 1, 1, 1))
        btn_br = Button(text="Choisir le fichier", size_hint_y=None, height=dp(50),
                        background_color=(0.28, 0.18, 0.65, 1), background_normal='',
                        font_size=dp(13), color=(1, 1, 1, 1))
        btn_ca = Button(text="Annuler", size_hint_y=None, height=dp(40),
                        background_color=(0.35, 0.15, 0.15, 1), background_normal='',
                        font_size=dp(12), color=(1, 1, 1, 1))
        popup = Popup(title="Mettre a jour", content=content,
                      size_hint=(0.88, 0.50),
                      background_color=(0.05, 0.08, 0.25, 1))
        def dl(*a):
            popup.dismiss()
            self._import_from_downloads()
        def br(*a):
            popup.dismiss()
            self._browse_csv()
        btn_dl.bind(on_release=dl)
        btn_br.bind(on_release=br)
        btn_ca.bind(on_release=popup.dismiss)
        content.add_widget(btn_dl)
        content.add_widget(btn_br)
        content.add_widget(btn_ca)
        popup.open()

    def _import_from_downloads(self, *args):
        downloads = get_downloads_dir()
        # Chercher ZIP en priorite
        zip_path = os.path.join(downloads, 'cenad_update.zip')
        if os.path.exists(zip_path):
            self._confirm_import(zip_path)
            return
        # Sinon CSV
        csv_path = os.path.join(downloads, 'cenad_membres.csv')
        if os.path.exists(csv_path):
            self._confirm_import(csv_path)
            return
        try:
            files = os.listdir(downloads)
            zips = [f for f in files if f.lower().endswith('.zip')]
            csvs = [f for f in files if f.lower().endswith('.csv')]
            if zips:
                self._confirm_import(os.path.join(downloads, zips[0]))
            elif csvs:
                self._confirm_import(os.path.join(downloads, csvs[0]))
            else:
                self.import_status.text = "Aucun fichier ZIP ou CSV trouve"
                self.import_status.color = (1, 0.4, 0.4, 1)
        except Exception:
            self.import_status.text = "Dossier Telechargements introuvable"
            self.import_status.color = (1, 0.4, 0.4, 1)

    def _browse_csv(self, *args):
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))
        start = get_downloads_dir()
        if not os.path.exists(start):
            start = os.path.expanduser('~')
        fc = FileChooserListView(filters=['*.csv', '*.CSV', '*.zip', '*.ZIP'], path=start)
        content.add_widget(fc)
        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        sel = Button(text="Selectionner", background_color=(0.10, 0.52, 0.10, 1),
                     background_normal='', color=(1, 1, 1, 1), font_size=dp(13))
        can = Button(text="Annuler", background_color=(0.45, 0.10, 0.10, 1),
                     background_normal='', color=(1, 1, 1, 1), font_size=dp(13))
        btn_row.add_widget(sel)
        btn_row.add_widget(can)
        content.add_widget(btn_row)
        fp = Popup(title="Choisir le fichier CSV ou ZIP", content=content,
                   size_hint=(0.95, 0.85),
                   background_color=(0.05, 0.08, 0.25, 1))
        def on_select(*a):
            if fc.selection:
                fp.dismiss()
                self._confirm_import(fc.selection[0])
        sel.bind(on_release=on_select)
        can.bind(on_release=fp.dismiss)
        fp.open()

    def _confirm_import(self, csv_path):
        try:
            if csv_path.lower().endswith('.zip'):
                import zipfile
                with zipfile.ZipFile(csv_path, 'r') as z:
                    names = z.namelist()
                csvs = [n for n in names if n.lower().endswith('.csv')]
                photos = [n for n in names if not n.lower().endswith('.csv') and not n.endswith('/')]
                lines = '?'
                if csvs:
                    import tempfile, csv as csv_mod
                    with zipfile.ZipFile(csv_path, 'r') as z:
                        with tempfile.TemporaryDirectory() as tmp:
                            z.extract(csvs[0], tmp)
                            with open(os.path.join(tmp, csvs[0]), 'r', encoding='utf-8') as f:
                                lines = max(0, sum(1 for _ in f) - 1)
                info = "{} membre(s), {} photo(s)".format(lines, len(photos))
            else:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    lines = max(0, sum(1 for _ in f) - 1)
                info = "{} membre(s)".format(lines)
        except Exception:
            info = '?'
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12))
        content.add_widget(Label(
            text="Fichier : {}\n{}\n\nCela remplacera la liste actuelle.".format(
                os.path.basename(csv_path), info),
            color=(1, 1, 1, 1), font_size=dp(13), halign='center'
        ))
        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        ok = Button(text="Mettre a jour", background_color=(0.10, 0.52, 0.10, 1),
                    background_normal='', color=(1, 1, 1, 1))
        ca = Button(text="Annuler", background_color=(0.45, 0.10, 0.10, 1),
                    background_normal='', color=(1, 1, 1, 1))
        btn_row.add_widget(ok)
        btn_row.add_widget(ca)
        content.add_widget(btn_row)
        popup = Popup(title="Confirmer", content=content,
                      size_hint=(0.85, 0.42),
                      background_color=(0.06, 0.10, 0.30, 1))
        def do(*a):
            popup.dismiss()
            self._do_import_csv(csv_path)
        ok.bind(on_release=do)
        ca.bind(on_release=popup.dismiss)
        popup.open()

    def _do_import_csv(self, file_path):
        self.import_status.text = "Import en cours..."
        self.import_status.color = (1, 0.85, 0.1, 1)
        def do():
            try:
                if file_path.lower().endswith('.zip'):
                    count = db.import_from_zip(file_path)
                else:
                    count = db.import_from_csv(file_path)
                Clock.schedule_once(lambda dt: self._on_import_done(count))
            except Exception as e:
                err_msg = str(e)
                Clock.schedule_once(lambda dt, msg=err_msg: self._on_import_error(msg))
        threading.Thread(target=do, daemon=True).start()

    def _on_import_done(self, count):
        self.import_status.text = "{} membre(s) importes !".format(count)
        self.import_status.color = (0.4, 1, 0.4, 1)
        self._load_stats()
        self._search()

    def _on_import_error(self, err):
        self.import_status.text = "Erreur : {}".format(err[:50])
        self.import_status.color = (1, 0.4, 0.4, 1)

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos


class StatCard(BoxLayout):
    def __init__(self, label, value, color_hex, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        r, g, b = [int(color_hex.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4)]
        with self.canvas.before:
            Color(r, g, b, 0.85)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(8)])
        self.bind(size=lambda *a: setattr(self._rect, 'size', self.size),
                  pos=lambda *a: setattr(self._rect, 'pos', self.pos))
        self.add_widget(Label(text=label, font_size=dp(10), color=(0.8, 0.9, 1, 0.9),
                               size_hint_y=0.4, bold=True))
        self.value_label = Label(text=value, font_size=dp(22), bold=True,
                                  color=(1, 1, 1, 1), size_hint_y=0.6)
        self.add_widget(self.value_label)


class MemberRow(BoxLayout):
    def __init__(self, membre, on_tap=None, **kwargs):
        super().__init__(size_hint_y=None, height=dp(56), spacing=dp(6),
                         padding=(dp(8), dp(4)), **kwargs)
        self.membre = membre
        self.on_tap = on_tap
        self._pressed = False

        with self.canvas.before:
            Color(0.10, 0.14, 0.40, 0.75)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(8)])
        self.bind(size=lambda *a: setattr(self._rect, 'size', self.size),
                  pos=lambda *a: setattr(self._rect, 'pos', self.pos))

        photo_path = membre.get('photo', '')
        avatar_box = BoxLayout(size_hint=(None, 1), width=dp(44))
        if photo_path and os.path.exists(photo_path):
            avatar_box.add_widget(Image(
                source=photo_path, allow_stretch=True, keep_ratio=True,
                size_hint=(None, None), size=(dp(40), dp(40)),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            ))
        else:
            sexe_color = (0.3, 0.65, 1, 1) if membre.get('sexe') == 'M' else (1, 0.45, 0.75, 1)
            avatar_box.add_widget(Label(
                text="[b]{}[/b]".format(membre.get('nom', '?')[0].upper()),
                markup=True, font_size=dp(18), color=sexe_color,
                halign='center', valign='middle'
            ))
        self.add_widget(avatar_box)

        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(
            text=membre.get('nom', ''), font_size=dp(13), bold=True,
            color=(1, 1, 1, 1), halign='left', text_size=(dp(165), None)
        ))
        info.add_widget(Label(
            text="{} | {}".format(membre.get('etablissement', ''), membre.get('batiment', '')),
            font_size=dp(10), color=(0.6, 0.8, 1, 0.8),
            halign='left', text_size=(dp(165), None)
        ))
        self.add_widget(info)

        badge = Label(
            text="[b]{}[/b]".format(membre.get('niveau', '')), markup=True,
            size_hint=(None, None), size=(dp(36), dp(22)),
            font_size=dp(11), color=(0.05, 0.05, 0.15, 1),
            halign='center', valign='middle', pos_hint={'center_y': 0.5}
        )
        with badge.canvas.before:
            Color(1, 0.85, 0.1, 1)
            self._br = RoundedRectangle(size=badge.size, pos=badge.pos, radius=[dp(4)])
        badge.bind(size=lambda *a: setattr(self._br, 'size', badge.size),
                   pos=lambda *a: setattr(self._br, 'pos', badge.pos))
        self.add_widget(badge)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._pressed = True
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._pressed:
            self._pressed = False
            if self.collide_point(*touch.pos) and self.on_tap:
                membre_complet = db.get_membre_by_id(self.membre['id'])
                if membre_complet:
                    self.on_tap(membre_complet)
            return True
        return super().on_touch_up(touch)
