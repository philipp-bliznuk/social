import random
from configparser import ConfigParser

from faker import Faker
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APIClient
from django.core.management.base import BaseCommand


faker = Faker()


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings.HUNTER_ENABLED = False
        settings.CLEARBIT_ENABLED = False
        config = ConfigParser()
        config.read('bot.ini')
        self.users_count = int(config.get('settings', 'number_of_users'))
        self.max_posts = int(config.get('settings', 'max_posts_per_user'))
        self.max_likes = int(config.get('settings', 'max_likes_per_user'))
        self.client = APIClient()

    def login(self, email, password):
        auth_response = self.client.post(
            reverse('login'), {'email': email, 'password': password}
        )
        token = auth_response.json().get('token')
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(token))

    def signup_users_and_create_posts(self):
        for i in range(self.users_count):
            email, password = faker.email(), faker.password(length=8)
            payload = {
                'email': email,
                'full_name': faker.name(),
                'password': password
            }
            response = self.client.post(reverse('user-list'), payload, format='json')

            if response.status_code == 201:
                self.stdout.write(self.style.ERROR('Registered new user: {}'.format(email)))
                self.login(email, password)
                author = response.json().get('id')

                for i in range(random.randint(1, self.max_posts)):
                    post_title = faker.sentence()
                    post_payload = {
                        'author': author,
                        'title': post_title,
                        'text': faker.text()
                    }
                    post_response = self.client.post(
                        reverse('post-list'), post_payload, format='json'
                    )

                    if post_response.status_code == 201:
                        self.stdout.write(
                            self.style.SUCCESS(
                                '\tUser {} just posted new headline: {}'.format(email, post_title)
                            )
                        )

    def like_activity(self):
        active_users = self.client.get(reverse('user-get-most-active-users')).json()
        active_users = {
            user_id: user_data for user_id, user_data in active_users.items()
            if user_data.get('likes') < self.max_likes
        }

        for user_id, user_data in active_users.items():
            posts_to_like = self.client.post(
                reverse('post-get-posts-by-other-authors'), {'author_id': user_id}
            ).json()
            random.shuffle(posts_to_like)

            for post_data in posts_to_like[:self.max_likes - user_data.get('likes')]:
                like_response = self.client.post(
                    reverse('user-like', kwargs={'pk': user_id}),
                    {'post_id': post_data.get('id')}
                )

                if like_response.status_code == 200:
                    self.stdout.write(
                        self.style.SUCCESS(
                            'User {} liked {} post'.format(
                                user_data.get('email'), post_data.get('title')
                            )
                        )
                    )

    def handle(self, *args, **options):
        self.signup_users_and_create_posts()
        self.stdout.write(self.style.SUCCESS('{:*^30}'.format('LIKES TIME')))
        self.like_activity()
