from flask import jsonify,request
from typing import Union

def get_limit_offset()->Union[int,int,int]:
    page:int = request.args.get("page", 1, type=int)
    page_size:int = request.args.get("page_size", 5, type=int)
    offset:int = (page - 1)*page_size
    return page,offset,page_size
