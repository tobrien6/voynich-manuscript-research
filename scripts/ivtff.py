"""Read the conventional page/locus form of IVTFF 2.0 without resolving text.

Not a full IVTFF conformance validator: alternative compact locus identifiers
and other format versions are rejected. Text annotations are preserved verbatim.
"""

from dataclasses import dataclass
from pathlib import Path
import re


HEADER = re.compile(r"#=IVTFF ([!-~]{4}) (2\.0) ([MDA])(?: .*)?")
PAGE = r"(?:f[1-9][0-9]*[rv][1-6]?|fRos)"
PAGE_HEADER = re.compile(rf"<({PAGE})>(.*)")
LOCUS = re.compile(
    rf"<({PAGE})\.([1-9][0-9]{{0,2}}),([@+*=&~/!])([A-Z][a-z0-9])(?:;([^\s<>;]))?>(.*)"
)
FREE_COMMENT = re.compile(r"<![^>]*>")
TAG = re.compile(r"<@([A-Z])=([A-Za-z0-9@])>")


@dataclass(frozen=True)
class Locus:
    page: str
    number: int
    locator: str
    kind: str
    transcriber: str | None
    text: str
    line_number: int
    variables: dict[str, str]

    @property
    def key(self):
        """Location without alphabet, locator or transcriber differences."""
        return f"{self.page}.{self.number}"

    @property
    def identifier(self):
        suffix = f";{self.transcriber}" if self.transcriber else ""
        return f"{self.key},{self.locator}{self.kind}{suffix}"

    @property
    def present(self):
        return self.locator != "!"


@dataclass(frozen=True)
class Document:
    header: str
    alphabet: str
    pages: dict[str, dict[str, str]]
    loci: tuple[Locus, ...]


def without_free_comments(text):
    """Do not count annotation-like characters inside human comments."""
    return FREE_COMMENT.sub("", text)


def _logical_lines(lines):
    pending = None
    parts = []
    for number, original in enumerate(lines, 1):
        line = original.rstrip()
        if pending is not None:
            if not line.startswith("/"):
                raise ValueError(f"line {number}: expected continuation beginning with /")
            part = line[1:].lstrip()
        else:
            if line.startswith("/"):
                raise ValueError(f"line {number}: orphan continuation")
            if not line or line.startswith("#"):
                continue
            pending = number
            part = line
        continued = part.endswith("/")
        parts.append(part[:-1].rstrip() if continued else part)
        if not continued:
            yield pending, "".join(parts)
            pending, parts = None, []
    if pending is not None:
        raise ValueError(f"line {pending}: unfinished continuation")


def parse_ivtff(text):
    lines = text.splitlines()
    if not lines:
        raise ValueError("empty IVTFF file")
    header = HEADER.fullmatch(lines[0])
    if not header:
        raise ValueError("unsupported header: require conventional IVTFF 2.0")
    pages, loci, seen = {}, [], set()
    current_page = None
    variables = {}
    last_number = 0
    # Keep physical source line numbers by including the skipped header here.
    for line_number, line in _logical_lines(lines):
        match = LOCUS.fullmatch(line)
        if match:
            page, number, locator, kind, transcriber, raw_text = match.groups()
            number = int(number)
            if page != current_page:
                raise ValueError(f"line {line_number}: locus page does not match page header")
            identity = (page, number, transcriber)
            if identity in seen:
                raise ValueError(f"line {line_number}: duplicate locus/transcriber")
            if number < last_number:
                raise ValueError(f"line {line_number}: locus numbers out of order")
            seen.add(identity)
            last_number = number
            visible = without_free_comments(raw_text)
            tags = {}
            for tag, value in TAG.findall(visible):
                if tag in tags and tags[tag] != value:
                    raise ValueError(f"line {line_number}: conflicting text tags")
                tags[tag] = value
            for tag, value in tags.items():
                if value == "@":
                    variables.pop(tag, None)
                else:
                    variables[tag] = value
            loci.append(Locus(page, number, locator, kind, transcriber,
                              raw_text.strip(), line_number, dict(variables)))
            continue
        match = PAGE_HEADER.fullmatch(line)
        if not match:
            raise ValueError(f"line {line_number}: unsupported or malformed record")
        page, suffix = match.groups()
        if page in pages:
            raise ValueError(f"line {line_number}: duplicate page header")
        if without_free_comments(suffix).strip():
            raise ValueError(f"line {line_number}: page header has non-metadata text")
        declared = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9@])", suffix))
        pages[page] = declared
        variables = {key: value for key, value in declared.items() if value != "@"}
        current_page, last_number = page, 0
    return Document(lines[0], header[1], pages, tuple(loci))


def read_ivtff(path):
    return parse_ivtff(Path(path).read_bytes().decode("ascii"))
