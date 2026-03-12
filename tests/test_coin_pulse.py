import pytest

from src.vending.coin_pulse import DEFAULT_PULSE_MAP, PulseCoinAcceptor


def test_decode_supported_coins() -> None:
    c = PulseCoinAcceptor(DEFAULT_PULSE_MAP)
    assert c.decode(1) == 1
    assert c.decode(2) == 2
    assert c.decode(5) == 5
    assert c.decode(10) == 10


def test_decode_invalid_pulse() -> None:
    c = PulseCoinAcceptor(DEFAULT_PULSE_MAP)
    with pytest.raises(ValueError):
        c.decode(3)
