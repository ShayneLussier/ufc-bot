from pydantic import BaseModel, conint, field_validator
from enum import Enum
from typing import Optional


# ------------------------- SCHEMA -------------------------- #


class WeightClassEnum(Enum):
    FLYWEIGHT = "flyweight"
    BANTAMWEIGHT = "bantamweight"
    FEATHERWEIGHT = "featherweight"
    LIGHTWEIGHT = "lightweight"
    WELTERWEIGHT = "welterweight"
    MIDDLEWEIGHT = "middleweight"
    LIGHT_HEAVYWEIGHT = "light heavyweight"
    HEAVYWEIGHT = "heavyweight"
    WOMEN_STRAWWEIGHT = "women's starwweight"
    WOMEN_FLYWEIGHT = "women's flyweight"
    WOMEN_BANTAMWEIGHT = "women's bantamweight"
    WOMEN_FEATHERWEIGHT = "women's featherweight"


class LastFightOutcomeEnum(Enum):
    WIN = "win"
    LOSS = "loss"
    OTHER = "other"
    NOT_FOUND = "not found"


class Last5Record(BaseModel):
    wins: conint(ge=0, le=5)
    loss: conint(ge=0, le=5)
    other: conint(ge=0, le=5)


class Fighter(BaseModel):
    name: str
    weight_class: WeightClassEnum
    rank: Optional[conint(ge=0, le=15)] = None
    champion: bool
    win_streak: conint(ge=0)
    last_fight_outcome: LastFightOutcomeEnum
    last_5_fight_record: Last5Record = Last5Record(wins=0, loss=0, other=0)
    last_5_opponents: list[str] = []
    # stats: None # nested list of stats

    @field_validator("last_5_opponents")
    def opponents_length(cls, value):
        if len(value) > 5:
            raise ValueError("List must be 5 or less!")
        return value

    @field_validator("last_5_fight_record")
    def record_sum(cls, value):
        total = value.wins + value.loss + value.other
        if total > 5:
            raise ValueError("Recent record must be 5 fights or less!")
        return value

    # return data as a dictionary
    def to_dict(self):
        return (
            {
                "name": self.name,
                "weight_class": self.weight_class.value,
                "rank": str(self.rank) if self.rank is not None else None,
                "champion": str(self.champion).lower(),
                "win_streak": str(self.win_streak),
                "last_fight_outcome": self.last_fight_outcome.value,
                "last_5_fight_record": {
                    "wins": str(self.last_5_fight_record.wins),
                    "loss": str(self.last_5_fight_record.loss),
                    "other": str(self.last_5_fight_record.other),
                },
                "last_5_opponents": self.last_5_opponents,
            },
        )
