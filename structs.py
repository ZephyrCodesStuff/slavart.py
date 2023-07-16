from typing import Any, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class BaseItem:
    duration: int
    parental_warning: bool
    maximum_channel_count: int
    id: int
    maximum_sampling_rate: float
    purchasable: bool
    purchasable_at: int
    streamable: bool
    streamable_at: int
    downloadable: bool
    displayable: bool
    sampleable: bool
    previewable: bool
    hires: bool
    hires_streamable: bool
    version: Optional[int]
    release_date_original: Optional[str]
    release_date_download: Optional[str]
    release_date_stream: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseItem':
        return cls(**data)

@dataclass
class Image:
    small: str
    thumbnail: str
    large: str
    back: str = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Image':
        return cls(**data)

@dataclass
class Label:
    name: str
    id: int
    albums_count: int
    supplier_id: int
    slug: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Label':
        return cls(**data)

@dataclass
class Genre:
    path: List[int]
    color: str
    name: str
    id: int
    slug: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Genre':
        return cls(**data)

@dataclass
class BaseArtist:
    name: str
    id: int
    roles: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseArtist':
        return cls(**data)

@dataclass
class AudioInfo:
    replaygain_track_peak: int
    replaygain_track_gain: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioInfo':
        return cls(**data)

@dataclass
class Article:
    image: str
    thumbnail: str
    root_category: int
    author: str
    abstract: str
    source: str
    title: str
    type: str
    url: str
    image_original: str
    category_id: int
    source_image: str
    id: int
    published_at: int
    category: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        return cls(**data)

@dataclass
class Artist:
    name: str
    id: int
    albums_count: Optional[int] = None
    slug: Optional[str] = None
    image: Optional[str] = None
    picture: Optional[str] = None
    roles: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Artist':
        return cls(**data)

@dataclass
class Album(BaseItem):
    maximum_bit_depth: int
    image: Image
    media_count: int
    upc: str
    released_at: int
    label: Label
    title: str
    qobuz_id: int
    popularity: int
    tracks_count: int
    genre: Genre
    url: Optional[str] = None
    artist: Optional[Artist] = None
    articles: Optional[List[Article]] = None
    artists: Optional[List[Artist]] = None


    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Album':
        data['image'] = Image.from_dict(data['image'])
        data['artist'] = Artist.from_dict(data['artist'])
        data['artists'] = [Artist.from_dict(artist) for artist in data['artists']] if data.get('artists') else None
        data['label'] = Label.from_dict(data['label'])
        data['genre'] = Genre.from_dict(data['genre'])
        return cls(**data)

@dataclass
class Track(BaseItem):
    maximum_bit_depth: int
    copyright: str
    performers: str
    audio_info: AudioInfo
    performer: BaseArtist
    isrc: str
    title: str
    track_number: int
    media_number: int
    work: Optional[str]
    album: Optional[Album] = None
    composer: Optional[BaseArtist] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Track':
        data['audio_info'] = AudioInfo.from_dict(data['audio_info'])
        data['performer'] = BaseArtist.from_dict(data['performer'])
        if data['album']:
            data['album'] = Album.from_dict(data['album'])
        return cls(**data)

    def to_string(self) -> str:
        return f"ID: {self.id:<10} Sample rate: {f'{self.maximum_sampling_rate} KHz':<10} Artist: {self.performer.name:<24} Title: {self.title:<32} Album: {(self.album.title if self.album is not None else 'N/A'):<32}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sample_rate": self.maximum_sampling_rate,
            "artist": self.performer.name,
            "album": self.album.title if self.album is not None else None,
            "title": self.title,
            "track_number": f"{self.track_number:02d}",
        }

@dataclass
class Analytics:
    search_external_id: str

    def from_dict(cls, data: Dict[str, Any]) -> 'Analytics':
        return cls(**data)

@dataclass
class BaseCollection(Generic[T]):
    limit: int
    offset: int
    analytics: Analytics
    total: int
    items: List[T]

    @classmethod
    def from_dict(cls, data: Dict[str, Any], item_type: T) -> 'BaseCollection':
        data['items'] = [item_type.from_dict(item) for item in data['items']]
        return cls(**data)

@dataclass
class Results:
    query: str
    albums: BaseCollection[Album]
    tracks: BaseCollection[Track]
    artists: BaseCollection[dict]
    playlists: BaseCollection[dict]
    focus: BaseCollection[dict]
    articles: BaseCollection[Article]
    stories: BaseCollection[dict]
    most_popular: BaseCollection[dict]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Results':
        data['albums'] = BaseCollection.from_dict(data['albums'], Album)
        data['tracks'] = BaseCollection.from_dict(data['tracks'], Track)
        data['artists'] = BaseCollection.from_dict(data['artists'], Artist)
        # data['playlists'] = BaseCollection.from_dict(data['playlists'], dict)
       #  data['focus'] = BaseCollection.from_dict(data['focus'], dict)
        data['articles'] = BaseCollection.from_dict(data['articles'], Article)
        # data['stories'] = BaseCollection.from_dict(data['stories'], dict)
        # data['most_popular'] = BaseCollection.from_dict(data['most_popular'], dict)
        return cls(**data)