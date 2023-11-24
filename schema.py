from pydantic import BaseModel, conint, field_validator
from enum import Enum
from typing import Optional
import json


# ------------------------- SCHEMA -------------------------- #

class FighterStyleEnum(Enum):
    MMA = 'mma'
    FREESTYLE = 'freestyle'
    STRIKER = 'striker'
    MUAY_THAI = 'muay-thai'
    JIU_JITSU = ('jiu-jitsu', 'brazilian jiu-jitsu')
    KICKBOXER = 'kickboxer'
    GRAPPLING = 'grappler'
    BOXING = 'boxer'
    BOXER = 'boxer'
    WRESTLER = ('wrestler', 'wrestling')
    KARATE = 'karate'
    JUDO = 'judo'
    SAMBO = 'sambo'
    BRAWLER = 'brawler'
    KUNG_FU = ('kung fu, kung-fu')
    TAEKWONDO = 'taekwondo'

class LastFightOutcomeEnum(Enum):
    WIN = 'win'
    LOSS = 'loss'
    OTHER = 'other'

class Last5Record(BaseModel):
    wins: conint(ge=0, le=5)
    loss: conint(ge=0, le=5)
    other: conint(ge=0, le=5)


class Fighter(BaseModel):
    name: str
    rank: Optional[conint(ge=0, le=15)] = None
    champion: bool
    fighting_style: FighterStyleEnum # fighter.fighting_style.name for clean text
    win_streak: conint(ge=0)
    last_fight_outcome: LastFightOutcomeEnum
    last_5_fight_record: Last5Record = Last5Record(wins=0, loss=0, other=0)
    last_5_opponents: list[str] = []
    # stats: None # nested list of stats
    
    @field_validator('last_5_opponents')
    def opponents_length(cls, value):
        if len(value) > 5:
            raise ValueError("List must be 5 or less!")
        return value

    @field_validator('last_5_fight_record')
    def record_sum(cls, value):
        total = value.wins + value.loss + value.other
        if total > 5:
            raise ValueError("Recent record must be 5 fights or less!")
        return value

# test fighter instance
fighter_data = '''{
    "name": "shayne lussier",
    "rank": "8",
    "champion": "false",
    "fighting_style": "mma",
    "win_streak": "2",
    "last_fight_outcome": "win",
    "last_5_fight_record": {
        "wins": "2",
        "loss": "0",
        "other": "0"
    },
    "last_5_opponents": [
        "john cena",
        "the rock"
    ]
}'''

# Convert JSON string to Python dictionary
data = json.loads(fighter_data)
    
fighter = Fighter(**data)
print(fighter)