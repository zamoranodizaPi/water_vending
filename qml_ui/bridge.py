"""Python bridge between the vending logic/config and the QML frontend."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Property, QAbstractListModel, QModelIndex, QObject, QTimer, Qt, QUrl, Signal, Slot

from config import settings
from qml_ui.palettes import THEMES, palette_for


class ProductListModel(QAbstractListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    VolumeRole = Qt.UserRole + 3
    PriceRole = Qt.UserRole + 4
    ImageRole = Qt.UserRole + 5
    AccentRole = Qt.UserRole + 6

    def __init__(self, products: list[dict], accents: list[str], parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._products = products
        self._accents = accents

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._products)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        product = self._products[index.row()]
        if role == self.IdRole:
            return product["id"]
        if role == self.NameRole:
            return product["name"]
        if role == self.VolumeRole:
            return float(product["volume_l"])
        if role == self.PriceRole:
            return float(product["price"])
        if role == self.ImageRole:
            return QUrl.fromLocalFile(str(Path(product["image"]).resolve())).toString()
        if role == self.AccentRole:
            return self._accents[index.row() % len(self._accents)]
        return None

    def roleNames(self) -> dict[int, bytes]:
        return {
            self.IdRole: b"id",
            self.NameRole: b"name",
            self.VolumeRole: b"volume",
            self.PriceRole: b"price",
            self.ImageRole: b"image",
            self.AccentRole: b"accent",
        }

    def refresh(self, products: list[dict], accents: list[str]) -> None:
        self.beginResetModel()
        self._products = products
        self._accents = accents
        self.endResetModel()


class AppBridge(QObject):
    brandChanged = Signal()
    themeChanged = Signal()
    creditChanged = Signal()
    selectedProductChanged = Signal()
    screenChanged = Signal()
    progressChanged = Signal()
    infoMessageChanged = Signal()
    drawerOpenChanged = Signal()
    particlesEnabledChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._credit = 0.0
        self._selected_product_id = ""
        self._screen = "home"
        self._progress = 0
        self._info_message = "Seleccione un producto para comenzar"
        self._drawer_open = False
        self._particles_enabled = settings.UI_THEME == "arcade_mario"
        self._products = [dict(product) for product in settings.PRODUCTS]
        self._product_model = ProductListModel(self._products, self._accent_cycle(), self)
        self._demo_timer = QTimer(self)
        self._demo_timer.setInterval(90)
        self._demo_timer.timeout.connect(self._tick_demo_progress)

    def _accent_cycle(self) -> list[str]:
        palette = self.palette
        return [
            str(palette["primary"]),
            str(palette["secondary"]),
            str(palette["accent"]),
        ]

    @Property(QObject, constant=True)
    def productModel(self) -> QObject:
        return self._product_model

    @Property("QVariantMap", notify=brandChanged)
    def branding(self) -> dict[str, str]:
        return {
            "title": settings.BRAND_TITLE,
            "tagline": settings.BRAND_TAGLINE,
            "systemName": settings.SYSTEM_NAME,
            "contactEmail": settings.CONTACT_EMAIL,
            "contactPhone": settings.CONTACT_PHONE,
        }

    @Property(str, notify=themeChanged)
    def themeName(self) -> str:
        return settings.UI_THEME

    @Property(str, notify=themeChanged)
    def themeMode(self) -> str:
        return settings.UI_MODE

    @Property("QVariantMap", notify=themeChanged)
    def palette(self) -> dict[str, object]:
        return palette_for(settings.UI_THEME, settings.UI_MODE)

    @Property(float, notify=creditChanged)
    def credit(self) -> float:
        return self._credit

    @Property(str, notify=selectedProductChanged)
    def selectedProductId(self) -> str:
        return self._selected_product_id

    @Property(float, notify=selectedProductChanged)
    def selectedPrice(self) -> float:
        product = self._selected_product()
        return float(product["price"]) if product else 0.0

    @Property(str, notify=screenChanged)
    def currentScreen(self) -> str:
        return self._screen

    @Property(int, notify=progressChanged)
    def progressValue(self) -> int:
        return self._progress

    @Property(str, notify=infoMessageChanged)
    def infoMessage(self) -> str:
        return self._info_message

    @Property(bool, notify=drawerOpenChanged)
    def drawerOpen(self) -> bool:
        return self._drawer_open

    @Property(bool, notify=particlesEnabledChanged)
    def particlesEnabled(self) -> bool:
        return self._particles_enabled

    @Slot(str)
    def selectProduct(self, product_id: str) -> None:
        if not any(product["id"] == product_id for product in self._products):
            return
        self._selected_product_id = product_id
        self._screen = "payment"
        self._info_message = "Ingrese crédito y confirme cuando esté listo"
        self.selectedProductChanged.emit()
        self.screenChanged.emit()
        self.infoMessageChanged.emit()

    @Slot(float)
    def addCredit(self, amount: float) -> None:
        self._credit = max(0.0, min(999.0, self._credit + float(amount)))
        self.creditChanged.emit()
        if self._selected_product_id:
            needed = max(0.0, self.selectedPrice - self._credit)
            self._info_message = "Crédito completo. Presione continuar." if needed <= 0 else f"Faltan ${needed:.2f}"
            self.infoMessageChanged.emit()

    @Slot()
    def proceedFromPayment(self) -> None:
        if not self._selected_product_id:
            self._info_message = "Seleccione un producto primero"
            self.infoMessageChanged.emit()
            return
        if self._credit < self.selectedPrice:
            missing = self.selectedPrice - self._credit
            self._info_message = f"Crédito insuficiente. Faltan ${missing:.2f}"
            self.infoMessageChanged.emit()
            return
        self._screen = "dispensing"
        self._progress = 0
        self._info_message = "Llenando recipiente..."
        self.screenChanged.emit()
        self.progressChanged.emit()
        self.infoMessageChanged.emit()
        self._demo_timer.start()

    @Slot()
    def goHome(self) -> None:
        self._demo_timer.stop()
        self._screen = "home"
        self._progress = 0
        self._credit = 0.0
        self._selected_product_id = ""
        self._info_message = "Seleccione un producto para comenzar"
        self.screenChanged.emit()
        self.progressChanged.emit()
        self.creditChanged.emit()
        self.selectedProductChanged.emit()
        self.infoMessageChanged.emit()

    @Slot()
    def toggleDrawer(self) -> None:
        self._drawer_open = not self._drawer_open
        self.drawerOpenChanged.emit()

    @Slot()
    def toggleMode(self) -> None:
        config = settings.get_runtime_config()
        config["modo"] = "dark" if settings.UI_MODE == "light" else "light"
        self._apply_runtime_config(config)

    @Slot(str)
    def setTheme(self, theme_name: str) -> None:
        if theme_name not in THEMES:
            return
        config = settings.get_runtime_config()
        config["tema"] = theme_name
        self._apply_runtime_config(config)

    @Slot()
    def cycleTheme(self) -> None:
        theme_names = list(THEMES.keys())
        current = settings.UI_THEME if settings.UI_THEME in theme_names else theme_names[0]
        next_index = (theme_names.index(current) + 1) % len(theme_names)
        self.setTheme(theme_names[next_index])

    def _apply_runtime_config(self, config: dict) -> None:
        sanitized = settings.save_runtime_config(config)
        settings.apply_runtime_config(sanitized)
        self._particles_enabled = settings.UI_THEME == "arcade_mario"
        self._product_model.refresh([dict(product) for product in settings.PRODUCTS], self._accent_cycle())
        self.themeChanged.emit()
        self.brandChanged.emit()
        self.particlesEnabledChanged.emit()
        self.selectedProductChanged.emit()

    def _selected_product(self) -> dict | None:
        return next((product for product in self._products if product["id"] == self._selected_product_id), None)

    def _tick_demo_progress(self) -> None:
        self._progress = min(100, self._progress + 2)
        self.progressChanged.emit()
        if self._progress >= 100:
            self._demo_timer.stop()
            self._screen = "message"
            self._info_message = "Llenado completo. Gracias por su compra."
            self.screenChanged.emit()
            self.infoMessageChanged.emit()

