from dataclasses import dataclass


@dataclass
class PulseCoinAcceptor:
    """Mapea pulsos a denominación para monedero de pulso."""

    pulse_to_value: dict[int, int]

    def decode(self, pulse_count: int) -> int:
        if pulse_count not in self.pulse_to_value:
            raise ValueError(f"Pulso inválido: {pulse_count}")
        return self.pulse_to_value[pulse_count]


DEFAULT_PULSE_MAP = {
    1: 1,
    2: 2,
    5: 5,
    10: 10,
}
