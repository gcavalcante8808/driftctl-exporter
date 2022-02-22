from collections import Counter
from dataclasses import dataclass, asdict, field, fields
from urllib.parse import urlparse


@dataclass
class Rfc1808Url:
    scheme: str
    netloc: str
    path: str

    @staticmethod
    def from_url(url):
        parsed_url = urlparse(url)
        return Rfc1808Url(scheme=parsed_url.scheme, netloc=parsed_url.netloc, path=parsed_url.path)

    def validate(self):
        return all([self.scheme, self.netloc, self.path])

    def __post_init__(self):
        if not self.validate():
            raise ValueError()

        self.path = self.path.lstrip('/')


@dataclass
class DriftOutput:
    total_resources: int
    total_changed: int
    total_unmanaged: int
    total_missing: int
    total_managed: int
    coverage: int
    managed_items: set = field(default_factory=set)
    unmanaged_items: set = field(default_factory=set)
    missing_items: set = field(default_factory=set)
    differences_items: set = field(default_factory=set)

    @staticmethod
    def from_json(content):
        summary = content['summary']

        return DriftOutput(**{
            "total_resources": summary.get("total_resources"),
            "total_changed": summary.get("total_changed"),
            "total_unmanaged": summary.get("total_unmanaged"),
            "total_missing": summary.get("total_missing"),
            "total_managed": summary.get("total_managed"),
            "coverage": content.get("coverage"),
            "managed_items": content['managed'] if summary.get("total_managed") else set(),
            "unmanaged_items": content['unmanaged'] if summary.get("total_unmanaged") else set(),
            "missing_items": content['missing'] if summary.get("total_missing") else set(),
            "differences_items": content['differences'] if summary.get("total_changed") else set(),
        })

    def as_dict(self):
        return asdict(self)

    @property
    def integer_attributes_suitable_for_metrics(self):
        return [field.name for field in fields(self) if field.type == int]

    @property
    def counter_attributes_suitable_for_metrics(self):
        return [
            'managed_items_count_by_type',
            'unmanaged_items_count_by_type',
            'missing_items_count_by_type',
            'changed_items_count_by_type'
        ]

    @property
    def managed_items_count_by_type(self):
        return Counter([item['type'] for item in self.managed_items])

    @property
    def unmanaged_items_count_by_type(self):
        return Counter([item['type'] for item in self.unmanaged_items])

    @property
    def missing_items_count_by_type(self):
        return Counter([item['type'] for item in self.missing_items])

    @property
    def changed_items_count_by_type(self):
        return Counter([item['res']['type'] for item in self.differences_items])
