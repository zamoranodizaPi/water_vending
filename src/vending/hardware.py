from dataclasses import dataclass, field


@dataclass
class ActuatorState:
    fill_valve: bool = False
    rinse_valve: bool = False
    uv_lamp: bool = False
    ozone_machine: bool = False
    interior_light: bool = False


@dataclass
class HardwareController:
    """Controla estados de actuadores con reglas de seguridad.

    Aquí se modela la lógica; en Raspberry se reemplaza por drivers GPIO reales.
    """

    state: ActuatorState = field(default_factory=ActuatorState)

    def on_door_changed(self, open_: bool) -> None:
        self.state.interior_light = open_

    def start_fill(self) -> None:
        self.state.fill_valve = True
        self.state.rinse_valve = False
        self.state.uv_lamp = True
        self.state.ozone_machine = False

    def start_rinse(self) -> None:
        self.state.fill_valve = False
        self.state.rinse_valve = True
        self.state.uv_lamp = False
        self.state.ozone_machine = False

    def stop_all(self, emergency: bool = False) -> None:
        self.state.fill_valve = False
        self.state.rinse_valve = False
        self.state.uv_lamp = False
        if emergency:
            self.state.ozone_machine = False

    def finish_fill_and_start_ozone(self) -> None:
        self.state.fill_valve = False
        self.state.uv_lamp = False
        self.state.ozone_machine = True

    def stop_ozone(self) -> None:
        self.state.ozone_machine = False
