from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    coach = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    position = models.CharField(max_length=50, blank=True)
    shirt_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Match(models.Model):
    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="home_matches"
    )
    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="away_matches"
    )
    match_date = models.DateTimeField()
    place = models.CharField(max_length=150, blank=True)

    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"


class Goal(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="goals")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="goals")
    minute = models.IntegerField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        home_goals = self.match.goals.filter(
            player__team=self.match.home_team
        ).count()

        away_goals = self.match.goals.filter(
            player__team=self.match.away_team
        ).count()

        self.match.home_score = home_goals
        self.match.away_score = away_goals
        self.match.save()

    def __str__(self):
        return f"{self.player} - {self.minute} min"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("referee", "Sędzia"),
        ("manager", "Menadżer"),
        ("user", "Użytkownik"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class League(models.Model):
    name = models.CharField(max_length=100)
    season = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} {self.season}"


class Scheduler(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="schedules")
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name="schedule")
    round_number = models.IntegerField()
    planned_date = models.DateTimeField()

    def __str__(self):
        return f"Kolejka {self.round_number} - {self.match}"