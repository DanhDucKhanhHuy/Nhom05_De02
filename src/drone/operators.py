"""Các toán tử biến đổi trạng thái và chi phí của chúng."""

from dataclasses import dataclass
from enum import Enum

from src.contracts import ToaDo
from src.drone.state import DroneState


class ActionType(str, Enum):
    """Ba loại hành động drone có thể thực hiện."""

    MOVE = "bay"
    SPRAY = "phun"
    REFILL = "nap"


@dataclass(frozen=True, slots=True)
class Action:
    """Hành động cùng tọa độ đích và các vật cản bay vượt qua."""

    kind: ActionType
    position: ToaDo
    crossed_obstacles: tuple[ToaDo, ...] = ()


@dataclass(frozen=True, slots=True)
class Transition:
    """Trạng thái kế tiếp, chi phí quãng đường và pin tiêu hao."""

    state: DroneState
    action: Action
    cost: int
    battery_cost: int = 0


def bay(
    state: DroneState,
    dich: ToaDo,
    pin_den_tram: int,
    quang_duong: int = 1,
    pin_ton: int = 1,
    vat_can: tuple[ToaDo, ...] = (),
) -> Transition | None:
    """Bay tới ô trống; mỗi vật cản vượt qua bị cộng thêm một đơn vị pin."""
    pin_con = state.battery - pin_ton
    if pin_con < pin_den_tram:
        return None

    moi = DroneState(
        position=dich,
        medicine=state.medicine,
        battery=pin_con,
        untreated=state.untreated,
    )
    return Transition(
        moi,
        Action(ActionType.MOVE, dich, vat_can),
        cost=quang_duong,
        battery_cost=pin_ton,
    )


def phun(state: DroneState, dich: ToaDo) -> Transition | None:
    """Phun một ô bệnh chưa xử lý; mỗi ô chỉ tốn một đơn vị thuốc."""
    if dich != state.position or dich not in state.untreated or state.medicine < 1:
        return None

    moi = DroneState(
        position=state.position,
        medicine=state.medicine - 1,
        battery=state.battery,
        untreated=state.untreated - {dich},
    )
    return Transition(moi, Action(ActionType.SPRAY, dich), cost=0)


def nap(
    state: DroneState,
    suc_chua: int,
    pin_max: int,
    tai_tram: bool,
) -> Transition | None:
    """Nạp đầy thuốc và pin tại trạm nếu ít nhất một tài nguyên đang thiếu."""
    if not tai_tram or (state.medicine == suc_chua and state.battery == pin_max):
        return None

    moi = DroneState(
        position=state.position,
        medicine=suc_chua,
        battery=pin_max,
        untreated=state.untreated,
    )
    return Transition(moi, Action(ActionType.REFILL, state.position), cost=0)
