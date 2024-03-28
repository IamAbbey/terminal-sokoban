from functools import cache
import pathlib
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, computed_field

BASE_DIR = pathlib.Path(__file__).resolve().parent


class Stage(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    static_index_list: list[int] = Field(alias="staticIndexList")
    box_start_position: list[int] = Field(alias="bricksStartPosition")
    box_storage_position_list: list[int] = Field(alias="foodPositionList")
    player_start_index: int = Field(alias="playerStartIndex")
    board_dimension_row: int = Field(alias="boardDimensionRow")
    board_dimension_column: int = Field(alias="boardDimensionColumn")

    @computed_field
    def dimension(self) -> tuple[int, int]:
        return (self.board_dimension_row, self.board_dimension_column)


@cache
def get_stages():
    return TypeAdapter(tuple[Stage, ...]).validate_json(
        pathlib.Path(BASE_DIR / "data" / "stages.json").read_bytes()
    )
