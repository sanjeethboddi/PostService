from fastapi import APIRouter, Body, Request, Response, HTTPException, status, File, UploadFile

from fastapi.encoders import jsonable_encoder
from typing import List

from models import Post, UpdatePostModel
import uuid
from dotenv import dotenv_values
import os
import requests

config = dotenv_values(".env")

router = APIRouter()

DB = "posts"
IMAGE_FOLDER = config["IMAGE_DIR"]


@router.post("/addPost/{token}", response_description="Create a new post", status_code=status.HTTP_201_CREATED)
def addPost(token:str, request:Request, response:Response, title:str, file: UploadFile = File(...)):
    resp =  requests.post(request.app.auth_service+f"/verify/{token}")
    if  resp.status_code != 200 :
        raise HTTPException(status_code=401, detail="Unauthorized")
    userID = resp.json()["username"]
    try:
        contents = file.file.read()
        
        if file.filename.endswith(".jpg") or file.filename.endswith(".png"):
            # TODO: Do some image processing  & upload to S3
            random_filename = str(uuid.uuid4())
            file_path = os.path.join(os.path.abspath(IMAGE_FOLDER),random_filename + ".png")
            with open(file_path, 'wb') as f:
                f.write(contents)
            post = Post(userID= userID, title=title, file=random_filename)
            post = jsonable_encoder(post)
            mongo_response = request.app.database[DB].insert_one(post)
            postID =  str(mongo_response.inserted_id)
            requests.patch(request.app.feed_service+f"/updateFeedDataForFollowers/{userID}/{token}", json={"postID":postID})
            # response.status_code = status.HTTP_201_CREATED
            return {"postID": str(mongo_response.inserted_id)}
        else:
            # response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "File type not supported"}
        
    except Exception as e:
        # response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}, status: {title}"}

@router.delete("/deletePost/{token}", response_description="Delete a post")
def deletePost(token:str, postID:str, request: Request, response:Response):
    post = request.app.database[DB].find_one({"_id": postID})

    resp =  requests.post(request.app.auth_service+f"/verify/{token}")
    if  resp.status_code != 200 or resp.json()["username"] != post["userID"]:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        mongo_response = request.app.database[DB].delete_one({"_id": postID})
        if mongo_response.deleted_count == 1:
            response.status_code = status.HTTP_204_NO_CONTENT
            return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile with ID {id} not found")

@router.put("/updatePost/{token}")
def updatePost(postID: str, title: str, request: Request):
    request.app.database[DB].update_one({"_id": postID},{"$set" :{"title": title}})
    return {"message": "Successfully updated post"}

@router.get("/getPost", response_model = Post)
def getPost(postID: str, request: Request):
    post = request.app.database[DB].find_one({"_id": postID})
    return post

@router.post("/getPosts", response_model = List[Post])
def getPosts(postIDs: List[str], request: Request, response:Response):
    posts = list()
    for id in postIDs:
        post = request.app.database[DB].find_one({"_id": id})
        posts.append(post)
    return posts

@router.get("/getAllPostIDsByUser")
def getAllPostIDsByUser(userID: str, request: Request):
    response =  request.app.database[DB].find({"userID": userID})
    return [i for i in response]

@router.get("/getAllPostIDsByUserAfterDate")
def getAllPostIDsByUserAfterDate(userID: str, date: str, request: Request):
    response = request.app.database[DB].find({"userID": userID, "date": {"$gt": date}})
    return [i for i in response]

@router.get("/getPostImage")
def getPostImage(postID: str, request: Request):
    post = request.app.database[DB].find_one({"_id": postID})
    with open(os.path.join(os.path.abspath(IMAGE_FOLDER),post["file"] + ".png"), 'rb') as f:
        return Response(content=f.read(), media_type="image/png")

# @router.get("/getPostImages")
# def getPostImages(postIDs: List[str], request: Request):
#     posts = list()
#     for id in postIDs:
#         post = request.app.database[DB].find
