from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from uuid import uuid4
from django.utils.text import slugify
from django.utils import timezone

class UserManager(BaseUserManager):
    
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        if not password:
            raise ValueError("Password is not provided")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        return self._create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')],
        default='Nam'
    )
    city = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    ward = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=255, blank=True)
    university = models.CharField(max_length=255, blank=True)
    major = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    facebook = models.URLField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    joined_date = models.DateTimeField(default=timezone.now)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.name or self.email
    

class TopicListen(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='image/',blank=True, null=True)
    lessons = models.IntegerField(default=0)
    levels = models.CharField(
        max_length=10,
        choices=[
            ('A1-C1','A1-C1'),
            ('A1-B1','A1-B1'),
            ('A2-C1','A2-C1'),
            ('B1-C2','B1-C2'),
            ('A1','A1'),
        ],
        default='A1'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Section(models.Model):
    title = models.CharField(max_length=150)
    position = models.PositiveIntegerField(default=1)
    topic = models.ForeignKey(TopicListen, on_delete=models.CASCADE, related_name='sections')

    def __str__(self):
        return self.title
    
class Subtopic(models.Model):
    title = models.CharField(max_length=150)
    level = models.CharField(
        max_length=20,
        choices=[('A1', 'A1'), ('A2', 'A2'), ('B1', 'B1'), ('B2', 'B2'), ('C1', 'C1')],
        default='A1'
    )
    slug = models.SlugField(unique=True, blank=True)
    num_part = models.IntegerField(default=0)
    full_textkey = models.TextField(blank=True)
    full_audioSrc = models.URLField()
    topic = models.ForeignKey(TopicListen, on_delete=models.CASCADE, related_name='topics', null=True, blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='subtopics', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class AudioExercise(models.Model):
    audioSrc = models.URLField()
    correct_text = models.TextField()
    position = models.PositiveIntegerField(default=1)
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE, related_name='exercises')
    timeStart = models.FloatField(null=True, blank=True)
    timeEnd = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.subtopic.title

# Chủ đề hệ thống (backup)
class TopicVocab(models.Model):
    topic = models.CharField(max_length=100)
    english = models.CharField(max_length=100, blank=True, null=True)
    ipa = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    vietnamese = models.CharField(max_length=100, blank=True, null=True)
    synced = models.BooleanField(default=True)

    def __str__(self):
        return self.topic

class Word(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="words")
    word = models.CharField(max_length=100)
    definition = models.TextField(blank=True)
    example = models.TextField(blank=True)
    topic = models.CharField(max_length=100, blank=True, null=True)
    is_learned = models.BooleanField(default=False)
    synced = models.BooleanField(default=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.word


