from models.links import Links as LinksModel
from schemas.links import URL
from .base import RepositoryDBLink


class RepositoryLink(RepositoryDBLink[LinksModel, URL]):
    pass


link_crud = RepositoryLink(LinksModel)
