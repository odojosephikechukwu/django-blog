from django import template
from ..models import Post
from django.contrib.postgres.search import SearchVector
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

# To count and display the number of blogs 
@register.simple_tag
def total_posts():
    return Post.published.count()

# Extract the most commented Post
@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments')[:count]

# This is to display the latest posts
@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}

# Markdown for mockup texts
@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))


@register.simple_tag
def search_posts(query):
    if not query:
        return Post.objects.none()
    return Post.objects.annotate(
        search=SearchVector('title', 'body'),
    ).filter(search=query)