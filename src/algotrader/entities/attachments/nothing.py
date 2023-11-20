from __future__ import annotations

from typing import Literal

from pydantic import Field

from algotrader.entities.base_dto import BaseEntity


class NothingClass(BaseEntity):
    type: Literal["NothingClass"] = "NothingClass"
    nothing: str = Field(default="nothing-at-all")
