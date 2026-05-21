from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Team, Player, Match, Goal, UserProfile, League, Scheduler

admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(Goal)
admin.site.register(UserProfile)
admin.site.register(League)
admin.site.register(Scheduler)