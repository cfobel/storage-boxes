from pydantic import BaseModel


class Dimensions(BaseModel):
    width: float
    length: float
    height: float


class BoxParameters(BaseModel):
    columns: int
    rows: int
    height: float = 61.5
    base_height: float = 3.9
    line_width: float = 0.3
    unit_extent: float = 45.8
    default_fillet: float = 2.5

    @property
    def wall_thickness(self):
        return 4 * self.line_width
