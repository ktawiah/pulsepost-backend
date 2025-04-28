from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.posts.models import Post, Tag, Comment, Like, Status
from faker import Faker
import random

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create admin user if not exists
        admin, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write('Created admin user')

        # Create regular users
        users = []
        for i in range(5):
            user, created = User.objects.get_or_create(
                email=f'user{i}@example.com',
                defaults={
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name()
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)
        self.stdout.write('Created regular users')

        # Create tags
        tags = []
        tag_names = ['Technology', 'Science', 'Art', 'Music', 'Sports', 'Food', 'Travel']
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(
                name=name,
                defaults={'slug': name.lower()}
            )
            tags.append(tag)
        self.stdout.write('Created tags')

        # Create posts
        posts = []
        for i in range(20):
            post = Post.objects.create(
                user=random.choice(users),
                title=fake.sentence(),
                content=fake.text(),
                status=random.choice([Status.DRAFT.value, Status.PUBLISHED.value])
            )
            # Add random tags to post
            post.tags.add(*random.sample(tags, random.randint(1, 3)))
            posts.append(post)
        self.stdout.write('Created posts')

        # Create comments
        for post in posts:
            for _ in range(random.randint(0, 5)):
                comment = Comment.objects.create(
                    user=random.choice(users),
                    post=post,
                    content=fake.text(max_nb_chars=200)
                )
                # Add some replies
                if random.random() > 0.7:  # 30% chance of having replies
                    for _ in range(random.randint(1, 3)):
                        Comment.objects.create(
                            user=random.choice(users),
                            post=post,
                            content=fake.text(max_nb_chars=100),
                            parent=comment
                        )
        self.stdout.write('Created comments')

        # Create likes
        for post in posts:
            for user in random.sample(users, random.randint(0, len(users))):
                Like.objects.get_or_create(user=user, post=post)
        self.stdout.write('Created likes')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!')) 