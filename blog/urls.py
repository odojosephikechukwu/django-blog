from django.urls import re_path, path
from . import views
from .feeds import LatestPostsFeed

app_name = 'blog'

urlpatterns = [
    # 🏠 Home page (Post List)
    path('', views.post_list, name='home'),

    # 📄 Post detail (date-based URL)
    re_path(
        r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<post>[-\w]+)/$',
        views.post_detail,
        name='post_detail'
    ),

    # 🔗 Share post
    path('<int:post_id>/share/', views.post_share, name='post_share'),

    # 🏷 Posts by tag
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),

    # 📡 RSS feed
    path('feed/', LatestPostsFeed(), name='post_feed'),

    # 🔍 Search
    path('search/', views.post_search, name='post_search'),
]

# urlpatterns = [    
#     re_path(r'^$', views.post_list, name='post_list'),
#     re_path(
#         r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<post>[-\w]+)/$',
#         views.post_detail,
#         name='post_detail'
#     ),
#     path(
#         '<int:post_id>/share/',
#         views.post_share,
#         name='blog_share'
#     ),
#     path('tag/<slug:tag_slug>/',
#      views.post_list, name='post_list_by_tag'),
    
#     path('feed/', LatestPostsFeed(), name='post_feed'),

#     path('search/', views.post_search, name='post_search'),
# ]
