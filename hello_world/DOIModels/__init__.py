from pydantic import BaseModel as _BaseModel, ConfigDict, AliasGenerator
from typing import List, Optional, Dict


def from_dash(s: str) -> str:
    return s.replace('-', '_')


def to_dash(s: str) -> str:
    return s.replace('_', '-')


class BaseModel(_BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_dash,
            serialization_alias=from_dash,
        )
    )

class Date(BaseModel):
    date_parts: List[List[int]]
    date_time: Optional[str] = None
    timestamp: Optional[int] = None

    def to_tana(self) -> str:
        return f"[[date:{self.year:d}-{self.month:02d}-{self.day:02d}]]"

    @property
    def year(self):
        return self.date_parts[0][0]

    @property
    def month(self):
        try:
            return self.date_parts[0][1]
        except IndexError:
            return 1

    @property
    def day(self):
        try:
            return self.date_parts[0][2]
        except IndexError:
            return 1


class LicenseElement(BaseModel):
    start: Optional[Date] = None
    content_version: Optional[str] = None
    delay_in_days: Optional[int] = None
    URL: Optional[str] = None


class FunderElement(BaseModel):
    DOI: Optional[str] = None
    name: Optional[str] = None
    doi_asserted_by: Optional[str] = None
    award: Optional[List[str]] = None


class ContentDomain(BaseModel):
    domain: List[str]
    crossmark_restriction: bool


class AuthorAffiliation(BaseModel):
    name: str


class Institution(BaseModel):
    name: str


class Author(BaseModel):
    given: str
    family: str
    sequence: str
    affiliation: List[AuthorAffiliation]

    def to_tana(self, indent=0, link_dict: dict[str, str] = None) -> str:
        link_dict = link_dict or {}
        indent_spaces = '  ' * indent

        a_name = f"{self.given} {self.family}"
        if a_name in link_dict:
            out_lines = [f"{indent_spaces}- [[^{link_dict[a_name]}]]"]
        else:
            out_lines = [
                f"{indent_spaces}- {a_name} #author",
                f"{indent_spaces}  - Company::"
            ]
            for c_affiliation in self.affiliation:
                cleaned_affiliation_name = c_affiliation.name.replace('\r', '')
                out_lines += [f"{indent_spaces}    - {cleaned_affiliation_name}"]

        return '\n'.join(out_lines)


class Reference(BaseModel):
    key: str
    doi_asserted_by: Optional[str] = None
    first_page: Optional[str] = None
    DOI: Optional[str] = None
    volume: Optional[str] = None
    author: Optional[str] = None
    year: Optional[str] = None
    journal_title: Optional[str] = None


class Link(BaseModel):
    URL: str
    content_type: Optional[str] = None
    content_version: Optional[str] = None
    intended_application: Optional[str] = None


class Resource(BaseModel):
    primary: Dict[str, str]


class JournalIssue(BaseModel):
    issue: str
    published_print: Optional[Date] = None


class MainObject(BaseModel):
    indexed: Optional[Date] = None
    reference_count: Optional[int] = None
    publisher: Optional[str] = None
    issue: Optional[str] = None
    license: Optional[List[LicenseElement]] = None
    funder: Optional[List[FunderElement]] = None
    content_domain: Optional[ContentDomain] = None
    published_print: Optional[Optional[Date]] = None
    DOI: str
    type: Optional[str] = None
    created: Optional[Date] = None
    page: Optional[str] = None
    source: Optional[str] = None
    is_referenced_by_count: Optional[int] = None
    title: str
    prefix: Optional[str] = None
    volume: Optional[str] = None
    author: List[Author]
    member: Optional[str] = None
    published_online: Optional[Date] = None
    reference: Optional[List[Reference]] = None
    container_title: str | List[str]
    language: Optional[str] = None
    link: Optional[List[Link]] = None
    deposited: Optional[Date] = None
    score: Optional[int] = None
    subtitle: Optional[List[str]] = None
    short_title: Optional[List[str]] = None
    issued: Optional[Date] = None
    references_count: Optional[int] = None
    journal_issue: Optional[JournalIssue] = None
    alternative_id: Optional[List[str]] = None
    URL: str
    relation: Optional[Dict] = None
    ISSN: Optional[List[str]] = None
    container_title_short: Optional[str] = None
    published: Optional[Date] = None
    subject: Optional[List[str]] = None
    institution: Optional[List[Institution]] = None

    @property
    def journal_title(self):
        if self.container_title:
            if isinstance(self.container_title, list):
                return self.container_title[0]
            return self.container_title

        if self.institution:
            return self.institution[0].name

        return '**Not Found**'

    def to_tana(self, link_dict: dict[str, str] = None) -> str:
        link_dict = link_dict or {}
        self.title = self.title.replace('<i>', '__').replace('</i>', '__')
        if self.journal_title in link_dict:
            journal_val = f"[[^{link_dict[self.journal_title]}]]"
        else:
            journal_val = f"{self.journal_title} #[[journal (publication) (Tanarian Brain)]]"

        out_lines = [
            f"- {self.title} #[[journal article]]",
            f"  - Title:: {self.title}",
            f"  - Source Status (Tanarian Brain):: [[^WoGDs0D2cBwU]]",
            f"  - Journal:: {journal_val}",
            f"  - Volume:: {self.volume}",
            f"  - Issue:: {self.issue}",
            f"  - Publication Date (Tanarian Brain):: {self.published.to_tana()}",
            f"  - DOI:: {self.DOI}",
            f"  - Year (Tanarian Brain):: {self.published.year} #year"
        ]

        if self.subject:
            out_lines += [
                '  - Tags:: ' + ', '.join(self.subject)
            ]

        if self.author:
            out_lines += ['  - Author::']
            for c_author in self.author:
                out_lines.append(c_author.to_tana(2, link_dict))

        return '\n'.join(out_lines)
