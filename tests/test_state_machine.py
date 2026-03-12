import pytest

from src.vending.state_machine import InvalidTransition, State, VendingStateMachine


def test_credit_and_start_cycle() -> None:
    sm = VendingStateMachine()
    sm.select_size("gallon")
    sm.add_credit(5, 10)
    assert sm.ctx.state == State.WAITING_COIN
    sm.add_credit(5, 10)
    assert sm.ctx.state == State.CREDIT_READY
    sm.start(10)
    assert sm.ctx.state == State.FILLING


def test_invalid_start_without_credit() -> None:
    sm = VendingStateMachine()
    sm.select_size("gallon")
    with pytest.raises(InvalidTransition):
        sm.start(10)
