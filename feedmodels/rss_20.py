import datetime as dt
import typing as t
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup, FeatureNotFound
from bs4.element import Tag

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


class RssParseError(ValueError):
    """Raised when an RSS document cannot be parsed into the expected RSS 2.0 structure."""


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


def parse_rss(rss: str) -> RssFeed:
    """Parse an RSS 2.0 document using BeautifulSoup with defensive input checks."""

    if not isinstance(rss, str):
        raise TypeError("RSS payload must be provided as a string.")

    stripped = rss.lstrip()
    if not stripped:
        raise RssParseError("Empty RSS payload provided.")

    upper = stripped.upper()
    if "<!DOCTYPE" in upper:
        raise RssParseError(
            "Refusing to process RSS feeds that declare a document type."
        )
    if "<!ENTITY" in upper:
        raise RssParseError(
            "Refusing to process RSS feeds that declare custom entities."
        )

    try:
        soup = BeautifulSoup(rss, "xml")
    except FeatureNotFound:
        soup = BeautifulSoup(rss, "html.parser")
    except Exception as exc:  # pragma: no cover - BeautifulSoup rarely raises
        raise RssParseError("Unable to parse RSS XML document.") from exc

    rss_tag = soup.find("rss")
    if rss_tag is None:
        raise RssParseError("Missing <rss> root element.")

    version_attr = _get_attr(rss_tag, "version")
    version = version_attr if version_attr else "2.0"

    channel_tag = _find_direct_child(rss_tag, "channel")
    if channel_tag is None:
        raise RssParseError("Missing <channel> element inside <rss>.")

    channel = Channel(
        title=_require_child_text(channel_tag, "title"),
        link=_require_child_text(channel_tag, "link"),
        description=_require_child_text(channel_tag, "description"),
        language=_optional_child_text(channel_tag, "language"),
        copyright=_optional_child_text(channel_tag, "copyright"),
        managing_editor=_optional_child_text(channel_tag, "managingEditor"),
        web_master=_optional_child_text(channel_tag, "webMaster"),
        pub_date=_optional_child_text(channel_tag, "pubDate"),
        last_build_date=_optional_child_text(channel_tag, "lastBuildDate"),
        categories=_parse_categories(channel_tag),
        generator=_optional_child_text(channel_tag, "generator"),
        docs=_optional_child_text(channel_tag, "docs"),
        cloud=_parse_cloud(channel_tag),
        ttl=_parse_int(_optional_child_text(channel_tag, "ttl")),
        image=_parse_image(channel_tag),
        rating=_optional_child_text(channel_tag, "rating"),
        text_input=_parse_text_input(channel_tag),
        skip_hours=_parse_skip_hours(channel_tag),
        skip_days=_parse_skip_days(channel_tag),
        items=_parse_items(channel_tag),
    )

    feed = RssFeed(channel=channel, version=version)
    channel.validate()
    for item in channel.items:
        item.validate()
    feed.validate()
    return feed


def _local_name(tag_name: str) -> str:
    return tag_name.split(":", 1)[-1]


