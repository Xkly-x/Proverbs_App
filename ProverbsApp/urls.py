from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),

    path('proverb/<int:proverb_id>/', views.proverb_detail, name='proverb_detail'),
    path('like/<int:pk>/', views.toggle_like, name='toggle_like'),
    path('proverb/<int:proverb_id>/comment/', views.add_comment, name='add_comment'),
    path('submit-proverb/', views.submit_proverb, name='submit_proverb'),

    path('quiz/', views.quiz_view, name='quiz'),
    path('quiz/answer/', views.quiz_answer, name='quiz_answer'),
    path('quiz/question/', views.get_question),
    path('quiz/answer/', views.check_answer),

    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='ProverbsApp/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile_view, name='profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('profile/<int:user_id>/', views.public_profile_view, name='public_profile'),
]