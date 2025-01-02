from flask import jsonify,request

def get_limit_offset():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 5, type=int)
    offset = (page - 1)*page_size
    return page,offset,page_size
