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
        #start = (3-1)*5
        start = (self.page - 1) * self.per_page
        #end = 10+5
        end = start + self.per_page
        #items_slice[10:15]
        items = self.query[start:end]
        #total_item = 8
        total_items = len(self.query)
        #total_pages=(8+3-1)//3
        #total pages =3
        total_pages = (total_items + self.per_page - 1) // self.per_page
        return {
            "items": items,
            "current_page": self.page,
            "per_page": self.per_page,
            "total_items": total_items,
            "total_pages": total_pages,
        }
