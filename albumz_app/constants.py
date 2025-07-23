from enum import Enum

APP_NAME = "albumz"
API_APP_NAME = "api"

TEST_PASSWORD = "testpass"

class BaseEnum(str, Enum):
    def __str__(self):
        return self.value


class URLNames(BaseEnum):
    COLLECTION = "collection"
    WISHLIST = "wishlist"
    DETAIL = "detail"
    DELETE = "delete"
    EDIT = "edit"
    MOVE_TO_COLLECTION = "move"
    ADD_TO_COLLECTION = "add_collection"
    ADD_TO_WISHLIST = "add_wishlist"

    class API(BaseEnum):
        ALBUMS = "album-list"
        DETAIL = "album-detail"


class ReverseURLNames(BaseEnum):
    COLLECTION = f"{APP_NAME}:{URLNames.COLLECTION.value}"
    WISHLIST = f"{APP_NAME}:{URLNames.WISHLIST.value}"
    DETAIL = f"{APP_NAME}:{URLNames.DETAIL.value}"
    DELETE = f"{APP_NAME}:{URLNames.DELETE.value}"
    EDIT = f"{APP_NAME}:{URLNames.EDIT.value}"
    MOVE_TO_COLLECTION = f"{APP_NAME}:{URLNames.MOVE_TO_COLLECTION.value}"
    ADD_TO_COLLECTION = f"{APP_NAME}:{URLNames.ADD_TO_COLLECTION.value}"
    ADD_TO_WISHLIST = f"{APP_NAME}:{URLNames.ADD_TO_WISHLIST.value}"

    class API(BaseEnum):
        ALBUMS = f"{API_APP_NAME}:{URLNames.API.ALBUMS.value}"
        DETAIL = f"{API_APP_NAME}:{URLNames.API.DETAIL.value}"


class ResponseStrings(BaseEnum):
    EMPTY_COLLECTION = "No albums in your collection yet."
    EMPTY_WISHLIST = "No albums on your wishlist yet."
    PUB_DATE_ERROR = "Publication date cannot be in the future."
    ALBUM_IN_COLLECTION_ERROR = "You already own this album!"
    ALBUM_ON_WISHLIST_ERROR = "You already have this album on wishlist!"
    ALBUM_DOES_NOT_EXIST_ERROR = "Album does not exist."
    MOVED_TO_COLLECTION = "Album has been moved to collection."


class TemplateContextVariables(BaseEnum):
    ALBUMS_COLLECTION = "albums_in_collection"
    ALBUMS_WISHLIST = "albums_on_wishlist"
    ALBUM = "album"
    FORM = "form"


class DirPaths(BaseEnum):
    TEMPLATES_PATH = "albumz_app/"
    FORM_PATH = f"{TEMPLATES_PATH}forms/"

    def file(self, filename):
        return f"{self.value}{filename}"