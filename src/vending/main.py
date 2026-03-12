from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .coin_pulse import DEFAULT_PULSE_MAP, PulseCoinAcceptor
from .config import load_config
from .hardware import HardwareController
from .state_machine import VendingStateMachine

BASE_DIR = Path(__file__).resolve().parents[2]

app = FastAPI(title="Lupita Vending")
app.mount("/ui", StaticFiles(directory=BASE_DIR / "ui"), name="ui")
app.mount("/assets", StaticFiles(directory=BASE_DIR / "assets"), name="assets")

sm = VendingStateMachine()
hw = HardwareController()
config = load_config(BASE_DIR / "config" / "default.yaml")
coin = PulseCoinAcceptor(DEFAULT_PULSE_MAP)


@app.get("/")
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "ui" / "index.html")


@app.get("/api/status")
def status() -> dict:
    return {
        "state": sm.ctx.state,
        "selected_size": sm.ctx.selected_size,
        "credit": sm.ctx.credit,
        "prices": config.prices,
        "hardware": hw.state.__dict__,
    }


@app.post("/api/select/{size}")
def select_size(size: str) -> dict:
    sm.select_size(size)
    return {"ok": True, "state": sm.ctx.state}


@app.post("/api/coin/{pulses}")
def add_coin(pulses: int) -> dict:
    value = coin.decode(pulses)
    selected = sm.ctx.selected_size or "gallon"
    price = config.prices.get(selected, 0)
    sm.add_credit(value, price)
    return {"inserted": value, "credit": sm.ctx.credit, "state": sm.ctx.state}


@app.post("/api/start")
def start() -> dict:
    selected = sm.ctx.selected_size or "gallon"
    price = config.prices[selected]
    sm.start(price)
    hw.start_fill()
    return {"ok": True, "state": sm.ctx.state, "hardware": hw.state.__dict__}


@app.post("/api/rinse")
def rinse() -> dict:
    sm.start_rinse()
    hw.start_rinse()
    return {"ok": True, "state": sm.ctx.state, "hardware": hw.state.__dict__}


@app.post("/api/complete")
def complete() -> dict:
    sm.complete_cycle()
    hw.finish_fill_and_start_ozone()
    return {"ok": True, "state": sm.ctx.state, "hardware": hw.state.__dict__}


@app.post("/api/ack")
def ack() -> dict:
    sm.acknowledge_complete()
    hw.stop_ozone()
    return {"ok": True, "state": sm.ctx.state, "hardware": hw.state.__dict__}


@app.post("/api/emergency")
def emergency() -> dict:
    sm.emergency_stop()
    hw.stop_all(emergency=True)
    return {"ok": True, "state": sm.ctx.state, "hardware": hw.state.__dict__}
