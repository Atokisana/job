"""
screens/etablissements.py - Établissements universitaires d'Antsiranana
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp


ETABLISSEMENTS = [
    {
        "nom": "ENSET",
        "complet": "École Normale Supérieure pour l'Enseignement Technique",
        "mission": "Former des enseignants techniques et des ingénieurs pédagogiques.",
        "mentions": ["Génie Civil", "Génie Électrique", "Génie Informatique", "Génie Mécanique"],
        "parcours": ["Licence", "Master"],
        "description": "L'ENSET est l'établissement phare pour la formation technique et pédagogique. Elle forme les futurs enseignants des lycées techniques ainsi que des ingénieurs.",
        "color": "#1565C0"
    },
    {
        "nom": "ESP",
        "complet": "École Supérieure Polytechnique",
        "mission": "Former des ingénieurs polytechniciens spécialisés.",
        "mentions": ["Génie Civil", "Génie Électrique", "Génie Informatique"],
        "parcours": ["Licence professionnelle", "Master Ingénierie"],
        "description": "L'ESP forme des ingénieurs capables de répondre aux besoins du secteur industriel et technologique de la région Nord de Madagascar.",
        "color": "#4527A0"
    },
    {
        "nom": "AGRO",
        "complet": "École Supérieure des Sciences Agronomiques",
        "mission": "Former des agronomes et spécialistes du développement rural.",
        "mentions": ["Agronomie", "Zootechnie", "Foresterie", "Aquaculture"],
        "parcours": ["Licence", "Master", "Doctorat"],
        "description": "L'ESSA-Antsiranana est dédiée à la formation agronomique adaptée aux spécificités de la région Nord, riche en ressources naturelles.",
        "color": "#2E7D32"
    },
    {
        "nom": "SCIENCES",
        "complet": "Faculté des Sciences",
        "mission": "Enseignement des sciences fondamentales et appliquées.",
        "mentions": ["Mathématiques", "Physique", "Chimie", "Biologie", "Informatique"],
        "parcours": ["Licence", "Master", "Doctorat"],
        "description": "La Faculté des Sciences dispense un enseignement rigoureux en sciences fondamentales, préparant les étudiants à la recherche et à l'enseignement.",
        "color": "#00695C"
    },
    {
        "nom": "FLSH",
        "complet": "Faculté des Lettres et Sciences Humaines",
        "mission": "Formation en lettres, langues, sciences sociales et humaines.",
        "mentions": ["Lettres Modernes", "Histoire-Géographie", "Anglais", "Sociologie"],
        "parcours": ["Licence", "Master", "Doctorat"],
        "description": "La FLSH est le pilier des sciences humaines à Antsiranana, valorisant les langues, l'histoire et la culture malgache.",
        "color": "#BF360C"
    },
    {
        "nom": "DEGSP",
        "complet": "Droit, Economie, Gestion et Science Politique",
        "mission": "Former des juristes, economistes, gestionnaires et politologues.",
        "mentions": ["Droit", "Economie", "Gestion", "Finance", "Sciences Politiques"],
        "parcours": ["Licence", "Master"],
        "description": "Le DEGSP répond aux besoins du secteur économique régional en formant des cadres compétents en gestion et en développement économique.",
        "color": "#F57F17"
    },
    {
        "nom": "ISAE",
        "complet": "Institut Superieur d'Administration et d'Entreprise",
        "mission": "Former des cadres en administration et gestion d'entreprise.",
        "mentions": ["Administration", "Gestion", "Management", "Commerce"],
        "parcours": ["Licence", "Master Administration"],
        "description": "L'ISAE forme des cadres competents en administration publique et en gestion d'entreprise pour repondre aux besoins du secteur economique regional.",
        "color": "#6A1B9A"
    },
    {
        "nom": "IST",
        "complet": "Institut Supérieur de Technologie",
        "mission": "Formation professionnelle en technologies appliquées.",
        "mentions": ["Informatique", "Réseaux", "Maintenance industrielle", "Électronique"],
        "parcours": ["BTS", "Licence Professionnelle"],
        "description": "L'IST offre une formation professionnalisante orientée vers l'insertion directe dans le monde du travail technique.",
        "color": "#006064"
    },
    {
        "nom": "ISISFA",
        "complet": "Institut Superieur de l'Infirmier et Sage Femme d'Antsiranana",
        "mission": "Former des infirmiers et sages-femmes qualifies pour la sante publique.",
        "mentions": ["Soins Infirmiers", "Sage-Femme", "Sante Publique"],
        "parcours": ["Licence en Soins Infirmiers", "Licence Sage-Femme"],
        "description": "L'ISISFA forme des professionnels de sante, notamment des infirmiers et sages-femmes, indispensables au systeme de sante de la region Nord de Madagascar.",
        "color": "#1565C0"
    },
]


class EtablissementsScreen(Screen):
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
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = Button(text="◀", size_hint=(None, 1), width=dp(40),
                          background_color=(0.2, 0.3, 0.7, 1), background_normal='')
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        header.add_widget(back_btn)
        header.add_widget(Label(text="[b]🏛 ÉTABLISSEMENTS UNIVERSITAIRES[/b]",
                                 markup=True, font_size=dp(13), color=(1, 0.85, 0.1, 1)))
        main.add_widget(header)

        subtitle = Label(
            text="Universités et instituts d'Antsiranana",
            font_size=dp(11), color=(0.6, 0.8, 1, 0.8),
            size_hint_y=None, height=dp(22)
        )
        main.add_widget(subtitle)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(10),
                             size_hint_y=None, padding=(0, dp(5)))
        content.bind(minimum_height=content.setter('height'))

        for etab in ETABLISSEMENTS:
            card = EtabCard(etab)
            content.add_widget(card)

        scroll.add_widget(content)
        main.add_widget(scroll)
        self.add_widget(main)


class EtabCard(BoxLayout):
    def __init__(self, etab, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None,
                         spacing=dp(2), **kwargs)
        color_hex = etab['color']
        r, g, b = [int(color_hex.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4)]

        # ── EN-TETE ──
        header = BoxLayout(orientation='vertical', size_hint_y=None,
                           padding=(dp(12), dp(8)), spacing=dp(2))
        with header.canvas.before:
            Color(r, g, b, 0.9)
            h_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda *a: setattr(h_rect, 'size', header.size),
                    pos=lambda *a: setattr(h_rect, 'pos', header.pos))

        nom_lbl = Label(
            text="[b]{}[/b]".format(etab['nom']), markup=True,
            font_size=dp(15), color=(1, 1, 1, 1),
            halign='left', valign='middle',
            size_hint_y=None, height=dp(26)
        )
        nom_lbl.bind(width=lambda *a: setattr(nom_lbl, 'text_size', (nom_lbl.width, None)))
        header.add_widget(nom_lbl)

        complet_lbl = Label(
            text=etab['complet'], font_size=dp(10),
            color=(0.85, 0.95, 1, 0.9),
            halign='left', valign='top',
            size_hint_y=None
        )
        complet_lbl.bind(
            width=lambda *a: setattr(complet_lbl, 'text_size', (complet_lbl.width, None)),
            texture_size=lambda *a: setattr(complet_lbl, 'height', complet_lbl.texture_size[1] + dp(4))
        )
        complet_lbl.height = dp(20)
        header.add_widget(complet_lbl)

        def _update_header(*a):
            header.height = nom_lbl.height + complet_lbl.height + dp(18)
        nom_lbl.bind(height=_update_header)
        complet_lbl.bind(height=_update_header)
        header.height = dp(58)

        self.add_widget(header)

        # ── CORPS ──
        body = BoxLayout(orientation='vertical', size_hint_y=None,
                         padding=(dp(12), dp(10)), spacing=dp(8))
        with body.canvas.before:
            Color(r * 0.3, g * 0.3, b * 0.3 + 0.1, 0.85)
            b_rect = Rectangle(size=body.size, pos=body.pos)
        body.bind(size=lambda *a: setattr(b_rect, 'size', body.size),
                  pos=lambda *a: setattr(b_rect, 'pos', body.pos))

        def make_row(prefix, text, text_color=(0.85, 0.9, 1, 0.9)):
            """Ligne avec label prefixe fixe + valeur hauteur auto."""
            row = BoxLayout(orientation='horizontal', size_hint_y=None,
                            spacing=dp(6), height=dp(20))

            prefix_lbl = Label(
                text="[b]{}[/b]".format(prefix), markup=True,
                font_size=dp(10), color=(1, 0.85, 0.4, 1),
                size_hint=(None, 1), width=dp(72),
                halign='left', valign='top'
            )
            prefix_lbl.bind(width=lambda *a: setattr(prefix_lbl, 'text_size', (dp(72), None)))

            val_lbl = Label(
                text=text, font_size=dp(11),
                color=text_color,
                halign='left', valign='top',
                size_hint=(1, None)
            )
            val_lbl.bind(
                width=lambda *a: setattr(val_lbl, 'text_size', (val_lbl.width, None)),
                texture_size=lambda *a: setattr(val_lbl, 'height', val_lbl.texture_size[1] + dp(2))
            )
            val_lbl.height = dp(18)

            def _sync_row(*a):
                row.height = max(val_lbl.height, dp(20))
            val_lbl.bind(height=_sync_row)

            row.add_widget(prefix_lbl)
            row.add_widget(val_lbl)
            body.add_widget(row)
            return row

        make_row("Mission :", etab['mission'], (1, 0.9, 0.6, 1))
        make_row("Details :", etab['description'])
        make_row("Mentions :", " - ".join(etab['mentions']))
        make_row("Parcours :", " | ".join(etab['parcours']), (0.7, 1, 0.7, 1))

        # Hauteur body : suit automatiquement ses enfants
        body.bind(minimum_height=body.setter('height'))
        body.height = dp(120)

        self.add_widget(body)

        # Hauteur carte totale auto
        def _update_card(*a):
            self.height = header.height + body.height + dp(6)
        header.bind(height=_update_card)
        body.bind(height=_update_card)
        self.height = dp(58) + dp(120) + dp(6)
