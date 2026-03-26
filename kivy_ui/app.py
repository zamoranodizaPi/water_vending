"""Modern KivyMD user interface for the water vending machine."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import FadeTransition, ScreenManager, SlideTransition, SwapTransition
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

from config import settings
from qml_ui.palettes import THEMES, palette_for


def hex_to_rgba(value: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    cleaned = value.lstrip("#")
    return (
        int(cleaned[0:2], 16) / 255.0,
        int(cleaned[2:4], 16) / 255.0,
        int(cleaned[4:6], 16) / 255.0,
        alpha,
    )


def mix_hex(left: str, right: str, factor: float) -> str:
    l = left.lstrip("#")
    r = right.lstrip("#")
    rv = []
    for index in (0, 2, 4):
        lv = int(l[index:index + 2], 16)
        rvv = int(r[index:index + 2], 16)
        rv.append(int(lv + (rvv - lv) * factor))
    return "#{:02X}{:02X}{:02X}".format(*rv)


def gradient_texture(colors: list[str]) -> Texture:
    width = 64
    texture = Texture.create(size=(1, width), colorfmt="rgba")
    buf = bytearray()
    segments = len(colors) - 1
    for y in range(width):
        pos = y / max(1, width - 1)
        left_index = min(int(pos * segments), segments - 1)
        right_index = left_index + 1
        local_span = 1 / segments
        local_pos = 0 if local_span == 0 else (pos - left_index * local_span) / local_span
        color = mix_hex(colors[left_index], colors[right_index], local_pos)
        red, green, blue, alpha = hex_to_rgba(color)
        buf.extend(
            [
                int(red * 255),
                int(green * 255),
                int(blue * 255),
                int(alpha * 255),
            ]
        )
    texture.blit_buffer(bytes(buf), colorfmt="rgba", bufferfmt="ubyte")
    texture.wrap = "repeat"
    texture.uvsize = (1, -1)
    return texture


class AnimatedGradientBackground(Widget):
    colors = ListProperty()
    overlay = ListProperty([1, 1, 1, 0.08])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._base_colors = list(self.colors or ["#0f172a", "#1e293b", "#334155"])
        self._target_colors = list(self._base_colors)
        with self.canvas:
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(1, 1, 1, 0.12)
            self._glow_a = Ellipse(size=(dp(340), dp(340)), pos=(-dp(40), self.height - dp(260)))
            Color(1, 1, 1, 0.08)
            self._glow_b = Ellipse(size=(dp(260), dp(260)), pos=(self.width - dp(220), -dp(40)))
        self.bind(pos=self._update_canvas, size=self._update_canvas, colors=self._on_colors)
        Clock.schedule_once(lambda *_: self._on_colors(), 0)
        self._pulse = Animation(opacity=0.92, duration=4.0) + Animation(opacity=1.0, duration=4.0)
        self._pulse.repeat = True
        self._pulse.start(self)

    def _on_colors(self, *_args):
        self._target_colors = list(self.colors or self._target_colors)
        self._bg.texture = gradient_texture(self._target_colors)
        self._bg.tex_coords = (0, 0, 1, 0, 1, 1, 0, 1)
        self._update_canvas()

    def _update_canvas(self, *_args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._glow_a.pos = (-dp(40), self.y + self.height - dp(260))
        self._glow_b.pos = (self.x + self.width - dp(220), self.y - dp(40))


class ShadowCard(MDCard):
    shadow_color = ListProperty([0.04, 0.08, 0.16, 0.22])
    shadow_offset = NumericProperty(dp(8))
    radius_value = NumericProperty(dp(28))
    bg_color = ListProperty([1, 1, 1, 0.18])
    border_color = ListProperty([1, 1, 1, 0.22])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (0, 0, 0, 0)
        self.radius = [self.radius_value] * 4
        self.elevation = 0
        self.padding = dp(16)
        self.bind(pos=self._redraw, size=self._redraw, bg_color=self._redraw, border_color=self._redraw, shadow_color=self._redraw, radius_value=self._redraw)
        with self.canvas.before:
            self._shadow_color = Color(*self.shadow_color)
            self._shadow = RoundedRectangle()
            self._panel_color = Color(*self.bg_color)
            self._panel = RoundedRectangle()
            self._line_color = Color(*self.border_color)
            self._border = RoundedRectangle()
        Clock.schedule_once(lambda *_: self._redraw(), 0)

    def _redraw(self, *_args):
        self.radius = [self.radius_value] * 4
        self._shadow_color.rgba = self.shadow_color
        self._shadow.pos = (self.x, self.y - self.shadow_offset)
        self._shadow.size = self.size
        self._shadow.radius = self.radius
        self._panel_color.rgba = self.bg_color
        self._panel.pos = self.pos
        self._panel.size = self.size
        self._panel.radius = self.radius
        self._line_color.rgba = self.border_color
        self._border.pos = (self.x + 1, self.y + 1)
        self._border.size = (max(0, self.width - 2), max(0, self.height - 2))
        self._border.radius = [max(0, r - 1) for r in self.radius]


class ModernButton(ButtonBehavior, ShadowCard):
    text = StringProperty("")
    icon_text = StringProperty("")
    text_color = ListProperty([1, 1, 1, 1])
    base_color = ListProperty([0.2, 0.4, 0.9, 1.0])
    hover_color = ListProperty([0.25, 0.5, 1.0, 1.0])
    pressed_color = ListProperty([0.14, 0.28, 0.65, 1.0])
    use_hover = BooleanProperty(True)

    def __init__(self, **kwargs):
        self.register_event_type("on_release")
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(54)
        self.shadow_offset = dp(7)
        self.radius_value = dp(20)
        self._hovered = False
        self.bg_color = self.base_color
        self.border_color = [1, 1, 1, 0.18]

        content = MDBoxLayout(orientation="horizontal", spacing=dp(10), padding=(dp(18), 0, dp(18), 0))
        self._icon = MDLabel(text=self.icon_text, halign="center", valign="middle", size_hint=(None, 1), width=dp(24), font_style="H6", theme_text_color="Custom", text_color=self.text_color)
        self._label = MDLabel(text=self.text, halign="center", valign="middle", theme_text_color="Custom", text_color=self.text_color, bold=True)
        content.add_widget(self._icon)
        content.add_widget(self._label)
        self.add_widget(content)

        Window.bind(mouse_pos=self._on_mouse_pos)
        self.bind(text=self._sync_text, icon_text=self._sync_text, text_color=self._sync_text, base_color=self._sync_colors)
        self._sync_text()
        self._sync_colors()

    def _sync_text(self, *_args):
        self._label.text = self.text
        self._label.text_color = self.text_color
        self._icon.text = self.icon_text
        self._icon.text_color = self.text_color
        self._icon.opacity = 1 if self.icon_text else 0

    def _sync_colors(self, *_args):
        self.bg_color = self.base_color

    def _on_mouse_pos(self, _window, pos):
        if not self.use_hover or not self.get_root_window():
            return
        inside = self.collide_point(*self.to_widget(*pos))
        if inside != self._hovered:
            self._hovered = inside
            self._animate_to(self.hover_color if inside else self.base_color, scale=1.02 if inside else 1.0)

    def on_press(self):
        self._animate_to(self.pressed_color, scale=0.98, offset=dp(3))

    def on_release(self):
        target = self.hover_color if self._hovered else self.base_color
        self._animate_to(target, scale=1.02 if self._hovered else 1.0, offset=dp(7))

    def _animate_to(self, color, scale=1.0, offset=None):
        Animation.cancel_all(self, "shadow_offset")
        self.bg_color = color
        if offset is not None:
            Animation(shadow_offset=offset, duration=0.12, t="out_cubic").start(self)
        self.scale = scale


class ProductCard(ShadowCard):
    product = ObjectProperty(allownone=False)
    palette = ObjectProperty(allownone=False)
    accent_color = ListProperty([1, 0.4, 0.2, 1])
    selected = BooleanProperty(False)
    on_selected = ObjectProperty(allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(10)
        self.radius_value = dp(30)
        self.shadow_offset = dp(10)
        self.bind(selected=self._refresh_state)
        Clock.schedule_once(lambda *_: self._build(), 0)

    def _build(self):
        if not self.product or not self.palette:
            return
        self.clear_widgets()
        header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24))
        header.add_widget(MDLabel(text="", size_hint_x=1))
        volume_color = hex_to_rgba(self.palette["volume"])
        header.add_widget(
            MDLabel(
                text=f"{float(self.product['volume_l']):g} L",
                halign="right",
                theme_text_color="Custom",
                text_color=volume_color,
                bold=True,
            )
        )
        self.add_widget(header)

        image_box = MDBoxLayout(size_hint_y=1)
        image_widget = Image(source=str(Path(self.product["image"])), allow_stretch=True, keep_ratio=True, pos_hint={"center_x": 0.5, "center_y": 0.55})
        image_box.add_widget(image_widget)
        self.add_widget(image_box)

        price_color = hex_to_rgba(self.palette["price"])
        self.add_widget(
            MDLabel(
                text=f"${float(self.product['price']):.0f}",
                halign="center",
                theme_text_color="Custom",
                text_color=price_color,
                bold=True,
                font_style="H4",
                size_hint_y=None,
                height=dp(42),
            )
        )

        button = ModernButton(
            text=self.product["name"],
            base_color=hex_to_rgba(self.palette["primary"]),
            hover_color=hex_to_rgba(self.palette["secondary"]),
            pressed_color=hex_to_rgba(mix_hex(self.palette["primary"], "#000000", 0.16)),
            text_color=hex_to_rgba(self.palette["buttonText"]),
            size_hint_y=None,
            height=dp(44),
        )
        button.bind(on_release=lambda *_: self._choose())
        self.add_widget(button)
        self._refresh_state()

    def _choose(self):
        if callable(self.on_selected):
            self.on_selected(self.product["id"])

    def _refresh_state(self, *_args):
        panel_alpha = 0.24 if self.selected else 0.16
        border_alpha = 0.42 if self.selected else 0.22
        self.bg_color = [1, 1, 1, panel_alpha]
        self.border_color = [*self.accent_color[:3], border_alpha] if self.selected else [1, 1, 1, border_alpha]
        self.shadow_offset = dp(14 if self.selected else 10)


class HeaderPanel(ShadowCard):
    def __init__(self, branding: dict[str, str], palette: dict[str, str], credit: float, on_menu, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(92)
        self.radius_value = dp(28)
        self.bg_color = [1, 1, 1, 0.18]
        self.border_color = [1, 1, 1, 0.28]
        self.shadow_offset = dp(6)
        self._branding = branding
        self._palette = palette
        self._on_menu = on_menu

        row = MDBoxLayout(orientation="horizontal", spacing=dp(14))
        icon = ShadowCard(size_hint=(None, None), size=(dp(58), dp(58)), radius_value=dp(20), bg_color=hex_to_rgba(palette["panelAlt"]), border_color=[1, 1, 1, 0.28], shadow_color=[0, 0, 0, 0])
        icon.add_widget(MDLabel(text="💧", halign="center", valign="middle", font_style="H5"))
        row.add_widget(icon)

        title_col = MDBoxLayout(orientation="vertical")
        title_col.add_widget(MDLabel(text=branding["title"], bold=True, theme_text_color="Custom", text_color=hex_to_rgba(palette["text"]), font_style="H5"))
        title_col.add_widget(MDLabel(text=branding["tagline"], theme_text_color="Custom", text_color=hex_to_rgba(palette["textSoft"]), font_style="Caption"))
        row.add_widget(title_col)

        credit_card = ShadowCard(size_hint=(None, None), size=(dp(208), dp(56)), radius_value=dp(20), bg_color=hex_to_rgba(palette["panel"], 0.92), border_color=[1, 1, 1, 0.22], shadow_color=[0, 0, 0, 0])
        credit_row = MDBoxLayout(orientation="horizontal", padding=(dp(14), 0, dp(14), 0), spacing=dp(6))
        credit_row.add_widget(MDLabel(text="Crédito", theme_text_color="Custom", text_color=hex_to_rgba(palette["textSoft"]), size_hint_x=None, width=dp(72)))
        self._credit_label = MDLabel(text=f"${credit:.2f}", bold=True, halign="left", theme_text_color="Custom", text_color=hex_to_rgba(palette["price"]), font_style="H5")
        credit_row.add_widget(self._credit_label)
        credit_card.add_widget(credit_row)
        row.add_widget(credit_card)

        menu_button = ModernButton(
            text="Menú",
            base_color=hex_to_rgba(palette["primary"]),
            hover_color=hex_to_rgba(palette["secondary"]),
            pressed_color=hex_to_rgba(mix_hex(palette["primary"], "#000000", 0.14)),
            text_color=hex_to_rgba(palette["buttonText"]),
            size_hint=(None, None),
            size=(dp(120), dp(52)),
        )
        menu_button.bind(on_release=lambda *_: self._on_menu())
        row.add_widget(menu_button)
        self.add_widget(row)

    def set_credit(self, credit: float):
        self._credit_label.text = f"${credit:.2f}"


class DrawerPanel(ShadowCard):
    open_progress = NumericProperty(0.0)

    def __init__(self, branding: dict[str, str], palette: dict[str, str], controller, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.width = dp(300)
        self.height = settings.SCREEN_HEIGHT - dp(36)
        self.pos = (settings.SCREEN_WIDTH + dp(12), dp(18))
        self.radius_value = dp(28)
        self.bg_color = [1, 1, 1, 0.18]
        self.border_color = [1, 1, 1, 0.22]
        self.shadow_offset = dp(8)
        self._controller = controller
        col = MDBoxLayout(orientation="vertical", spacing=dp(14))
        col.add_widget(MDLabel(text=branding["title"], bold=True, theme_text_color="Custom", text_color=hex_to_rgba(palette["text"]), font_style="H5", size_hint_y=None, height=dp(32)))
        col.add_widget(MDLabel(text=branding["tagline"], theme_text_color="Custom", text_color=hex_to_rgba(palette["textSoft"]), font_style="Caption", size_hint_y=None, height=dp(34)))
        col.add_widget(MDLabel(text=f"Sistema: {branding['systemName']}", theme_text_color="Custom", text_color=hex_to_rgba(palette["text"]), size_hint_y=None, height=dp(28)))
        col.add_widget(MDLabel(text=f"Tema: {settings.UI_THEME} / {settings.UI_MODE}", theme_text_color="Custom", text_color=hex_to_rgba(palette["text"]), size_hint_y=None, height=dp(28)))
        col.add_widget(Widget())
        buttons = [
            ("Cambiar tema", controller.cycle_theme),
            ("Cambiar modo", controller.toggle_mode),
            ("Volver a inicio", controller.go_home),
            ("Cerrar", controller.close_drawer),
        ]
        for label, callback in buttons:
            button = ModernButton(
                text=label,
                base_color=hex_to_rgba(palette["primary"]),
                hover_color=hex_to_rgba(palette["secondary"]),
                pressed_color=hex_to_rgba(mix_hex(palette["primary"], "#000000", 0.14)),
                text_color=hex_to_rgba(palette["buttonText"]),
                size_hint_y=None,
                height=dp(50),
            )
            button.bind(on_release=lambda *_args, cb=callback: cb())
            col.add_widget(button)
        self.add_widget(col)

    def open(self):
        Animation.cancel_all(self)
        Animation(x=settings.SCREEN_WIDTH - self.width - dp(18), duration=0.28, t="out_cubic").start(self)

    def close(self):
        Animation.cancel_all(self)
        Animation(x=settings.SCREEN_WIDTH + dp(12), duration=0.22, t="out_cubic").start(self)


class HomeScreen(MDScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.build()

    def build(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(14), padding=dp(18))
        self.header = HeaderPanel(self.controller.branding, self.controller.palette, self.controller.credit, self.controller.toggle_drawer)
        layout.add_widget(self.header)

        title = MDLabel(text="Seleccione un producto", halign="center", theme_text_color="Custom", text_color=hex_to_rgba(self.controller.palette["text"]), bold=True, size_hint_y=None, height=dp(34))
        layout.add_widget(title)

        cards = MDBoxLayout(orientation="horizontal", spacing=dp(16))
        accents = [
            hex_to_rgba(self.controller.palette["primary"]),
            hex_to_rgba(self.controller.palette["secondary"]),
            hex_to_rgba(self.controller.palette["accent"]),
        ]
        self._product_cards: list[ProductCard] = []
        for index, product in enumerate(settings.PRODUCTS):
            card = ProductCard(
                product=product,
                palette=self.controller.palette,
                accent_color=accents[index % len(accents)],
                on_selected=self.controller.select_product,
            )
            self._product_cards.append(card)
            cards.add_widget(card)
        layout.add_widget(cards)
        self.add_widget(layout)

    def refresh(self):
        self.header.set_credit(self.controller.credit)
        for card in self._product_cards:
            card.selected = card.product["id"] == self.controller.selected_product_id


class PaymentScreen(MDScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.build()

    def build(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(18), padding=dp(26))
        self.panel = ShadowCard(radius_value=dp(30), bg_color=[1, 1, 1, 0.18], border_color=[1, 1, 1, 0.22], shadow_offset=dp(8))
        content = MDBoxLayout(orientation="vertical", spacing=dp(18))
        self.title = MDLabel(text="Confirme su selección", bold=True, font_style="H4", theme_text_color="Custom", text_color=hex_to_rgba(self.controller.palette["text"]), size_hint_y=None, height=dp(40))
        self.message = MDLabel(text="", theme_text_color="Custom", text_color=hex_to_rgba(self.controller.palette["textSoft"]), size_hint_y=None, height=dp(40))
        content.add_widget(self.title)
        content.add_widget(self.message)

        button_row = MDBoxLayout(orientation="horizontal", spacing=dp(14), size_hint_y=None, height=dp(54))
        for amount in (1, 5, 10):
            button = ModernButton(
                text=f"+${amount}",
                base_color=hex_to_rgba(self.controller.palette["primary"]),
                hover_color=hex_to_rgba(self.controller.palette["secondary"]),
                pressed_color=hex_to_rgba(mix_hex(self.controller.palette["primary"], "#000000", 0.14)),
                text_color=hex_to_rgba(self.controller.palette["buttonText"]),
            )
            button.bind(on_release=lambda *_args, value=amount: self.controller.add_credit(value))
            button_row.add_widget(button)
        content.add_widget(button_row)
        content.add_widget(Widget())

        footer = MDBoxLayout(orientation="horizontal", spacing=dp(16), size_hint_y=None, height=dp(54))
        back = ModernButton(
            text="Volver",
            base_color=[1, 1, 1, 0.15],
            hover_color=[1, 1, 1, 0.22],
            pressed_color=[1, 1, 1, 0.10],
            text_color=hex_to_rgba(self.controller.palette["text"]),
        )
        back.bind(on_release=lambda *_: self.controller.go_home())
        footer.add_widget(back)
        footer.add_widget(Widget())
        proceed = ModernButton(
            text="Continuar",
            base_color=hex_to_rgba(self.controller.palette["primary"]),
            hover_color=hex_to_rgba(self.controller.palette["secondary"]),
            pressed_color=hex_to_rgba(mix_hex(self.controller.palette["primary"], "#000000", 0.14)),
            text_color=hex_to_rgba(self.controller.palette["buttonText"]),
            size_hint_x=None,
            width=dp(220),
        )
        proceed.bind(on_release=lambda *_: self.controller.start_dispense())
        footer.add_widget(proceed)
        content.add_widget(footer)

        self.panel.add_widget(content)
        layout.add_widget(self.panel)
        self.add_widget(layout)

    def refresh(self):
        selected = next((p for p in settings.PRODUCTS if p["id"] == self.controller.selected_product_id), None)
        product_name = selected["name"] if selected else "Sin producto"
        self.message.text = f"{product_name} | Crédito ${self.controller.credit:.2f} | Precio ${self.controller.selected_price:.2f}"


class DispenseScreen(MDScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.build()

    def build(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(18), padding=dp(26))
        panel = ShadowCard(radius_value=dp(30), bg_color=[1, 1, 1, 0.18], border_color=[1, 1, 1, 0.22], shadow_offset=dp(8))
        col = MDBoxLayout(orientation="vertical", spacing=dp(18))
        col.add_widget(MDLabel(text="Proceso de llenado", bold=True, font_style="H4", theme_text_color="Custom", text_color=hex_to_rgba(self.controller.palette["text"]), size_hint_y=None, height=dp(40)))
        self.message = MDLabel(text="Llenando recipiente...", theme_text_color="Custom", text_color=hex_to_rgba(self.controller.palette["textSoft"]), size_hint_y=None, height=dp(32))
        col.add_widget(self.message)
        self.progress_card = ShadowCard(radius_value=dp(34), bg_color=hex_to_rgba(self.controller.palette["panel"], 0.88), border_color=[1, 1, 1, 0.20], shadow_color=[0, 0, 0, 0], size_hint_y=1)
        self.progress_label = MDLabel(text="0%", halign="center", valign="middle", theme_text_color="Custom", text_color=hex_to_rgba(self.controller.palette["price"]), font_style="H2", bold=True)
        self.progress_card.add_widget(self.progress_label)
        col.add_widget(self.progress_card)
        panel.add_widget(col)
        layout.add_widget(panel)
        self.add_widget(layout)

    def refresh(self):
        self.progress_label.text = f"{self.controller.progress}%"


class MessageScreen(MDScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.build()

    def build(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(18), padding=dp(26))
        panel = ShadowCard(radius_value=dp(30), bg_color=[1, 1, 1, 0.18], border_color=[1, 1, 1, 0.22], shadow_offset=dp(8))
        col = MDBoxLayout(orientation="vertical", spacing=dp(18))
        col.add_widget(MDLabel(text="Gracias por su compra", bold=True, font_style="H4", theme_text_color="Custom", text_color=hex_to_rgba(self.controller.palette["text"]), size_hint_y=None, height=dp(40)))
        col.add_widget(MDLabel(text="Llenado completo. Puede retirar su recipiente.", theme_text_color="Custom", text_color=hex_to_rgba(self.controller.palette["textSoft"]), size_hint_y=None, height=dp(36)))
        col.add_widget(Widget())
        button = ModernButton(
            text="Volver al inicio",
            base_color=hex_to_rgba(self.controller.palette["primary"]),
            hover_color=hex_to_rgba(self.controller.palette["secondary"]),
            pressed_color=hex_to_rgba(mix_hex(self.controller.palette["primary"], "#000000", 0.14)),
            text_color=hex_to_rgba(self.controller.palette["buttonText"]),
            size_hint=(None, None),
            size=(dp(220), dp(52)),
            pos_hint={"right": 1},
        )
        button.bind(on_release=lambda *_: self.controller.go_home())
        col.add_widget(button)
        panel.add_widget(col)
        layout.add_widget(panel)
        self.add_widget(layout)


class ModernVendingApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.credit = 0.0
        self.selected_product_id = ""
        self.progress = 0
        self._progress_event = None
        self.palette = palette_for(settings.UI_THEME, settings.UI_MODE)
        self.branding = {
            "title": settings.BRAND_TITLE,
            "tagline": settings.BRAND_TAGLINE,
            "systemName": settings.SYSTEM_NAME,
        }

    @property
    def selected_price(self) -> float:
        product = next((p for p in settings.PRODUCTS if p["id"] == self.selected_product_id), None)
        return float(product["price"]) if product else 0.0

    def build(self):
        self.title = settings.BRAND_TITLE
        Window.size = (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        Window.softinput_mode = "below_target"
        Window.clearcolor = (0, 0, 0, 0)
        if settings.FULLSCREEN:
            Window.fullscreen = "auto"

        self.theme_cls.theme_style = "Dark" if settings.UI_MODE == "dark" else "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.material_style = "M3"

        root = FloatLayout()
        self._compose_root(root)
        return root

    def _compose_root(self, root: FloatLayout):
        self.background = AnimatedGradientBackground(colors=self.palette["background"])
        root.add_widget(self.background)

        self.screen_manager = ScreenManager(transition=SlideTransition(direction="left", duration=0.32))
        self.home_screen = HomeScreen(self, name="home")
        self.payment_screen = PaymentScreen(self, name="payment")
        self.dispense_screen = DispenseScreen(self, name="dispense")
        self.message_screen = MessageScreen(self, name="message")
        self.screen_manager.add_widget(self.home_screen)
        self.screen_manager.add_widget(self.payment_screen)
        self.screen_manager.add_widget(self.dispense_screen)
        self.screen_manager.add_widget(self.message_screen)
        root.add_widget(self.screen_manager)

        self.drawer = DrawerPanel(self.branding, self.palette, self)
        root.add_widget(self.drawer)

        self.refresh_all()

    def refresh_all(self):
        self.home_screen.refresh()
        self.payment_screen.refresh()
        self.dispense_screen.refresh()

    def select_product(self, product_id: str):
        self.selected_product_id = product_id
        self.screen_manager.transition = SlideTransition(direction="left", duration=0.28)
        self.screen_manager.current = "payment"
        self.refresh_all()

    def add_credit(self, amount: float):
        self.credit = max(0.0, min(999.0, self.credit + float(amount)))
        self.refresh_all()

    def start_dispense(self):
        if not self.selected_product_id or self.credit < self.selected_price:
            return
        self.progress = 0
        self.dispense_screen.refresh()
        self.screen_manager.transition = SwapTransition(duration=0.32)
        self.screen_manager.current = "dispense"
        if self._progress_event:
            self._progress_event.cancel()
        self._progress_event = Clock.schedule_interval(self._tick_progress, 0.08)

    def _tick_progress(self, *_args):
        self.progress = min(100, self.progress + 2)
        self.dispense_screen.refresh()
        if self.progress >= 100:
            if self._progress_event:
                self._progress_event.cancel()
                self._progress_event = None
            self.screen_manager.transition = FadeTransition(duration=0.28)
            self.screen_manager.current = "message"
            return False
        return True

    def go_home(self):
        if self._progress_event:
            self._progress_event.cancel()
            self._progress_event = None
        self.credit = 0.0
        self.progress = 0
        self.selected_product_id = ""
        self.close_drawer()
        self.screen_manager.transition = SlideTransition(direction="right", duration=0.24)
        self.screen_manager.current = "home"
        self.refresh_all()

    def toggle_drawer(self):
        if self.drawer.x < settings.SCREEN_WIDTH:
            self.close_drawer()
        else:
            self.drawer.open()

    def close_drawer(self):
        self.drawer.close()

    def cycle_theme(self):
        names = list(THEMES.keys())
        current = settings.UI_THEME if settings.UI_THEME in names else names[0]
        settings_config = settings.get_runtime_config()
        settings_config["tema"] = names[(names.index(current) + 1) % len(names)]
        self._apply_runtime(settings_config)

    def toggle_mode(self):
        settings_config = settings.get_runtime_config()
        settings_config["modo"] = "dark" if settings.UI_MODE == "light" else "light"
        self._apply_runtime(settings_config)

    def _apply_runtime(self, config: dict):
        sanitized = settings.save_runtime_config(config)
        settings.apply_runtime_config(sanitized)
        self.palette = palette_for(settings.UI_THEME, settings.UI_MODE)
        self.branding = {
            "title": settings.BRAND_TITLE,
            "tagline": settings.BRAND_TAGLINE,
            "systemName": settings.SYSTEM_NAME,
        }
        self.theme_cls.theme_style = "Dark" if settings.UI_MODE == "dark" else "Light"
        current_screen = self.screen_manager.current if hasattr(self, "screen_manager") else "home"
        drawer_was_open = hasattr(self, "drawer") and self.drawer.x < settings.SCREEN_WIDTH
        if self.root:
            self.root.clear_widgets()
            self._compose_root(self.root)
            self.screen_manager.current = current_screen
            if drawer_was_open:
                Clock.schedule_once(lambda *_: self.drawer.open(), 0)


def main(argv: list[str] | None = None) -> int:
    ModernVendingApp().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
