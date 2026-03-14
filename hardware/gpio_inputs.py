from gpiozero import Button


class GPIOInputs:
    def __init__(
        self,
        coin_pin: int,
        full_pin: int,
        half_pin: int,
        gallon_pin: int,
        rinse_pin: int,
        ok_pin: int,
        on_coin,
        on_select_full,
        on_select_half,
        on_select_gallon,
        on_rinse_toggle,
        on_ok,
        bounce_time: float = 0.08,
    ):
        self.coin_button = Button(coin_pin, pull_up=True, bounce_time=bounce_time)
        self.full_button = Button(full_pin, pull_up=True, bounce_time=bounce_time)
        self.half_button = Button(half_pin, pull_up=True, bounce_time=bounce_time)
        self.gallon_button = Button(gallon_pin, pull_up=True, bounce_time=bounce_time)
        self.rinse_button = Button(rinse_pin, pull_up=True, bounce_time=bounce_time)
        self.ok_button = Button(ok_pin, pull_up=True, bounce_time=bounce_time)

        self.coin_button.when_pressed = on_coin
        self.full_button.when_pressed = on_select_full
        self.half_button.when_pressed = on_select_half
        self.gallon_button.when_pressed = on_select_gallon
        self.rinse_button.when_pressed = on_rinse_toggle
        self.ok_button.when_pressed = on_ok

    def close(self) -> None:
        self.coin_button.close()
        self.full_button.close()
        self.half_button.close()
        self.gallon_button.close()
        self.rinse_button.close()
        self.ok_button.close()
