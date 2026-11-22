"""The case file Ekmat reads and the report it writes.

M1 reads a structured, human-entered case file. It does not extract facts from scanned documents.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Source(Strict):
    document: str
    page: int | None = None


class Document(Strict):
    kind: str  # e.g. joint_petition, affidavit_wife, marriage_proof
    dated: date | None = None
    husband_name: str | None = None  # the names as this document spells them
    wife_name: str | None = None
    marriage_date: date | None = None  # as this document states it
    separation_date: date | None = None


class PendingCase(Strict):
    kind: Literal["498A", "DV", "maintenance_125", "other"]
    involves_child: bool = False


class Mediation(Strict):
    referred: bool = False
    outcome: Literal["failed", "settled", "pending", "not_attended"] | None = None


class Settlement(Strict):
    maintenance: bool = False  # permanent alimony or maintenance, including an express waiver
    stridhan: Literal["returned", "in_possession", "none_claimed", "not_addressed"] = "not_addressed"
    custody: bool = False
    visitation: bool = False
    child_support: bool = False
    property: bool = False
    pending_cases_plan: bool = False


class CaseFile(Strict):
    schema_version: Literal[1]
    case_id: str
    law: Literal["HMA_13B"] = "HMA_13B"
    jurisdiction: Literal["delhi"]  # M1 covers Delhi only; anything else is rejected
    court_district: str

    husband_name: str
    wife_name: str

    marriage_date: date
    marriage_district: str | None = None
    separation_date: date
    last_resided_together_district: str | None = None
    husband_residence_district: str | None = None
    wife_residence_district: str | None = None

    first_motion_date: date | None = None  # None: not filed yet; the report gives the dates to plan around
    second_motion_date: date | None = None
    s14_leave_application: bool = False  # application for leave under the proviso to s.14(1)
    exceptional_hardship_pleaded: bool = False
    waiver_application_date: date | None = None  # application to waive the s.13B(2) wait

    minor_children: int = 0
    settlement: Settlement = Settlement()
    pending_cases: list[PendingCase] = []
    mediation: Mediation = Mediation()
    documents: list[Document] = []
    sources: dict[str, Source] = {}  # case-file field -> where that fact appears


class FindingSource(Strict):
    fields: list[str]
    document: str | None = None
    page: int | None = None


class Finding(Strict):
    id: str
    rule_id: str
    severity: Literal["defect", "warning", "info"]
    citation: str
    issue: str
    waiver_route: str | None = None
    source: FindingSource
    rule_verified: bool


class Report(Strict):
    tool: str = "ekmat"
    version: str
    case_id: str
    jurisdiction: str
    status: Literal["DEFECTS_FOUND", "NO_DEFECTS_FOUND_IN_FILE"]
    findings: list[Finding]
    timeline: dict[str, date]
    unverified_rules: list[str]
    not_checked: list[str]
    disclaimer: str


class WaiverCondition(Strict):
    id: str
    text: str
    facts_on_file: list[str]
    facts_missing: list[str]
    for_the_court: str


class WaiverBrief(Strict):
    tool: str = "ekmat"
    version: str
    case_id: str
    authority: str
    conditions: list[WaiverCondition]
    local_position: str
    local_position_verified: bool
    disclaimer: str = Field(default="")
