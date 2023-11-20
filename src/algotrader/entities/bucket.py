from __future__ import annotations

import math
from typing import List, Union, Optional

from pydantic import Field

from algotrader.entities.base_dto import BaseEntity


class Bucket(BaseEntity):
    ident: float
    start: Optional[float] = Field(default=-math.inf)
    end: Optional[float] = Field(default=math.inf)

    @property
    def get_start(self):
        return self.start or -math.inf

    @property
    def get_end(self):
        return self.end or math.inf


BucketList = List[Bucket]
CompoundBucketList = Union[List[BucketList], BucketList]
