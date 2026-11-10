"""SQLAlchemy 2.0 ORM models for LeadForge.

Implements the five core tables:
1. IcpProfile (icp_profiles)
2. Prospect (prospects)
3. WebSource (web_sources)
4. EvidenceItem (evidence_items)
5. OutreachDraft (outreach_drafts)

Follows DATABASE.md specifications including constraints, defaults,
foreign keys, and performance indexes. Configured with lazy='selectin'
for native async relationship resolution.
"""

from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy models."""


class IcpProfile(Base):
    """Ideal Customer Profile (ICP) parameters against which prospects are evaluated."""

    __tablename__ = "icp_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vertical: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="B2B SaaS serving SMBs / MSMEs",
        server_default="B2B SaaS serving SMBs / MSMEs",
    )
    target_geo: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="India",
        server_default="India",
    )
    smb_criteria_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default='["Self-serve onboarding", "Pricing in INR", "Mobile-first / WhatsApp capability", "Simplified SME workflows"]',
        server_default='["Self-serve onboarding", "Pricing in INR", "Mobile-first / WhatsApp capability", "Simplified SME workflows"]',
    )
    tech_keywords_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default='["SaaS", "cloud", "subscription", "API", "merchant", "invoicing", "kirana", "MSME"]',
        server_default='["SaaS", "cloud", "subscription", "API", "merchant", "invoicing", "kirana", "MSME"]',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    # Relationships
    prospects: Mapped[list["Prospect"]] = relationship(
        "Prospect",
        back_populates="icp",
        passive_deletes="all",
        lazy="selectin",
    )


class Prospect(Base):
    """Target SaaS company evaluated for ICP fit and outreach potential."""

    __tablename__ = "prospects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    icp_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("icp_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        default=1,
        server_default="1",
    )
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    website_url: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    hq_location: Mapped[str | None] = mapped_column(Text, nullable=True)
    employee_range: Mapped[str | None] = mapped_column(Text, nullable=True)
    lead_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    score_breakdown_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="PENDING",
        server_default="PENDING",
    )
    researched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "lead_score >= 0 AND lead_score <= 100",
            name="check_prospect_lead_score_range",
        ),
        CheckConstraint(
            "status IN ('PENDING', 'RESEARCHING', 'ANALYZED', 'FAILED')",
            name="check_prospect_status_valid",
        ),
        Index("idx_prospects_domain", "domain"),
        Index("idx_prospects_status", "status"),
        Index("idx_prospects_score", "lead_score"),
    )

    # Relationships
    icp: Mapped["IcpProfile"] = relationship(
        "IcpProfile",
        back_populates="prospects",
        lazy="selectin",
    )
    web_sources: Mapped[list["WebSource"]] = relationship(
        "WebSource",
        back_populates="prospect",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    evidence_items: Mapped[list["EvidenceItem"]] = relationship(
        "EvidenceItem",
        back_populates="prospect",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    outreach_drafts: Mapped[list["OutreachDraft"]] = relationship(
        "OutreachDraft",
        back_populates="prospect",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class WebSource(Base):
    """Scraped web page captured from target prospect domain for evidence and caching."""

    __tablename__ = "web_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prospect_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("prospects.id", ondelete="CASCADE"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    page_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="HOMEPAGE",
        server_default="HOMEPAGE",
    )
    raw_text_snippet: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(Text, nullable=False)
    http_status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=200,
        server_default="200",
    )
    publication_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "page_type IN ('HOMEPAGE', 'ABOUT', 'PRICING', 'PRODUCT', 'BLOG', 'OTHER')",
            name="check_web_sources_page_type_valid",
        ),
        Index("idx_web_sources_prospect_id", "prospect_id"),
        Index("idx_web_sources_hash", "content_hash"),
    )

    # Relationships
    prospect: Mapped["Prospect"] = relationship(
        "Prospect",
        back_populates="web_sources",
        lazy="selectin",
    )
    evidence_items: Mapped[list["EvidenceItem"]] = relationship(
        "EvidenceItem",
        back_populates="source",
        lazy="selectin",
    )


class EvidenceItem(Base):
    """Atomic epistemic claim extracted from web source with verbatim quote or reasoning."""

    __tablename__ = "evidence_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prospect_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("prospects.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("web_sources.id", ondelete="SET NULL"),
        nullable=True,
    )
    category: Mapped[str] = mapped_column(Text, nullable=False)
    rubric_criterion: Mapped[str | None] = mapped_column(Text, nullable=True)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    exact_quote: Mapped[str | None] = mapped_column(Text, nullable=True)
    epistemic_status: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        server_default="1.0",
    )
    gemini_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "category IN ('SMB_FOCUS', 'SAAS_MODEL', 'GROWTH_SIGNAL', 'TECH_FIT', 'COMPANY_PROFILE')",
            name="check_evidence_items_category_valid",
        ),
        CheckConstraint(
            "epistemic_status IN ('FACT', 'INFERENCE', 'UNKNOWN')",
            name="check_evidence_items_epistemic_status_valid",
        ),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="check_evidence_items_confidence_range",
        ),
        Index("idx_evidence_prospect_status", "prospect_id", "epistemic_status"),
    )

    # Relationships
    prospect: Mapped["Prospect"] = relationship(
        "Prospect",
        back_populates="evidence_items",
        lazy="selectin",
    )
    source: Mapped["WebSource | None"] = relationship(
        "WebSource",
        back_populates="evidence_items",
        lazy="selectin",
    )


class OutreachDraft(Base):
    """Personalized cold email draft citing verified evidence items."""

    __tablename__ = "outreach_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prospect_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("prospects.id", ondelete="CASCADE"),
        nullable=False,
    )
    template_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="EVIDENCE_PROBLEM_SOLUTION",
        server_default="EVIDENCE_PROBLEM_SOLUTION",
    )
    subject_line: Mapped[str] = mapped_column(Text, nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    citations_json: Mapped[str] = mapped_column(Text, nullable=False)
    tone: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="CONSULTATIVE_DIRECT",
        server_default="CONSULTATIVE_DIRECT",
    )
    generation_source: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="DETERMINISTIC_TEMPLATE",
        server_default="DETERMINISTIC_TEMPLATE",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    __table_args__ = (Index("idx_outreach_prospect", "prospect_id"),)

    # Relationships
    prospect: Mapped["Prospect"] = relationship(
        "Prospect",
        back_populates="outreach_drafts",
        lazy="selectin",
    )
