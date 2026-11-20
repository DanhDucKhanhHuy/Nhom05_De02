"""Định nghĩa trạng thái bất biến của drone."""

from dataclasses import dataclass

from src.contracts import ToaDo


@dataclass(frozen=True, slots=True)
class DroneState:
    """Trạng thái gồm vị trí, thuốc, pin và các ô bệnh chưa phun."""

    position: ToaDo
    medicine: int
    battery: int
    untreated: frozenset[ToaDo]
