class CustomPagination:
    def __init__(self,query,page,per_page):
        self.query = query
        self.page = page
        self.per_page = per_page
    
    def paginate(self):
        start = (self.page - 1)* self.per_page
        end = start + self.per_page
        items = self.query[start:end]
        total_items = len(self.query)
        total_pages = (total_items + self.per_page - 1) // self.per_page 
        return {
            "current_page": self.page,
            "per_page": self.per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "items": items
        }
    