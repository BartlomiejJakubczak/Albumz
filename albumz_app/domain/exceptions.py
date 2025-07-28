class AlbumAlreadyOnWishlistError(Exception):
    """Raised when trying to add an album to the wishlist
    that is already on wishlist.
    """

    pass


class AlbumAlreadyInCollectionError(Exception):
    """Raised when trying to add an album to the collection
    that is already in collection.
    """

    pass


class AlbumDoesNotExistError(Exception):
    """Raised when trying to remove an album that is not in current possession,
    nor on wishlist.
    """

    pass
