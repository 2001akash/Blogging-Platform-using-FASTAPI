from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['blog']
posts_collection = db['posts']

# Model for Post
class Post(BaseModel):
    title: str
    content: str
    author: str

# Model for Comment
class Comment(BaseModel):
    content: str
    author: str

# Model for Like/Dislike
class LikeDislike(BaseModel):
    liked: bool
    user: str

# Post operations
class PostOperations:
    @staticmethod
    def create_post(post: Post):
        post_data = post.dict()
        post_id = posts_collection.insert_one(post_data).inserted_id
        return str(post_id)

    @staticmethod
    def get_post(post_id: str):
        post = posts_collection.find_one({"_id": ObjectId(post_id)})
        if post:
            return post
        else:
            raise HTTPException(status_code=404, detail="Post not found")

    @staticmethod
    def update_post(post_id: str, post: Post):
        post_data = post.dict()
        result = posts_collection.update_one({"_id": ObjectId(post_id)}, {"$set": post_data})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")

    @staticmethod
    def delete_post(post_id: str):
        result = posts_collection.delete_one({"_id": ObjectId(post_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")

    @staticmethod
    def add_comment(post_id: str, comment: Comment):
        comment_data = comment.dict()
        result = posts_collection.update_one({"_id": ObjectId(post_id)}, {"$push": {"comments": comment_data}})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")

    @staticmethod
    def like_dislike(post_id: str, like_dislike: LikeDislike):
        update_field = "$push" if like_dislike.liked else "$pull"
        result = posts_collection.update_one({"_id": ObjectId(post_id)}, {update_field: {"likes": like_dislike.user}})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")

# Routes for CRUD operations on posts
@app.post("/posts/")
def create_post(post: Post):
    return {"post_id": PostOperations.create_post(post)}

@app.get("/posts/{post_id}")
def read_post(post_id: str):
    return PostOperations.get_post(post_id)

@app.put("/posts/{post_id}")
def update_post(post_id: str, post: Post):
    PostOperations.update_post(post_id, post)
    return {"message": "Post updated successfully"}

@app.delete("/posts/{post_id}")
def delete_post(post_id: str):
    PostOperations.delete_post(post_id)
    return {"message": "Post deleted successfully"}

# Routes for comments and likes/dislikes
@app.post("/posts/{post_id}/comments/")
def add_comment_to_post(post_id: str, comment: Comment):
    PostOperations.add_comment(post_id, comment)
    return {"message": "Comment added successfully"}

@app.post("/posts/{post_id}/like-dislike/")
def like_dislike_post(post_id: str, like_dislike: LikeDislike):
    PostOperations.like_dislike(post_id, like_dislike)
    return {"message": "Like/Dislike updated successfully"}
