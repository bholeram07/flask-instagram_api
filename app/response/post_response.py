from uuid import UUID
def post_response(posts,schema):
    post_likes = {}
    post_comments = {}
    for post in posts:
            post.like_count = post.likes.count()
            post.comment_count = post.comments.count()
            post_likes[post.id] = post.like_count
            post_comments[post.id] = post.comment_count
    serialized_post = schema.dump(posts, many=True)
    # serialized_post.pop(user)
    for post in serialized_post:
            # Assuming comment["id"] is in string format ,convert into uuid
        post_id = UUID(post["id"])
        post["likes_count"] = post_likes.get(post_id, 0)
        post["comments_count"] = post_comments.get(post_id, 0)
    return serialized_post
            
