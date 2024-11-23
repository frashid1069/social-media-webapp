import requests
from service.utils.jwt_auth import create_hearders
from service.models import Node
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status

def push(author, request, data):
    follow_objects = author.followers.filter(pending='no')
    log = []
    for follow in follow_objects:
        print(follow)
        follower = follow.follower
        nodes_exists = Node.objects.filter(is_allowed=True, url=follower.host).exists()
        if nodes_exists:
            print("send to remote followers")
            node = Node.objects.get(is_allowed=True, url=follower.host)
            headers = create_hearders(node)
            try:
                response = requests.post(f"{follower.fqid}/inbox", headers=headers, json=data)
                if response.status_code == 201:
                    response_data = f"Notify {follower} in {node.url} with {response} Successfully"
                else:
                    response_data = f"Failed to notify {follower} in {node.url} with {response}"
                    
            except requests.RequestException as e:
                print(f"Error notifying {follower} in {node.url}: {e}")
                return Response(f"Error notifying {follower} in {node.url}: {e}", status=status.HTTP_400_BAD_REQUEST)
            
        elif follower.host == author.host:
            print("send to local followers")
            headers = {"Authorization": f"Bearer {request.auth}"}
            response = requests.post(f"{follower.fqid}/inbox", headers=headers, json=data)
            response_data = f"Notify {follower} in local with {response} Successfully"
        else:
            response_data = f"Error fetching from {node.url}"
        
        log.append(response_data)
    print(log)
    return log
            
