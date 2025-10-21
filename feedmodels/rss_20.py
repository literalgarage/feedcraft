import datetime as dt
import typing as t
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime

type Weekday = t.Literal[
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


@dataclass(frozen=True, slots=True)
class Category:
    """Represents a taxonomy element as described for channel- and item-level <category>."""

    value: str
    """Forward-slash-separated string identifying a hierarchic location in the indicated taxonomy."""

    domain: str | None = None
    """Optional string identifying the categorization taxonomy associated with this category."""


@dataclass(frozen=True, slots=True)
class Guid:
    """Globally unique identifier for an item, following the <guid> element semantics."""

    value: str
    """String that uniquely identifies the item; aggregators may use it to detect new entries."""

    is_perma_link: bool = True
    """When true, the guid is a permalink to the item; defaults to true per the specification."""


@dataclass(frozen=True, slots=True)
class Enclosure:
    """Describes a media object attached to an item via the <enclosure> element."""

    url: str
    """HTTP URL where the enclosure is located."""

    length: int
    """Size of the enclosure in bytes."""

    media_type: str
    """Standard MIME type indicating the nature of the enclosure."""

    def validate(self) -> None:
        if self.length < 0:
            raise ValueError("Enclosure length must be a non-negative byte count.")


@dataclass(frozen=True, slots=True)
class Source:
    """Identifies the channel from which an item originated, mirroring the <source> element."""

    name: str
    """Human-readable name of the source channel, derived from its <title>."""

    url: str
    """URL that links to the XMLization of the source channel."""


@dataclass(frozen=True, slots=True)
class Cloud:
    """Models the <cloud> element that advertises an rssCloud-compatible notification endpoint."""

    domain: str
    """Domain name of the web service providing rssCloud notifications."""

    port: int
    """TCP port on which the cloud service listens for subscription requests."""

    path: str
    """Request path to invoke on the cloud service when registering for updates."""

    register_procedure: str
    """Procedure name to call on the cloud service when requesting notification."""

    protocol: str
    """Protocol supported by the cloud service (HTTP-POST, XML-RPC, or SOAP 1.1)."""

    def validate(self) -> None:
        allowed_protocols = {
            "HTTP-POST",
            "http-post",
            "XML-RPC",
            "xml-rpc",
            "SOAP 1.1",
            "soap",
        }
        if self.protocol not in allowed_protocols:
            raise ValueError(
                "Cloud protocol must be one of HTTP-POST, XML-RPC, or SOAP 1.1."
            )


@dataclass(frozen=True, slots=True)
class Image:
    """Represents the <image> element that visually brands the channel."""

    url: str
    """URL of a GIF, JPEG, or PNG image that represents the channel."""

    title: str
    """Descriptive text for the image, used in the ALT attribute when rendered in HTML."""

    link: str
    """URL of the site; the image should link to this when rendered."""

    width: int = 88
    """Optional image width in pixels; defaults to 88 and must not exceed 144."""

    height: int = 31
    """Optional image height in pixels; defaults to 31 and must not exceed 400."""

    description: str | None = None
    """Optional text included in the TITLE attribute of the link formed around the image."""

    def validate(self) -> None:
        if self.width > 144:
            raise ValueError("Image width must not exceed 144 pixels.")
        if self.height > 400:
            raise ValueError("Image height must not exceed 400 pixels.")


@dataclass(frozen=True, slots=True)
class TextInput:
    """Encapsulates the <textInput> element for providing a text submission interface."""

    title: str
    """Label for the Submit button in the text input area."""

    description: str
    """Explanation of the purpose of the text input area."""

    name: str
    """Name of the text object in the input area."""

    link: str
    """URL of the CGI script that processes text input requests."""


@dataclass(frozen=True, slots=True)
class Item:
    """Represents an <item>; each item may be a story, synopsis, or complete piece of content."""

    title: str | None = None
    """Title of the item; at least one of title or description must be present."""

    link: str | None = None
    """URL of the item; may be omitted when the item is complete in itself."""

    description: str | None = None
    """Synopsis or full content of the item; entity-encoded HTML is permitted."""

    author: str | None = None
    """Email address of the author of the item."""

    categories: tuple[Category, ...] = field(default_factory=tuple)
    """Zero or more categories that classify the item; follows <category> element rules."""

    comments: str | None = None
    """URL of the comments page for the item."""

    enclosure: Enclosure | None = None
    """Description of a media object attached to the item."""

    guid: Guid | None = None
    """Globally unique identifier for the item to help aggregators avoid repeats."""

    pub_date: str | None = None
    """Publication date of the item as an RFC 822 date-time string."""

    source: Source | None = None
    """Channel from which the item originated; includes the source channel's title and URL."""

    def validate(self) -> None:
        if self.title is None and self.description is None:
            raise ValueError("RSS items require at least a title or a description.")


@dataclass(frozen=True, slots=True)
class Channel:
    """Encapsulates the required metadata and content elements of an RSS <channel>."""

    title: str
    """Name of the channel; should match the title of the corresponding website."""

    link: str
    """URL of the HTML website corresponding to the channel."""

    description: str
    """Phrase or sentence describing the channel's content."""

    language: str | None = None
    """Language code of the channel, enabling aggregators to group feeds by language."""

    copyright: str | None = None
    """Copyright notice covering the content in the channel."""

    managing_editor: str | None = None
    """Email address of the person responsible for editorial content."""

    web_master: str | None = None
    """Email address of the person responsible for technical issues relating to the channel."""

    pub_date: str | None = None
    """Publication date for the channel content, expressed as an RFC 822 string."""

    last_build_date: str | None = None
    """Date the channel content last changed, expressed as an RFC 822 string."""

    categories: tuple[Category, ...] = field(default_factory=tuple)
    """One or more categories to which the channel belongs, using <category> semantics."""

    generator: str | None = None
    """String indicating the program used to generate the channel."""

    docs: str | None = None
    """URL pointing to documentation for the format used in the RSS file."""

    cloud: Cloud | None = None
    """Optional rssCloud registration endpoint for lightweight publish-subscribe updates."""

    ttl: int | None = None
    """Time to live in minutes, hinting how long the channel may be cached before refresh."""

    image: Image | None = None
    """Optional image associated with the channel for display alongside the feed."""

    rating: str | None = None
    """PICS rating string for the channel."""

    text_input: TextInput | None = None
    """Optional text input box specification that aggregators may render with the channel."""

    skip_hours: tuple[int, ...] = field(default_factory=tuple)
    """Up to 24 GMT hours (0–23) during which aggregators may skip reading the channel."""

    skip_days: tuple[Weekday, ...] = field(default_factory=tuple)
    """Up to seven named days during which aggregators may skip reading the channel."""

    items: tuple[Item, ...] = field(default_factory=tuple)
    """Ordered collection of items contained in the channel; a channel may include any number."""

    def validate(self) -> None:
        if len(self.skip_hours) > 24:
            raise ValueError("skip_hours may contain at most 24 entries.")
        if any(hour < 0 or hour > 23 for hour in self.skip_hours):
            raise ValueError("Each skip hour must be between 0 and 23 inclusive.")
        if len(self.skip_days) > 7:
            raise ValueError(
                "skip_days may contain at most the seven days of the week."
            )
        if self.ttl is not None and self.ttl < 0:
            raise ValueError("ttl must be a non-negative number of minutes.")


@dataclass(frozen=True, slots=True)
class RssFeed:
    """Top-level representation of an RSS 2.0 document consisting of an <rss> element."""

    channel: Channel
    """The single <channel> element containing metadata and content entries."""

    version: str = "2.0"
    """Version attribute of the <rss> element; must be 2.0 for this specification."""

    def validate(self) -> None:
        if self.version != "2.0":
            raise ValueError("RSS 2.0 documents must declare version '2.0'.")


class RssDateError(ValueError):
    """Raised when an RSS date string cannot be parsed according to RFC 822 allowances."""


def parse_rfc822_date(value: str) -> dt.datetime:
    """Parse an RFC 822 date-time string as used by RSS <pubDate> and <lastBuildDate>."""

    if not value:
        raise RssDateError("RSS date strings must be non-empty.")
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError) as exc:  # raised for unparseable inputs
        raise RssDateError(f"Invalid RSS date string: {value!r}") from exc
    if parsed is None:
        raise RssDateError(f"Invalid RSS date string: {value!r}")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed


def parse_optional_rfc822_date(value: str | None) -> dt.datetime | None:
    """Parse an optional RSS date string, returning None when the input is None."""

    if value is None:
        return None
    return parse_rfc822_date(value)
