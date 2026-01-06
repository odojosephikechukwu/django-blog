from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.db.models import Count
from django.contrib.postgres.search import SearchVector
from .forms import EmailPostForm, CommentForm, SearchForm
from taggit.models import Tag



def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    form = SearchForm()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)  # 3 posts per page

    page_number = request.GET.get('page')

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
         # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
         # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    return render(
        request,
        'blog/post/list.html',
        {
            'posts': posts,
            'page_number': page_number,
            'tag': tag,
            'form':form,
        }
    )

    
def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day)
    
    if post.tags.exists():
        similar_posts = Post.objects.filter(tags__in=post.tags.all())
    else:
        similar_posts = []
    #List of active comments for this post
    comments=post.comments.filter(active=True) #List of active comments for this post

    comment_form = CommentForm()

    new_comment = None
    
    if request.method=='POST':
            #A comment was posted
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                #Create Comment object but don't save to database yet
                new_comment = comment_form.save(commit=False)
                #Assign the current post to the comment
                new_comment.post = post
                #Save the comment to the database
                new_comment.save()
            else:
                comment_form = CommentForm()
                # List of similar posts
            post_tags_ids = post.tags.values_list('id', flat=True)
            similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                        .exclude(id=post.id)
            similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                            .order_by('-same_tags','-publish')[:4]
    return render(
        request,
        'blog/post/detail.html',
        {'post': post,
         'comments': comments,
         'new_comment':new_comment,
         'comment_form': comment_form,
         'similar_posts': similar_posts
         }
    )



def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )

            subject = f"{cd['name']} recommends you read {post.title}"
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments:\n{cd['comments']}"
            )

            send_mail(
                subject,
                message,
                cd['email'],
                [cd['to']]
            )

            sent = True
    else:
        form = EmailPostForm()

    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )


def post_search(request):
    # Initialize the form
    form = SearchForm(request.GET or None)
    query = ''
    results = []

    # Only run search if the form is valid and has a query
    if form.is_valid():
        query = form.cleaned_data['query']
        if query:  # avoid empty searches
            results = Post.published.annotate(
                search=SearchVector('title', 'body')
            ).filter(search=query)

    return render(
        request,
        'blog/search.html',  # your template
        {
            'form': form,
            'query': query,
            'results': results
        }
    )

# def post_search(request):
#     form = SearchForm()
#     query = None
#     results = []
#     if 'query' in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             results = Post.published.annotate(
#                 search=SearchVector('title', 'body'),
#             ).filter(search=query)
#     return render(request, 
#             'blog/post/search.html',
#             {'form': form,
#             'query': query,
#             'results': results})


# def post_search(request):
#     form = SearchForm(request.GET or None)
#     query = ''
#     results = []

#     if form.is_valid():
#         query = form.cleaned_data['query']
#         results = Post.objects.annotate(
#             search=SearchVector('title', 'body')
#         ).filter(search=query)

#     return render(request, 'blog/search.html', {'form': form, 'results': results, 'query': query})