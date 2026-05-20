from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('teams', views.TeamViewSet)
router.register('players', views.PlayerViewSet)
router.register('matches', views.MatchViewSet)
router.register('goals', views.GoalViewSet)
#router.register('profiles', views.UserProfileViewSet)

urlpatterns = [

    path('api/', include(router.urls)),
    path('api/table/', views.api_league_table, name='api_league_table'),
    path('api/best-team/', views.api_best_team, name='api_best_team'),
    path('api/best-player/', views.api_best_player, name='api_best_player'),
    path(
        'api/best-player-against-team/<int:team_id>/',
        views.api_best_player_against_team,
        name='api_best_player_against_team'
    ),
]