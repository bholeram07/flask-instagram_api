class CustomPagination:
    """
    provides a pagination to the items user can adjust their page size and by providing the page size
    default page_size is 10
    """

    def __init__(self, query, page, per_page):
        self.query = query
        self.page = page
        self.per_page = per_page

    def paginate(self):
        # start = (3-1)*5
        offset = (self.page - 1) * self.per_page
        limit = self.per_page

        # If self.query is a SQLAlchemy query object, apply offset and limit
        # Ensure the offset doesn't exceed the total number of items
        total_items = len(self.query)
        if offset >= total_items:
            offset = total_items - self.per_page if total_items > 0 else 0

        if isinstance(self.query, list):
            # If it's a list, slice it
            items = self.query[offset:offset + limit]

            total_items = len(self.query)

        # Calculate total pages
        total_pages = (total_items + self.per_page - 1) // self.per_page

        # Return paginated response
        return {
            "items": items,
            "current_page": self.page,
            "per_page": self.per_page,
            "total_items": total_items,
            "total_pages": total_pages,
        }
