from service.models import Follow

def check_friend(author1, author2):
    follow1 = Follow.objects.filter(follower=author1, followed=author2, pending='no').exists()
    follow2 = Follow.objects.filter(follower=author2, followed=author1, pending='no').exists()
    
    return follow1 and follow2