import requests

def push(author, request, data):
    follow_objects = author.followers.all()
    print(follow_objects)
    headers = {"Authorization": f"Bearer {request.auth}"}
    for follow in follow_objects:
        follower = follow.followed
        inbox_url = f'{follower.fqid}/inbox'
        try:
            response = requests.post(inbox_url, json=data, headers=headers)
            if response.status_code != 201:
                # print(f"Failed to notify {follower}: {response.content}")
                print(f"Failed to notify {follower}")
        except requests.exceptions.RequestException as e:
            print(f"Error notifying {follower}: {e}")