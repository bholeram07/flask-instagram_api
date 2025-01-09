from flask import request, jsonify
from app.custom_pagination import CustomPagination
from typing import Optional


def paginate_and_serialize(queryset:str, page:int, per_page:int, schema=None, **extra_fields)->dict:
    """
    Paginate and serialize a queryset.

    :param queryset: The data to be paginated (e.g., SQLAlchemy query or list).
    :param schema: Marshmallow schema to serialize the paginated items.
    :return: JSON response with paginated and serialized data.
    """
    paginator = CustomPagination(queryset, page, per_page)
    paginated_data:dict = paginator.paginate()
    if extra_fields:
        paginated_data.update(extra_fields)
    if schema:
        paginated_data["items"] = schema.dump(
            paginated_data["items"], many=True)

    # if extra field is provided in the response
   
    # return the json data
    return jsonify(paginated_data)
