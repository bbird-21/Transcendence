# Generated by Django 4.2.13 on 2024-11-25 15:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cursor_player_one', models.IntegerField()),
                ('cursor_player_two', models.IntegerField()),
                ('score_player_one', models.IntegerField()),
                ('x_ball_position', models.IntegerField()),
                ('y_ball_position', models.IntegerField()),
                ('timer', models.IntegerField()),
                ('player_one', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player_one', to=settings.AUTH_USER_MODEL)),
                ('player_two', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player_two', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
