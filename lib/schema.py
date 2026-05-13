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
    height: int = 1080
    created_at: str


class SceneBase(BaseModel):
    id: str
    narration_text: str
    audio_path: Optional[str] = None
    duration: Optional[float] = None


# ----- Bulletin scenes -----

class IntroHighlight(BaseModel):
    text: str
    appear_at_sec: float
    style: Literal["stat", "bullet"] = "bullet"  # stat = số to nổi bật, bullet = gạch đầu dòng


class IntroData(BaseModel):
    headline: str
    category: str
    issue_label: Optional[str] = None
    highlights: Optional[list[IntroHighlight]] = None  # bullets/stats hiện sync với narration


class IntroScene(SceneBase):
    type: Literal["intro"]
    data: IntroData


class RankItem(BaseModel):
    rank: int
    label: str
    value: Optional[float] = None  # số chính (giá, giá trị tỷ, VSI, ...). None = không hiển thị
    value_suffix: Optional[str] = None  # đơn vị append sau value, ví dụ "tỷ", "điểm"
    change_pct: Optional[float] = None
    appear_at_sec: Optional[float] = None  # khi nào item này hiện lên (giây, relative to scene start)


class RankingData(BaseModel):
    title: str
    summary_text: Optional[str] = None  # sub-title dưới title (vd "Tổng bán ròng -836 tỷ")
    items: list[RankItem]


class RankingScene(SceneBase):
    type: Literal["ranking"]
    data: RankingData


class MetricData(BaseModel):
    metric: str
    current_value: float
    previous_value: float
    unit: str = ""
    delta: Optional[float] = None  # current - previous, optional override
    context_note: Optional[str] = None  # caption thêm dưới delta (vd "Cao nhất 3 năm", "MA20: 1.847,24")


class MetricScene(SceneBase):
    type: Literal["metric"]
    data: MetricData


class OutroData(BaseModel):
    cta: str
    handle: Optional[str] = None
    next_topic: Optional[str] = None  # teaser cho số tiếp theo, hiện ở góc outro
    date_label: Optional[str] = None  # date stamp ở đầu outro (vd "Phiên 12/05/2026")


class OutroScene(SceneBase):
    type: Literal["outro"]
    data: OutroData


# Discriminated union
Scene = Annotated[
    Union[IntroScene, RankingScene, MetricScene, OutroScene],
    Field(discriminator="type"),
]


class Script(BaseModel):
    video_id: str
    template: Literal["bulletin", "editorial_mystery", "news_analysis"]
    meta: Meta
    scenes: list[Scene]
