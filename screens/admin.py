"""
screens/admin.py - Administration avec export CSV + photos zip
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
from kivy.uix.filechooser import FileChooserIconView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp
import os
import shutil
import zipfile
import threading
import db_manager as db


def make_bg(widget, r, g, b, a=1):
    with widget.canvas.before:
        Color(r, g, b, a)
        rect = Rectangle(size=widget.size, pos=widget.pos)
    widget.bind(size=lambda *x: setattr(rect, 'size', widget.size),
                pos=lambda *x: setattr(rect, 'pos', widget.pos))
    return rect


def get_photos_dir():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    photos = os.path.join(base, 'data', 'photos')
    os.makedirs(photos, exist_ok=True)
    return photos


def get_data_dir():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, 'data')


class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.authenticated = False
        self._built = False

    def on_enter(self):
        if not self._built:
            self._build_login()
            self._built = True

    def _build_login(self):
        make_bg(self, 0.04, 0.06, 0.20, 1)
        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(16))
        layout.add_widget(Label(
            text="[b]ADMINISTRATION[/b]", markup=True,
            font_size=dp(22), color=(1, 0.85, 0.1, 1),
            size_hint_y=None, height=dp(50)
        ))
        layout.add_widget(Label(
            text="Mot de passe requis", font_size=dp(14),
            color=(0.6, 0.75, 1, 1), size_hint_y=None, height=dp(28)
        ))
        self.pwd_input = TextInput(
            hint_text="Entrez le mot de passe...",
            password=True, multiline=False, write_tab=False,
            size_hint_y=None, height=dp(50),
            background_color=(0.12, 0.17, 0.42, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.6, 0.8, 1),
            cursor_color=(1, 1, 1, 1), font_size=dp(15)
        )
        layout.add_widget(self.pwd_input)
        login_btn = Button(
            text="Se connecter", size_hint_y=None, height=dp(52),
            background_color=(0.10, 0.52, 0.10, 1), background_normal='',
            font_size=dp(15), color=(1, 1, 1, 1)
        )
        login_btn.bind(on_release=self._check_password)
        layout.add_widget(login_btn)
        back_btn = Button(
            text="< Retour", size_hint_y=None, height=dp(44),
            background_color=(0.25, 0.25, 0.45, 1), background_normal='',
            font_size=dp(13), color=(1, 1, 1, 1)
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        layout.add_widget(back_btn)
        self.error_label = Label(
            text="", color=(1, 0.3, 0.3, 1),
            size_hint_y=None, height=dp(30), font_size=dp(13)
        )
        layout.add_widget(self.error_label)
        layout.add_widget(Label())
        self.add_widget(layout)

    def _check_password(self, *args):
        if db.verify_admin_password(self.pwd_input.text):
            self.authenticated = True
            self.clear_widgets()
            self._build_admin_panel()
        else:
            self.error_label.text = "Mot de passe incorrect"
            self.pwd_input.text = ""

    def _build_admin_panel(self):
        make_bg(self, 0.04, 0.06, 0.20, 1)
        main = BoxLayout(orientation='vertical', padding=(dp(8), dp(6)), spacing=dp(6))

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        with header.canvas.before:
            Color(0.03, 0.05, 0.18, 1)
            h_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda *a: setattr(h_rect, 'size', header.size),
                    pos=lambda *a: setattr(h_rect, 'pos', header.pos))

        back_btn = Button(
            text="<", size_hint=(None, 1), width=dp(44),
            background_color=(0.18, 0.28, 0.65, 1), background_normal='',
            color=(1, 1, 1, 1), font_size=dp(16), bold=True
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        header.add_widget(back_btn)
        header.add_widget(Label(
            text="[b]ADMINISTRATION[/b]", markup=True,
            font_size=dp(15), color=(1, 0.85, 0.1, 1)
        ))
        add_btn = Button(
            text="+ Ajouter", size_hint=(None, 1), width=dp(100),
            background_color=(0.10, 0.52, 0.10, 1), background_normal='',
            font_size=dp(13), color=(1, 1, 1, 1)
        )
        add_btn.bind(on_release=lambda x: self._open_form())
        header.add_widget(add_btn)
        main.add_widget(header)

        # Boutons export
        export_box = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        btn_csv = Button(
            text="Exporter CSV", size_hint=(0.5, 1),
            background_color=(0.05, 0.48, 0.28, 1), background_normal='',
            font_size=dp(12), color=(1, 1, 1, 1)
        )
        btn_csv.bind(on_release=self._export_csv)

        btn_zip = Button(
            text="Exporter CSV + Photos",
            size_hint=(0.5, 1),
            background_color=(0.48, 0.28, 0.05, 1), background_normal='',
            font_size=dp(12), color=(1, 1, 1, 1)
        )
        btn_zip.bind(on_release=self._export_zip)
        export_box.add_widget(btn_csv)
        export_box.add_widget(btn_zip)
        main.add_widget(export_box)

        self.export_status = Label(
            text="", font_size=dp(11), color=(0.5, 1, 0.5, 1),
            size_hint_y=None, height=dp(22), halign='center'
        )
        main.add_widget(self.export_status)

        # Compteur
        self.count_lbl = Label(
            text="", font_size=dp(11), color=(0.5, 0.7, 1, 0.8),
            size_hint_y=None, height=dp(20), halign='right'
        )
        main.add_widget(self.count_lbl)

        scroll = ScrollView()
        self.member_list = BoxLayout(
            orientation='vertical', spacing=dp(5),
            size_hint_y=None, padding=(0, dp(4))
        )
        self.member_list.bind(minimum_height=self.member_list.setter('height'))
        scroll.add_widget(self.member_list)
        main.add_widget(scroll)
        self.add_widget(main)
        self._load_list()

    def _export_csv(self, *args):
        def do():
            try:
                path = db.export_csv()
                Clock.schedule_once(lambda dt: setattr(
                    self.export_status, 'text',
                    "CSV sauvegarde : data/cenad_membres.csv"
                ))
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(
                    self.export_status, 'text', "Erreur: {}".format(str(e)[:40])
                ))
        threading.Thread(target=do, daemon=True).start()
        self.export_status.text = "Export CSV en cours..."

    def _export_zip(self, *args):
        """Exporte CSV + photos renommees avec nom du membre dans un zip."""
        def do():
            try:
                # Exporter CSV
                csv_path = db.export_csv()
                zip_path = os.path.join(get_data_dir(), 'cenad_update.zip')
                photos_dir = get_photos_dir()

                # Charger tous les membres pour relier photo -> nom
                membres = db.get_all_membres(limit=1000)
                # Construire un dict photo_path -> nom_fichier_propre
                photo_map = {}
                for m in membres:
                    photo = m.get('photo', '').strip()
                    nom = m.get('nom', '').strip()
                    if photo and os.path.exists(photo) and nom:
                        # Nom de fichier propre: NOM_PRENOM.jpg
                        ext = os.path.splitext(photo)[1].lower() or '.jpg'
                        safe_name = nom.replace(' ', '_').replace('/', '_') + ext
                        photo_map[photo] = safe_name

                # Mettre a jour le CSV avec les nouveaux noms de photos
                import csv as csv_mod
                rows = []
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv_mod.DictReader(f)
                    fieldnames = reader.fieldnames
                    for row in reader:
                        photo_src = row.get('photo', '').strip()
                        if photo_src in photo_map:
                            row['photo'] = 'photos/' + photo_map[photo_src]
                        rows.append(row)

                # Réécrire le CSV avec les nouveaux chemins
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv_mod.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)

                # Créer le ZIP
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.write(csv_path, 'cenad_membres.csv')
                    for photo_src, safe_name in photo_map.items():
                        zf.write(photo_src, os.path.join('photos', safe_name))

                nb_photos = len(photo_map)
                Clock.schedule_once(lambda dt: setattr(
                    self.export_status, 'text',
                    "ZIP OK : CSV + {} photo(s)".format(nb_photos)
                ))
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(
                    self.export_status, 'text', "Erreur: {}".format(str(e)[:40])
                ))
        threading.Thread(target=do, daemon=True).start()
        self.export_status.text = "Creation ZIP en cours..."

    def _load_list(self):
        self.member_list.clear_widgets()
        membres = db.get_all_membres()
        self.count_lbl.text = "{} membre(s)".format(len(membres))
        for m in membres:
            row = AdminMemberRow(m, self._edit_membre, self._delete_membre)
            self.member_list.add_widget(row)

    def _open_form(self, membre=None):
        popup = MemberFormPopup(membre, on_save=self._on_save)
        popup.open()

    def _edit_membre(self, membre_id):
        self._open_form(db.get_membre_by_id(membre_id))

    def _delete_membre(self, membre_id, nom):
        def confirm(*a):
            db.delete_membre(membre_id)
            self._load_list()
            popup.dismiss()

        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(
            text="Supprimer [b]{}[/b] ?".format(nom), markup=True,
            color=(1, 1, 1, 1), font_size=dp(14)
        ))
        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cb = Button(text="Supprimer", background_color=(0.75, 0.1, 0.1, 1),
                    background_normal='', color=(1, 1, 1, 1))
        ca = Button(text="Annuler", background_color=(0.3, 0.3, 0.5, 1),
                    background_normal='', color=(1, 1, 1, 1))
        cb.bind(on_release=confirm)
        ca.bind(on_release=lambda x: popup.dismiss())
        btns.add_widget(cb)
        btns.add_widget(ca)
        content.add_widget(btns)
        popup = Popup(title="Confirmation", content=content,
                      size_hint=(0.85, 0.32),
                      background_color=(0.08, 0.12, 0.38, 1))
        popup.open()

    def _on_save(self, data, membre_id=None):
        if membre_id:
            db.update_membre(membre_id, data)
        else:
            db.add_membre(data)
        self._load_list()


class AdminMemberRow(BoxLayout):
    def __init__(self, membre, edit_cb, delete_cb, **kwargs):
        super().__init__(
            size_hint_y=None, height=dp(58), spacing=dp(6),
            padding=(dp(6), dp(4)), **kwargs
        )
        with self.canvas.before:
            Color(0.09, 0.13, 0.38, 0.7)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(8)])
        self.bind(size=lambda *a: setattr(self._rect, 'size', self.size),
                  pos=lambda *a: setattr(self._rect, 'pos', self.pos))

        photo_path = membre.get('photo', '')
        avatar = BoxLayout(size_hint=(None, 1), width=dp(44))
        if photo_path and os.path.exists(photo_path):
            avatar.add_widget(Image(
                source=photo_path, allow_stretch=True, keep_ratio=True,
                size_hint=(None, None), size=(dp(40), dp(40)),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            ))
        else:
            sexe_color = (0.3, 0.65, 1, 1) if membre.get('sexe') == 'M' else (1, 0.45, 0.7, 1)
            avatar.add_widget(Label(
                text="[b]{}[/b]".format(membre.get('nom', '?')[0].upper()),
                markup=True, font_size=dp(18), color=sexe_color,
                halign='center', valign='middle'
            ))
        self.add_widget(avatar)

        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(
            text=membre['nom'], font_size=dp(13), bold=True,
            color=(1, 1, 1, 1), halign='left', text_size=(dp(150), None)
        ))
        info.add_widget(Label(
            text="{} | {} | {}".format(
                membre.get('niveau', ''), membre.get('batiment', ''),
                membre.get('etablissement', '')
            ),
            font_size=dp(10), color=(0.6, 0.8, 1, 0.8),
            halign='left', text_size=(dp(150), None)
        ))
        self.add_widget(info)

        edit_btn = Button(
            text="Edit", size_hint=(None, 1), width=dp(46),
            background_color=(0.15, 0.45, 0.85, 1), background_normal='',
            font_size=dp(12), color=(1, 1, 1, 1)
        )
        edit_btn.bind(on_release=lambda x: edit_cb(membre['id']))

        del_btn = Button(
            text="Supp", size_hint=(None, 1), width=dp(46),
            background_color=(0.72, 0.1, 0.1, 1), background_normal='',
            font_size=dp(12), color=(1, 1, 1, 1)
        )
        del_btn.bind(on_release=lambda x: delete_cb(membre['id'], membre['nom']))

        self.add_widget(edit_btn)
        self.add_widget(del_btn)


class MemberFormPopup(Popup):
    NIVEAUX = ["L1", "L2", "L3", "M1", "M2"]
    BATIMENTS = ["BLOC A", "BLOC B", "BLOC C", "BLOC D", "BLOC E",
                 "BLOC F", "BLOC G", "BLOC H", "BLOC I",
                 "PJ A", "PJ B", "PJ C", "PV B", "PV C", "Belle rose", "Autre"]
    ETABLISSEMENTS = ["ENSET", "ESP", "AGRO", "SCIENCES", "FLSH",
                      "DEGSP", "ISAE", "IST", "ISISFA", "Autre"]

    def __init__(self, membre=None, on_save=None, **kwargs):
        self.membre = membre
        self.on_save_cb = on_save
        self.selected_photo = membre.get('photo', '') if membre else ''
        content = self._build_form()
        super().__init__(
            title="Modifier" if membre else "Ajouter un membre",
            content=content,
            size_hint=(0.95, 0.92),
            background_color=(0.05, 0.08, 0.25, 1),
            **kwargs
        )

    def _build_form(self):
        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing=dp(8), padding=dp(10), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        m = self.membre or {}

        def field(hint, key):
            return TextInput(
                hint_text=hint, text=str(m.get(key, '')),
                multiline=False, size_hint_y=None, height=dp(46),
                background_color=(0.12, 0.17, 0.42, 1),
                foreground_color=(1, 1, 1, 1),
                hint_text_color=(0.5, 0.6, 0.8, 1),
                cursor_color=(1, 1, 1, 1), font_size=dp(13), write_tab=False,
            )

        def lbl(text):
            return Label(text=text, color=(0.65, 0.82, 1, 1),
                         size_hint_y=None, height=dp(22), halign='left', font_size=dp(12))

        def spn(vals, key, default):
            return Spinner(text=m.get(key, default), values=vals,
                           size_hint_y=None, height=dp(46),
                           background_color=(0.18, 0.28, 0.65, 1), color=(1, 1, 1, 1))

        self.nom_input = field("Nom complet *", 'nom')
        self.telephone_input = field("Telephone", 'telephone')
        self.commune_input = field("Commune d'origine", 'commune_origine')
        self.promotion_input = field("Promotion (ex: 2022)", 'promotion')
        self.sexe_spinner = spn(['M', 'F'], 'sexe', 'M')
        self.niveau_spinner = spn(self.NIVEAUX, 'niveau', 'L1')
        self.batiment_spinner = spn(self.BATIMENTS, 'batiment', 'BLOC A')
        self.etab_spinner = spn(self.ETABLISSEMENTS, 'etablissement', 'ENSET')

        # Photo
        self.photo_preview = Image(
            source=self.selected_photo if self.selected_photo and os.path.exists(self.selected_photo) else '',
            size_hint=(None, None), size=(dp(80), dp(80)),
            pos_hint={'center_x': 0.5}, allow_stretch=True, keep_ratio=True
        )
        choose_btn = Button(
            text="Choisir une photo", size_hint_y=None, height=dp(40),
            background_color=(0.25, 0.45, 0.85, 1), background_normal='',
            color=(1, 1, 1, 1), font_size=dp(12)
        )
        choose_btn.bind(on_release=self._open_file_chooser)

        photo_box = BoxLayout(orientation='vertical', size_hint_y=None,
                              height=dp(130), spacing=dp(6))
        photo_box.add_widget(self.photo_preview)
        photo_box.add_widget(choose_btn)

        for w in [
            lbl("Nom complet *"), self.nom_input,
            lbl("Sexe"), self.sexe_spinner,
            lbl("Niveau"), self.niveau_spinner,
            lbl("Promotion"), self.promotion_input,
            lbl("Batiment"), self.batiment_spinner,
            lbl("Etablissement"), self.etab_spinner,
            lbl("Telephone"), self.telephone_input,
            lbl("Commune d'origine"), self.commune_input,
            lbl("Photo de profil"), photo_box,
        ]:
            layout.add_widget(w)

        btns = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        save_btn = Button(
            text="Enregistrer",
            background_color=(0.10, 0.52, 0.10, 1), background_normal='',
            color=(1, 1, 1, 1), font_size=dp(14)
        )
        cancel_btn = Button(
            text="Annuler",
            background_color=(0.45, 0.10, 0.10, 1), background_normal='',
            color=(1, 1, 1, 1), font_size=dp(14)
        )
        save_btn.bind(on_release=self._save)
        cancel_btn.bind(on_release=self.dismiss)
        btns.add_widget(save_btn)
        btns.add_widget(cancel_btn)
        layout.add_widget(btns)

        scroll.add_widget(layout)
        return scroll

    def _open_file_chooser(self, *args):
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))
        fc = FileChooserIconView(
            filters=['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG'],
            path=os.path.expanduser('~')
        )
        content.add_widget(fc)
        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        sel = Button(text="Selectionner", background_color=(0.10, 0.52, 0.10, 1),
                     background_normal='', color=(1, 1, 1, 1))
        can = Button(text="Annuler", background_color=(0.45, 0.10, 0.10, 1),
                     background_normal='', color=(1, 1, 1, 1))
        btn_row.add_widget(sel)
        btn_row.add_widget(can)
        content.add_widget(btn_row)

        fp = Popup(title="Choisir une photo", content=content,
                   size_hint=(0.95, 0.85),
                   background_color=(0.05, 0.08, 0.25, 1))

        def on_select(*a):
            if fc.selection:
                src = fc.selection[0]
                dst = os.path.join(get_photos_dir(), os.path.basename(src))
                shutil.copy2(src, dst)
                self.selected_photo = dst
                self.photo_preview.source = dst
                self.photo_preview.reload()
            fp.dismiss()

        sel.bind(on_release=on_select)
        can.bind(on_release=fp.dismiss)
        fp.open()

    def _save(self, *args):
        nom = self.nom_input.text.strip()
        if not nom:
            return
        data = {
            'nom': nom,
            'sexe': self.sexe_spinner.text,
            'niveau': self.niveau_spinner.text,
            'promotion': self.promotion_input.text.strip(),
            'batiment': self.batiment_spinner.text,
            'etablissement': self.etab_spinner.text,
            'commune_origine': self.commune_input.text.strip(),
            'telephone': self.telephone_input.text.strip(),
            'photo': self.selected_photo
        }
        if self.on_save_cb:
            self.on_save_cb(data, self.membre['id'] if self.membre else None)
        self.dismiss()
