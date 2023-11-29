from pydantic import BaseModel, conint, field_validator
from enum import Enum


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
    WOMEN_STRAWWEIGHT = "women's strawweight"
    WOMEN_FLYWEIGHT = "women's flyweight"
    WOMEN_BANTAMWEIGHT = "women's bantamweight"
    WOMEN_FEATHERWEIGHT = "women's featherweight"


class LastFightOutcomeEnum(Enum):
    WIN = "win"
    LOSS = "loss"
    OTHER = "other"
    NOT_FOUND = "not found"


class Fighter(BaseModel):
    id: str
    name: str
    country: str | None
    weight_class: WeightClassEnum
    rank: conint(ge=0, le=15) | None
    champion: bool
    win_streak: conint(ge=0)
    last_fight_outcome: LastFightOutcomeEnum
    fight_record: dict
    last_5_opponents: list[str] = []

    @field_validator("last_5_opponents")
    def opponents_length(cls, value):
        if len(value) > 5:
            raise ValueError("List must be 5 or less!")
        return value
    

    # return data as a dictionary
    def to_dict(self):
        return (
            {
                "_id": self.id,
                "name": self.name,
                "country": self.country,
                "weight_class": self.weight_class.value,
                "rank": str(self.rank) if self.rank is not None else None,
                "champion": str(self.champion).lower(),
                "win_streak": str(self.win_streak),
                "last_fight_outcome": self.last_fight_outcome.value,
                "fight_record": self.fight_record,
                "last_5_opponents": self.last_5_opponents,
            },
        )

