from flask_jwt_extended import get_jwt_identity,jwt_required
from app.models.user import User
from functools import wraps  # Correctly import wraps
from flask import request, jsonify
from app.models.post import Post
from app.models.comment import Comment 
global target_user
class Permission:
    @staticmethod
    @jwt_required()  # Ensure JWT is validated before getting identity
    def get_current_user_id():
        """Retrieve the current user's ID from the JWT."""
        return get_jwt_identity()
   
    @staticmethod
    def can_access_user(target_user):
        """Check if the current user can access the target user's resource."""
        print("in permission class")
        # Get user ID from JWT
        print(request.method)
        current_user_id = Permission.get_current_user_id()
        if not current_user_id:
            return False
      
        current_user = User.query.get(current_user_id)
        print("current_user")
        print(current_user)
        if target_user == current_user:
            return True

        # If the account is public, allow access
        print(target_user.is_private)
        if not target_user.is_private or current_user.is_follower(target_user):
            print("is follower or not ",current_user.is_follower(target_user))
            return True
        
        # If the current user is a follower, allow access
        # Deny access otherwise
        return False
    

    @staticmethod
    def user_permission_required(view_func):
        """Decorator to enforce user access permissions."""
        print("here in permission class")
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            # Assuming user_id is passed in the route
            data = request.json
            user_id = kwargs.get('user_id')
            post_id = data.get('post_id') or kwargs.get('post_id')
            comment_id = data.get('comment_id') or kwargs.get('comment_id')
            story_id = data.get('story_id') or kwargs.get("story_id")
            

            # current_user = User.query.get(self.current_user_id)
            # if not current_user.is_follower(target_user):
            #     return jsonify("you are not follower")
            # print("this cis the relationships",current_user.is_follower(target_user))
            # print(current_user.is_follower(target_user))
            # print(f)
           
            target_user = None
            if post_id:
                post = Post.query.filter_by(id = post_id,is_deleted = False).first()
                if not post:
                    return jsonify({"error":"Post not found"}),400
                target_user = User.query.get(post.user)
                print(target_user)
            
            if comment_id:
                comment = Comment.query.filter_by(id = comment_id, is_deleted = False).first()
                print(comment)
                print(comment_id)
                print(comment.user_id)
                if not comment:
                    return jsonify({"error" : "comment not exist"}),404
                target_user = User.query.get(comment.user_id)
                print(target_user)
            
            print(target_user)
            
        
            if not target_user:
                return jsonify({"error": "User not found"}), 404
            if target_user.is_private:
                return jsonify({"error" : "account is private"}),403
            p = Permission.can_access_user(target_user)
            print(p)

            if not Permission.can_access_user(target_user):
                return jsonify({"error": "Permission denied"}), 403
            

            # Proceed if permission is granted
            return view_func(*args, **kwargs)

        return wrapped_view  

