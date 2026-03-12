from dataclasses import dataclass
from enum import Enum


class State(str, Enum):
    IDLE = "IDLE"
    WAITING_COIN = "WAITING_COIN"
    CREDIT_READY = "CREDIT_READY"
    FILLING = "FILLING"
    RINSING = "RINSING"
    COMPLETE = "COMPLETE"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    ERROR = "ERROR"


@dataclass
class MachineContext:
    state: State = State.IDLE
    selected_size: str | None = None
    credit: int = 0


class InvalidTransition(Exception):
    pass


class VendingStateMachine:
    def __init__(self) -> None:
        self.ctx = MachineContext()

    def select_size(self, size: str) -> None:
        if self.ctx.state not in {State.IDLE, State.WAITING_COIN, State.CREDIT_READY}:
            raise InvalidTransition("No se puede seleccionar volumen en este estado")
        self.ctx.selected_size = size
        self.ctx.state = State.WAITING_COIN

    def add_credit(self, amount: int, price_required: int) -> None:
        if self.ctx.state not in {State.WAITING_COIN, State.CREDIT_READY}:
            raise InvalidTransition("Crédito no permitido en este estado")
        self.ctx.credit += amount
        self.ctx.state = State.CREDIT_READY if self.ctx.credit >= price_required else State.WAITING_COIN

    def start(self, price_required: int) -> None:
        if self.ctx.state != State.CREDIT_READY:
            raise InvalidTransition("No hay crédito suficiente")
        if self.ctx.credit < price_required:
            raise InvalidTransition("Crédito insuficiente")
        self.ctx.state = State.FILLING

    def start_rinse(self) -> None:
        if self.ctx.state not in {State.IDLE, State.WAITING_COIN, State.CREDIT_READY}:
            raise InvalidTransition("Enjuague no permitido")
        self.ctx.state = State.RINSING

    def complete_cycle(self) -> None:
        if self.ctx.state not in {State.FILLING, State.RINSING}:
            raise InvalidTransition("No hay ciclo activo")
        self.ctx.state = State.COMPLETE

    def acknowledge_complete(self) -> None:
        if self.ctx.state != State.COMPLETE:
            raise InvalidTransition("No hay ciclo completado")
        self.ctx.state = State.IDLE
        self.ctx.selected_size = None
        self.ctx.credit = 0

    def emergency_stop(self) -> None:
        self.ctx.state = State.EMERGENCY_STOP

    def clear_emergency(self) -> None:
        if self.ctx.state != State.EMERGENCY_STOP:
            raise InvalidTransition("No está en paro de emergencia")
        self.ctx.state = State.IDLE
        self.ctx.selected_size = None
        self.ctx.credit = 0
