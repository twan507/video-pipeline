"""Pydantic models = SOURCE OF TRUTH. Sync to TS via scripts/sync_schema.py.

Bulletin template scenes only for Phase 1. Add editorial_mystery + news_analysis later.
"""
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field

DEFAULT_VOICE = "hn_male_phuthang_news65dt_44k-fhg"  # HN - Anh Khoi, news, 44k


class Meta(BaseModel):
    title: str
    voice: str = DEFAULT_VOICE
    speed: float = 1.0
    fps: int = 30
    width: int = 1080
    height: int = 1920
    created_at: str


class SceneBase(BaseModel):
    id: str
    narration_text: str
    audio_path: Optional[str] = None
    duration: Optional[float] = None


# ----- Bulletin scenes -----

class HeadlineData(BaseModel):
    headline: str
    category: str
    issue_label: Optional[str] = None


class HeadlineScene(SceneBase):
    type: Literal["headline"]
    data: HeadlineData


class RankItem(BaseModel):
    rank: int
    label: str
    value: float
    change_pct: Optional[float] = None


class QuickRankData(BaseModel):
    title: str
    items: list[RankItem]


class QuickRankScene(SceneBase):
    type: Literal["quick_rank"]
    data: QuickRankData


class KPIData(BaseModel):
    metric: str
    current_value: float
    previous_value: float
    unit: str = ""
    delta: Optional[float] = None  # current - previous, optional override


class KPIScene(SceneBase):
    type: Literal["kpi"]
    data: KPIData


class OutroData(BaseModel):
    cta: str
    handle: Optional[str] = None


class OutroScene(SceneBase):
    type: Literal["outro"]
    data: OutroData


# Discriminated union
Scene = Annotated[
    Union[HeadlineScene, QuickRankScene, KPIScene, OutroScene],
    Field(discriminator="type"),
]


class Script(BaseModel):
    video_id: str
    template: Literal["bulletin", "editorial_mystery", "news_analysis"]
    meta: Meta
    scenes: list[Scene]
