from uuid import UUID
from app.extensions import db
from app.models.comment import Comment
from sqlalchemy import func
def comment_respose(comments,schema):
    comment_likes = {}
    for comment in comments:
            comment.likes_count = len(comment.likes)
            comment_likes[comment.id] = comment.likes_count

   

    # Get comment IDs to calculate reply counts
    comment_ids = [comment.id for comment in comments]
    #this will get the comment id and reply count on the comment
    reply_counts = (
        db.session.query(Comment.parent, func.count(
            Comment.id).label("reply_count"))
        .filter(Comment.parent.in_(comment_ids), Comment.is_deleted == False)
        .group_by(Comment.parent)
        .all()
    )
    # Map reply counts to comment IDs
    # convert into dictionary the reply_count list
    reply_count_map = {parent: count for parent, count in reply_counts}

    # Serialize comments and add reply counts
    serialized_comments = schema.dump(comments, many=True)
    for comment in serialized_comments:
        # Assuming comment["id"] is in string format ,convert into uuid
        comment_id = UUID(comment["id"])
        #get the reply count from the list reply
        comment["reply_count"] = reply_count_map.get(comment_id, 0)
        comment["likes_count"] = comment_likes.get(comment_id, 0)
    return serialized_comments

