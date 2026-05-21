from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('teams', views.TeamViewSet, basename='teams')
router.register('players', views.PlayerViewSet, basename='players')
router.register('matches', views.MatchViewSet, basename='matches')
router.register('goals', views.GoalViewSet, basename='goals')
router.register('leagues', views.LeagueViewSet, basename='leagues')
router.register('schedulers', views.SchedulerViewSet, basename='schedulers')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/login/', views.api_login),
    path('api/register/', views.api_register),
    path('api/table/', views.api_league_table),
    path('api/best-team/', views.api_best_team),
    path('api/best-player/', views.api_best_player),
    path('api/best-player-against-team/<int:team_id>/', views.api_best_player_against_team),
    path('api/add-goal/', views.api_add_goal),
]