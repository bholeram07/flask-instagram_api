from flask import request, jsonify
from app.custom_pagination import CustomPagination


def paginate_and_serialize(queryset, schema = None,extra_fields =None):
    """
    Paginate and serialize a queryset.
    
    :param queryset: The data to be paginated (e.g., SQLAlchemy query or list).
    :param schema: Marshmallow schema to serialize the paginated items.
    :return: JSON response with paginated and serialized data.
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    paginator = CustomPagination(queryset, page, per_page)
    paginated_data = paginator.paginate()
    paginated_data["items"] = schema.dump(paginated_data["items"], many=True)
    
    #if extra field is provided in the response
    if extra_fields:
        paginated_data.update(extra_fields)

    return jsonify(paginated_data), 200
