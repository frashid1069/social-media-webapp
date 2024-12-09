import requests
from service.utils.jwt_auth import create_hearders
from service.models import Node
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status

def push(author, request, data):
    log = []
    type = data.get('type')
    
    if type == 'post':
        follow_objects = author.followers.filter(pending='no')
        # check all followers
        for follow in follow_objects:
            print(follow)
            follower = follow.follower
            nodes_exists = Node.objects.filter(is_allowed=True, url=follower.host).exists()
            # request to remote if node exists
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
            # handle local followers
            elif follower.host == author.host:
                print("send to local followers")
                headers = {"Authorization": f"Bearer {request.auth}"}
                response = requests.post(f"{follower.fqid}/inbox", headers=headers, json=data)
                response_data = f"Notify {follower} in local with {response} Successfully"
            else:
                response_data = f"Error fetching from {follower.host}"
            
            log.append(response_data)
    
    elif type == 'comment':
        post_fqid = data.get("post")
        print(post_fqid)
        url = post_fqid.split("/posts/")[0]
        allowed_nodes = Node.objects.filter(is_allowed=True)
        matching_nodes = [node for node in allowed_nodes if url.startswith(node.url)]
        nodes_exists = bool(matching_nodes)
        # request to remote if node exists
        if nodes_exists:
            print("send to remote post owner")
            node = matching_nodes[0]
            headers = create_hearders(node)
            try:
                response = requests.post(f"{url}/inbox", headers=headers, json=data)
                if response.status_code == 201 or response.status_code == 200:
                    response_data = f"Notify {url} in {node.url} with {response} Successfully"
                else:
                    response_data = f"Failed to notify {url} in {node.url} with {response}"
                    
            except requests.RequestException as e:
                print(f"Error notifying {url} in {node.url}: {e}")
                return Response(f"Error notifying {url} in {node.url}: {e}", status=status.HTTP_400_BAD_REQUEST)
        # handle local author 
        elif author.host in post_fqid:
            print("send to local post owner")
            headers = {"Authorization": f"Bearer {request.auth}"}
            response_data = f"Notify {author} in local Successfully"
        else:
            response_data = f"Error fetching from {url}"
        
        log.append(response_data)
    
    elif type == 'like':
        object_fqid = data.get("object")
        serial = object_fqid.split('authors/')[1].split('/')[0]
        print(object_fqid, serial)
        url = object_fqid.split("/posts/")[0]
        allowed_nodes = Node.objects.filter(is_allowed=True)
        matching_nodes = [node for node in allowed_nodes if url.startswith(node.url)]
        nodes_exists = bool(matching_nodes)
        # request to remote if node exists
        if nodes_exists:
            print("send to remote post owner")
            node = node = matching_nodes[0]
            headers = create_hearders(node)
            try:
                response = requests.post(f"{node.url}authors/{serial}/inbox", headers=headers, json=data)
                if response.status_code == 201 or response.status_code == 200:
                    response_data = f"Notify {node.url}authors/{serial} in {node.url} with {response} Successfully"
                else:
                    response_data = f"Failed to notify {node.url}authors/{serial} in {node.url} with {response}"
                    
            except requests.RequestException as e:
                print(f"Error notifying {node.url}authors/{serial} in {node.url}: {e}")
                return Response(f"Error notifying {node.url}authors/{serial} in {node.url}: {e}", status=status.HTTP_400_BAD_REQUEST)
        # handle local author
        elif author.host in object_fqid:
            print("send to local post owner")
            headers = {"Authorization": f"Bearer {request.auth}"}
            response_data = f"Notify {author} in local Successfully"
        else:
            response_data = f"Error fetching from {author}"
        
        log.append(response_data)
        
        
    print(log)
    return log