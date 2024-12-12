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
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        items = self.query[start:end]
        total_items = len(self.query)
        total_pages = (total_items + self.per_page - 1) // self.per_page
        return {
            "items": items,
            "current_page": self.page,
            "per_page": self.per_page,
            "total_items": total_items,
            "total_pages": total_pages,
        }
