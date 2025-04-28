import os
import requests
from shared import *
from utils import *

def function_fetchUserData():
    response = requests.get(
        ADDRESS
        + "/api/auth/search?apikey="
        + API_KEY
        + "&userName=&role=&"
        + PAGE_SIZE_PAGE,
        headers=headers,
    ).json()

    users = response["data"]["data"]

    for user in users:
        userName = user["userName"]
        userId = user["uuid"]
        userData[userName] = userId

    return


def function_searchUser(username):
    response = requests.get(
        ADDRESS
        + "/api/auth/search?apikey="
        + API_KEY
        + "&userName="
        + username
        + "&role=&"
        + PAGE_SIZE_PAGE,
        headers=headers,
    ).json()

    status = function_statusCheck(response)

    if status is True:
        if response["data"]["data"] and len(response["data"]["data"]) > 0:
            user_data = response["data"]["data"][0]
            data_set = {
                "status": response["status"],
                "uuid": user_data["uuid"],
                "username": user_data["userName"],
                "permission": function_permissionCheck(
                    user_data["permission"]
                ),
                "registerTime": user_data["registerTime"],
                "loginTime": user_data["loginTime"],
                "2fa": function_trueFalseJudge(user_data.get("open2FA", False)),
            }
        else:
            data_set = {
                "message": "User not found",
            }
        return data_set
    else:
        return status


def function_createUser(username: str, password: str, role: int):
    request_body = {"username": username, "password": password, "permission": role}

    response = requests.post(
        ADDRESS + "/api/auth?apikey=" + API_KEY, headers=headers, json=request_body
    ).json()

    status = function_statusCheck(response)

    if status is True:
        data_set = {
            "status": response["status"],
            "user_uuid": response["data"]["uuid"],
        }
        return data_set
    else:
        return status


def function_deleteUser(user_uuid):
    request_body = [user_uuid]

    response = requests.delete(
        ADDRESS + "/api/auth?apikey=" + API_KEY, headers=headers, json=request_body
    ).json()

    status = function_statusCheck(response)

    if status is True:
        if response["status"] is True:
            data_set = {
                "status": response["status"],
                "message": "User has been deleted",
            }
        else:
            data_set = {
                "status": response["status"],
                "message": "User has NOT been deleted",
            }
        return data_set
    else:
        return status
