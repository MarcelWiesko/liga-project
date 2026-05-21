from django.db import models
from django.contrib.auth import authenticate

from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny
)
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import (
    Team,
    Player,
    Match,
    Goal,
    League,
    Scheduler
)

from .serializers import (
    TeamSerializer,
    PlayerSerializer,
    MatchSerializer,
    GoalSerializer,
    LeagueSerializer,
    SchedulerSerializer
)


# =========================
# VIEWSETS
# =========================

class TeamViewSet(viewsets.ModelViewSet):

    serializer_class = TeamSerializer

    def get_queryset(self):

        queryset = Team.objects.all()

        league_id = self.request.query_params.get('league_id')

        if league_id:
            queryset = queryset.filter(
                league_id=league_id
            )

        return queryset


class PlayerViewSet(viewsets.ModelViewSet):

    serializer_class = PlayerSerializer

    def get_queryset(self):

        queryset = Player.objects.all()

        league_id = self.request.query_params.get('league_id')

        if league_id:
            queryset = queryset.filter(
                team__league_id=league_id
            )

        return queryset

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer


class LeagueViewSet(viewsets.ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer


class SchedulerViewSet(viewsets.ModelViewSet):
    queryset = Scheduler.objects.all()
    serializer_class = SchedulerSerializer


# =========================
# LOGIN
# =========================

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):

    username = request.data.get("username", "").strip()
    password = request.data.get("password", "")

    user = authenticate(
        username=username,
        password=password
    )

    if user is None:
        return Response({
            "success": False,
            "message": "Nieprawidłowy login lub hasło"
        }, status=401)

    token, created = Token.objects.get_or_create(user=user)

    role = "user"

    if hasattr(user, "userprofile"):
        role = user.userprofile.role

    return Response({
        "success": True,
        "token": token.key,
        "username": user.username,
        "role": role
    })


# =========================
# TABELA LIGOWA
# =========================

def calculate_league_table(league_id=None):

    teams = Team.objects.all()
    table = []

    for team in teams:

        matches = Match.objects.filter(
            finished=True
        ).filter(
            models.Q(home_team=team) |
            models.Q(away_team=team)
        )

        if league_id:
            matches = matches.filter(
                schedule__league_id=league_id
            )

        points = 0
        wins = 0
        draws = 0
        losses = 0

        goals_for = 0
        goals_against = 0

        for match in matches:

            if match.home_team == team:
                gf = match.home_score
                ga = match.away_score
            else:
                gf = match.away_score
                ga = match.home_score

            goals_for += gf
            goals_against += ga

            if gf > ga:
                wins += 1
                points += 3

            elif gf == ga:
                draws += 1
                points += 1

            else:
                losses += 1

        table.append({
            "team_id": team.id,
            "team": team.name,
            "points": points,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": goals_for - goals_against,
        })

    return sorted(
        table,
        key=lambda x: (
            x["points"],
            x["goal_difference"],
            x["goals_for"]
        ),
        reverse=True
    )


# =========================
# API TABLE
# =========================

@api_view(['GET'])
def api_league_table(request):

    league_id = request.GET.get("league_id")

    return Response(
        calculate_league_table(league_id)
    )


# =========================
# BEST TEAM
# =========================

@api_view(['GET'])
def api_best_team(request):

    league_id = request.GET.get("league_id")

    table = calculate_league_table(
        league_id
    )

    if not table:
        return Response({
            "message": "Brak drużyn"
        })

    return Response(table[0])


# =========================
# BEST PLAYER
# =========================

@api_view(['GET'])
def api_best_player(request):

    players = Player.objects.all()

    ranking = []

    for player in players:

        goals_count = Goal.objects.filter(
            player=player
        ).count()

        ranking.append({
            "player_id": player.id,
            "player": f"{player.first_name} {player.last_name}",
            "team": player.team.name,
            "goals": goals_count,
        })

    ranking = sorted(
        ranking,
        key=lambda x: x["goals"],
        reverse=True
    )

    if not ranking:
        return Response({
            "message": "Brak zawodników"
        })

    return Response(ranking[0])


# =========================
# BEST PLAYER AGAINST TEAM
# =========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_best_player_against_team(request, team_id):

    if request.user.userprofile.role != "manager":
        return Response({
            "message": "Brak uprawnień"
        }, status=403)

    try:
        selected_team = Team.objects.get(
            id=team_id
        )

    except Team.DoesNotExist:
        return Response({
            "message": "Nie znaleziono drużyny"
        }, status=404)

    goals = Goal.objects.filter(
        models.Q(match__home_team=selected_team) |
        models.Q(match__away_team=selected_team)
    ).exclude(
        player__team=selected_team
    )

    ranking = {}

    for goal in goals:

        player = goal.player

        if player.id not in ranking:

            ranking[player.id] = {
                "player_id": player.id,
                "player": f"{player.first_name} {player.last_name}",
                "team": player.team.name,
                "against_team": selected_team.name,
                "goals_against_team": 0,
            }

        ranking[player.id]["goals_against_team"] += 1

    result = sorted(
        ranking.values(),
        key=lambda x: x["goals_against_team"],
        reverse=True
    )

    if not result:
        return Response({
            "message": "Brak goli przeciw tej drużynie"
        })

    return Response(result[0])


# =========================
# ADD GOAL
# =========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_add_goal(request):

    if request.user.userprofile.role != "referee":
        return Response({
            "message": "Brak uprawnień"
        }, status=403)

    match_id = request.data.get("match")
    player_id = request.data.get("player")
    minute = request.data.get("minute")

    goal = Goal.objects.create(
        match_id=match_id,
        player_id=player_id,
        minute=minute
    )

    match = Match.objects.get(id=match_id)

    if goal.player.team == match.home_team:
        match.home_score += 1
    else:
        match.away_score += 1

    match.save()

    return Response({
        "message": "Gol dodany",
        "goal_id": goal.id
    })