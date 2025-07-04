# Generated by Django 5.2.1 on 2025-05-31 22:13

import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_usersession_ended_at_usersession_logout_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalLoginAttempt',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField()),
                ('success', models.BooleanField(default=False)),
                ('attempted_at', models.DateTimeField(blank=True, editable=False)),
                ('failure_reason', models.CharField(blank=True, max_length=100)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Intento de Login',
                'verbose_name_plural': 'historical Intentos de Login',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalUser',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(db_index=True, error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(db_index=True, max_length=254)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('profile_picture', models.TextField(blank=True, max_length=100, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('employee_id', models.CharField(blank=True, db_index=True, max_length=20, null=True)),
                ('hire_date', models.DateField(blank=True, null=True)),
                ('department', models.CharField(blank=True, max_length=100)),
                ('position', models.CharField(blank=True, max_length=100)),
                ('is_email_verified', models.BooleanField(default=False)),
                ('email_verification_token', models.CharField(blank=True, max_length=255, null=True)),
                ('password_reset_token', models.CharField(blank=True, max_length=255, null=True)),
                ('password_reset_token_created', models.DateTimeField(blank=True, null=True)),
                ('last_login_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Usuario',
                'verbose_name_plural': 'historical Usuarios',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalUserSession',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('session_key', models.CharField(db_index=True, max_length=40)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField()),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('last_activity', models.DateTimeField(blank=True, editable=False)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('logout_type', models.CharField(blank=True, choices=[('manual', 'Logout Manual'), ('expired', 'Sesión Expirada'), ('forced', 'Logout Forzado'), ('password_change', 'Cambio de Contraseña')], max_length=20, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Sesión de Usuario',
                'verbose_name_plural': 'historical Sesiones de Usuario',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
