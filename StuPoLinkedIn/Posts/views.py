from django.shortcuts import render
from .models import Post
# Create your views here.
def index(request):
    post=Post.objects.all()[0]
    context={
        'post': post,
    }
    return render(request,'Posts/index.html',context=context)