def _normalize_attr(value: t.Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except Exception:
            return value.decode("utf-8", "ignore")
    if isinstance(value, (list, tuple)):
        for item in value:
            text = _normalize_attr(item)
            if text is not None:
                return text
        return None
    return str(value)


def _get_attr(tag: Tag, name: str, *, strip: bool = True) -> str | None:
    raw = tag.attrs.get(name)
    value = _normalize_attr(raw)
    if value is None:
        return None
    return value.strip() if strip else value


def _find_direct_child(parent: Tag, name: str) -> Tag | None:
    for child in parent.find_all(True, recursive=False):
        if _local_name(child.name) == name:
            return child
    return None


def _find_children(parent: Tag, name: str) -> list[Tag]:
    matches: list[Tag] = []
    for child in parent.find_all(True, recursive=False):
        if _local_name(child.name) == name:
            matches.append(child)
    return matches


def _get_text(node, *, strip: bool = True) -> str | None:
    if node is None:
        return None
    if node.string is not None:
        text = node.string
    else:
        text = node.get_text()
    if text is None:
        return None
    return text.strip() if strip else text


def _require_child_text(parent, name: str) -> str:
    child = _find_direct_child(parent, name)
    value = _get_text(child)
    if value is None or not value:
        raise RssParseError(f"Missing required <{name}> element in RSS channel.")
    return value


def _optional_child_text(parent, name: str) -> str | None:
    child = _find_direct_child(parent, name)
    return _get_text(child)


def _parse_categories(parent) -> tuple[Category, ...]:
    categories: list[Category] = []
    for cat in _find_children(parent, "category"):
        value = _get_text(cat)
        if not value:
            continue
        domain = _get_attr(cat, "domain")
        categories.append(Category(value=value, domain=domain))
    return tuple(categories)


def _parse_cloud(parent) -> Cloud | None:
    cloud_tag = _find_direct_child(parent, "cloud")
    if cloud_tag is None:
        return None
    domain = _get_attr(cloud_tag, "domain")
    port_text = _get_attr(cloud_tag, "port")
    path = _get_attr(cloud_tag, "path")
    register_procedure = _get_attr(cloud_tag, "registerProcedure")
    protocol = _get_attr(cloud_tag, "protocol")
    if (
        domain is None
        or port_text is None
        or path is None
        or register_procedure is None
        or protocol is None
    ):
        return None
    try:
        port_int = int(port_text)
    except ValueError:
        return None
    cloud = Cloud(
        domain=domain,
        port=port_int,
        path=path,
        register_procedure=register_procedure,
        protocol=protocol,
    )
    try:
        cloud.validate()
    except ValueError:
        return None
    return cloud


def _parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


def _parse_image(parent) -> Image | None:
    image_tag = _find_direct_child(parent, "image")
    if image_tag is None:
        return None
    url = _optional_child_text(image_tag, "url")
    title = _optional_child_text(image_tag, "title")
    link = _optional_child_text(image_tag, "link")
    if url is None or title is None or link is None:
        return None
    width = _parse_int(_optional_child_text(image_tag, "width")) or 88
    height = _parse_int(_optional_child_text(image_tag, "height")) or 31
    description = _optional_child_text(image_tag, "description")
    image = Image(
        url=url,
        title=title,
        link=link,
        width=width,
        height=height,
        description=description,
    )
    try:
        image.validate()
    except ValueError:
        return None
    return image


def _parse_text_input(parent) -> TextInput | None:
    text_input_tag = _find_direct_child(parent, "textInput")
    if text_input_tag is None:
        return None
    title = _optional_child_text(text_input_tag, "title")
    description = _optional_child_text(text_input_tag, "description")
    name = _optional_child_text(text_input_tag, "name")
    link = _optional_child_text(text_input_tag, "link")
    if title is None or description is None or name is None or link is None:
        return None
    return TextInput(title=title, description=description, name=name, link=link)


def _parse_skip_hours(parent) -> tuple[int, ...]:
    skip_hours_tag = _find_direct_child(parent, "skipHours")
    if skip_hours_tag is None:
        return tuple()
    hours: list[int] = []
    for hour_tag in _find_children(skip_hours_tag, "hour"):
        value = _parse_int(_get_text(hour_tag))
        if value is None or not 0 <= value <= 23:
            continue
        hours.append(value)
    return tuple(hours)


def _parse_skip_days(parent) -> tuple[Weekday, ...]:
    skip_days_tag = _find_direct_child(parent, "skipDays")
    if skip_days_tag is None:
        return tuple()
    valid_days: set[str] = set(t.get_args(Weekday))
    days: list[Weekday] = []
    for day_tag in _find_children(skip_days_tag, "day"):
        value = _get_text(day_tag)
        if not value:
            continue
        normalized = value.strip().capitalize()
        if normalized in valid_days:
            days.append(t.cast(Weekday, normalized))
    return tuple(days)


def _parse_items(parent) -> tuple[Item, ...]:
    items: list[Item] = []
    for item_tag in _find_children(parent, "item"):
        title = _optional_child_text(item_tag, "title")
        link = _optional_child_text(item_tag, "link")
        description = _optional_child_text(item_tag, "description")
        author = _optional_child_text(item_tag, "author")
        comments = _optional_child_text(item_tag, "comments")
        pub_date = _optional_child_text(item_tag, "pubDate")
        guid = _parse_guid(item_tag)
        enclosure = _parse_enclosure(item_tag)
        source = _parse_source(item_tag)
        categories = _parse_categories(item_tag)

        if title is None and description is None:
            continue

        items.append(
            Item(
                title=title,
                link=link,
                description=description,
                author=author,
                categories=categories,
                comments=comments,
                enclosure=enclosure,
                guid=guid,
                pub_date=pub_date,
                source=source,
            )
        )
    return tuple(items)


def _parse_guid(parent) -> Guid | None:
    guid_tag = _find_direct_child(parent, "guid")
    if guid_tag is None:
        return None
    value = _get_text(guid_tag)
    if not value:
        return None
    attr = _get_attr(guid_tag, "isPermaLink")
    if attr is None:
        is_permalink = True
    else:
        attr_lower = attr.lower()
        if attr_lower in {"true", "1", "yes"}:
            is_permalink = True
        elif attr_lower in {"false", "0", "no"}:
            is_permalink = False
        else:
            is_permalink = True
    return Guid(value=value, is_perma_link=is_permalink)


def _parse_enclosure(parent) -> Enclosure | None:
    enclosure_tag = _find_direct_child(parent, "enclosure")
    if enclosure_tag is None:
        return None
    url = _get_attr(enclosure_tag, "url")
    length_text = _get_attr(enclosure_tag, "length")
    media_type = _get_attr(enclosure_tag, "type")
    if url is None or length_text is None or media_type is None:
        return None
    try:
        length_int = int(length_text)
    except ValueError:
        return None
    enclosure = Enclosure(url=url, length=length_int, media_type=media_type)
    try:
        enclosure.validate()
    except ValueError:
        return None
    return enclosure


def _parse_source(parent) -> Source | None:
    source_tag = _find_direct_child(parent, "source")
    if source_tag is None:
        return None
    url = _get_attr(source_tag, "url")
    name = _get_text(source_tag)
    if not url or not name:
        return None
    return Source(name=name, url=url)
