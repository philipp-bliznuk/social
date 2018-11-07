Project setup
-------------

```bash
$ pip3 install -r requirements.txt
$ ./manage.py migrate
$ ./manage.py loaddata initial_data
$ ./manage.py runserver
```

Create `HUNTER_API_KEY` and `CLEARBIT_API_KEY` environment variables with corresponding API keys.

Endpoints
---------


* login/ 
  * POST - Request with credentials in json ```{"email": "email@example.com", "password": "secret123"}```. Authenticates user and returns json with JWT token ```{"token": <jwt token>}```
* user/
  * POST - Request with json payload ```{"email": "email@example.com",	"full_name": "Example Name", "password": "secret123"}```. Creates new user profile.
  * GET - Returns list with all users.
* user/get_most_active_users/
  * GET - Returns list of users ordered by number of posts
* user/`<pk>`/like/ 
  * POST - Request with json payload ```{"post_id": 1}```. Creates like for `<pk>` user and `post_id` post.
* user/`<pk>`/dislike/
  * POST - Request with json payload ```{"post_id": 1}```. Removes like for `<pk>` user and `post_id` post.
* post/
  * POST - Request with json payload ```{"author": "7",	"title": "Test post", "text": "some text for test post"}```. Creates a new post.
  * GET - Returns lust of all posts.
* post/get_posts_by_other_authors/
  * POST - Request with json payload ```{"author_id": 1}```. Returns list of posts of other than `author_id` authors, who also has at least one post with zero likes.
  
Automated bot
-------------

```bash
$ ./manage.py bot
```

Config for automated bot you can find in `bot.ini` file in root directory.
