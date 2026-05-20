from django.db import models
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Team, Player, Match, Goal, UserProfile
from .serializers import (
    TeamSerializer,
    PlayerSerializer,
    MatchSerializer,
    GoalSerializer,
    UserProfileSerializer
)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

def calculate_league_table():
    teams = Team.objects.all()
    table = []

    for team in teams:
        matches = Match.objects.filter(finished=True).filter(
            models.Q(home_team=team) | models.Q(away_team=team)
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


@api_view(['GET'])
def api_league_table(request):
    return Response(calculate_league_table())


@api_view(['GET'])
def api_best_team(request):
    table = calculate_league_table()

    if not table:
        return Response({
            "message": "Brak drużyn"
        })

    return Response(table[0])


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


@api_view(['GET'])
def api_best_player_against_team(request, team_id):

    try:
        selected_team = Team.objects.get(id=team_id)

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