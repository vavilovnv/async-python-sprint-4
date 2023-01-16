from models.links import Link as LinkModel
from models.links import LinksUsage as LinksUsageModel
from schemas.links import URLBase, ShortUrl
from .base import RepositoryDBLink


class RepositoryLink(RepositoryDBLink[LinkModel, LinksUsageModel, URLBase, ShortUrl]):
    pass


link_crud = RepositoryLink(LinkModel, LinksUsageModel)
