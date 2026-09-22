"""Plan v3: a small, explicit vocabulary for checking business state."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator, model_validator

from donewitness.browser_plan import (
    AssertVisibleStep,
    BrowserAcceptanceCriterion,
    BrowserVerificationPlan,
    ClickStep,
    FillStep,
    NavigateStep,
)
from donewitness.domain import NonBlankText


class _SelectorAssertion(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    selector: StrictStr

    @field_validator("selector")
    @classmethod
    def require_nonblank_selector(cls, selector: str) -> str:
        if not selector.strip():
            raise ValueError("selector must contain non-whitespace text")
        return selector


class AssertTextStep(_SelectorAssertion):
    """Compare the full text using Playwright's whitespace normalization."""

    type: Literal["assert_text"]
    text: StrictStr


class AssertValueStep(_SelectorAssertion):
    """Compare the exact input value; never record that value as evidence."""

    type: Literal["assert_value"]
    value: StrictStr


class AssertCountStep(_SelectorAssertion):
    """Compare the exact number of matching elements, including zero."""

    type: Literal["assert_count"]
    count: Annotated[int, Field(strict=True, ge=0)]


class AssertHiddenStep(_SelectorAssertion):
    """Assert that an element is hidden or absent (Playwright semantics)."""

    type: Literal["assert_hidden"]


type BrowserStepV3 = Annotated[
    NavigateStep
    | FillStep
    | ClickStep
    | AssertVisibleStep
    | AssertTextStep
    | AssertValueStep
    | AssertCountStep
    | AssertHiddenStep,
    Field(discriminator="type"),
]


class BrowserProcedureV3(BaseModel):
    """A v3 procedure leaves the published v2 validation contract unchanged."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    type: Literal["browser"]
    timeout_ms: Annotated[int, Field(ge=100, le=30_000)] = 5_000
    steps: Annotated[tuple[BrowserStepV3, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def require_navigated_assertion(self) -> BrowserProcedureV3:
        if not isinstance(self.steps[0], NavigateStep):
            raise ValueError("the first browser step must be navigate")
        if not any(
            isinstance(step, (AssertVisibleStep, _SelectorAssertion)) for step in self.steps
        ):
            raise ValueError("browser procedure must contain at least one assertion step")
        return self


class BrowserAcceptanceCriterionV3(BaseModel):
    """A human-reviewed criterion and its deterministic procedure."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: NonBlankText
    description: NonBlankText
    procedure: BrowserProcedureV3


class BrowserVerificationPlanV3(BaseModel):
    """Explicit version boundary for the additional assertions."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_version: Literal[3]
    task: NonBlankText
    criteria: Annotated[tuple[BrowserAcceptanceCriterionV3, ...], Field(min_length=1)]

    @field_validator("criteria")
    @classmethod
    def require_unique_criterion_ids(
        cls,
        criteria: tuple[BrowserAcceptanceCriterionV3, ...],
    ) -> tuple[BrowserAcceptanceCriterionV3, ...]:
        seen: set[str] = set()
        for criterion in criteria:
            if criterion.id in seen:
                raise ValueError(f"criterion id must be unique: {criterion.id}")
            seen.add(criterion.id)
        return criteria


type ExecutableBrowserPlan = BrowserVerificationPlan | BrowserVerificationPlanV3
type ExecutableBrowserCriterion = BrowserAcceptanceCriterion | BrowserAcceptanceCriterionV3
