from dataclasses import dataclass

@dataclass
class BSMeasurement:
    x: float
    y: float
    distance: float

@dataclass
class GASample:
    user_x: float
    user_y: float
    measurements: list[BSMeasurement]
    case: str

@dataclass
class Chromossome:
    x: float
    y: float
    fitness: float = float("inf")