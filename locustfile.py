from locust import HttpUser, task, between, tag
import random
import json


class MyLoadTest(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        print("Test started!")
        # Ініціалізуємо випадкові ID для використання в тестах
        self.random_user_id = random.randint(1, 10)
        self.random_post_id = random.randint(1, 100)
        self.random_album_id = random.randint(1, 100)
        self.random_todo_id = random.randint(1, 200)

    def on_stop(self):
        print("Test stopped!")

    @tag('posts', 'get')
    @task
    def get_all_posts(self):
        self.client.get("/posts/", name="GET /posts")

    @tag('posts', 'get')
    @task
    def get_post_by_id(self):
        post_id = random.randint(1, 100)
        with self.client.get(f"/posts/{post_id}", name=f"GET /posts/[id]", catch_response=True) as response:
            if response.status_code == 200:
                if "id" in response.json() and "title" in response.json():
                    response.success()
                else:
                    response.failure("Відсутні очікувані поля в відповіді")
            else:
                response.failure(f"Невірний статус код: {response.status_code}")

    @tag('posts', 'post')
    @task(3)  # вага завдання
    def create_post(self):
        payload = {
            "userId": random.randint(1, 10),
            "title": f"Awesome title {random.randint(1, 100)}",
            "body": f"Test body for post {random.randint(1, 100)}"
        }
        with self.client.post("/posts/", json=payload, name="POST /posts", catch_response=True) as response:
            if response.status_code == 201:
                if "id" in response.json():
                    response.success()
                else:
                    response.failure("Створений пост не містить ID")
            else:
                response.failure(f"Невірний статус код при створенні поста: {response.status_code}")

    @tag('posts', 'put')
    @task(2)
    def update_post(self):
        post_id = random.randint(1, 100)
        payload = {
            "userId": self.random_user_id,
            "id": post_id,
            "title": f"Updated title {random.randint(1, 100)}",
            "body": f"Updated body {random.randint(1, 100)}"
        }
        with self.client.put(f"/posts/{post_id}", json=payload, name="PUT /posts/[id]", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Невдала спроба оновлення поста: {response.status_code}")

    @tag('posts', 'delete')
    @task(1)
    def delete_post(self):
        post_id = random.randint(1, 100)
        with self.client.delete(f"/posts/{post_id}", name="DELETE /posts/[id]", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Помилка видалення поста: {response.status_code}")

    @tag('posts', 'comments', 'get')
    @task(2)
    def get_post_comments(self):
        post_id = random.randint(1, 100)
        with self.client.get(f"/posts/{post_id}/comments", name="GET /posts/[id]/comments", catch_response=True) as response:
            if response.status_code == 200:
                if isinstance(response.json(), list):
                    response.success()
                else:
                    response.failure("Неправильний формат відповіді для коментарів")
            else:
                response.failure(f"Помилка отримання коментарів: {response.status_code}")

    @tag('users', 'get')
    @task(1)
    def get_user(self):
        user_id = random.randint(1, 10)
        with self.client.get(f"/users/{user_id}", name="GET /users/[id]", catch_response=True) as response:
            if response.status_code == 200:
                if "name" in response.json() and "email" in response.json():
                    response.success()
                else:
                    response.failure("Відсутні очікувані поля користувача")
            else:
                response.failure(f"Помилка отримання даних користувача: {response.status_code}")

    @tag('users', 'todos', 'get')
    @task(1)
    def get_user_todos(self):
        user_id = random.randint(1, 10)
        with self.client.get(f"/users/{user_id}/todos", name="GET /users/[id]/todos", catch_response=True) as response:
            if response.status_code == 200:
                if isinstance(response.json(), list):
                    response.success()
                else:
                    response.failure("Неправильний формат відповіді для завдань")
            else:
                response.failure(f"Помилка отримання завдань: {response.status_code}")

    @tag('todos', 'post')
    @task(1)
    def create_todo(self):
        payload = {
            "userId": self.random_user_id,
            "title": f"Todo task {random.randint(1, 100)}",
            "completed": random.choice([True, False])
        }
        with self.client.post("/todos", json=payload, name="POST /todos", catch_response=True) as response:
            if response.status_code == 201:
                if "id" in response.json():
                    response.success()
                else:
                    response.failure("Створене завдання не містить ID")
            else:
                response.failure(f"Помилка створення завдання: {response.status_code}")

    @tag('albums', 'get')
    @task(1)
    def get_albums(self):
        with self.client.get("/albums", name="GET /albums", catch_response=True) as response:
            if response.status_code == 200:
                if isinstance(response.json(), list) and len(response.json()) > 0:
                    response.success()
                else:
                    response.failure("Пустий або неправильний список альбомів")
            else:
                response.failure(f"Помилка отримання списку альбомів: {response.status_code}")

    @tag('photos', 'get')
    @task(1)
    def get_album_photos(self):
        album_id = random.randint(1, 100)
        with self.client.get(f"/albums/{album_id}/photos", name="GET /albums/[id]/photos", catch_response=True) as response:
            if response.status_code == 200:
                if isinstance(response.json(), list):
                    for photo in response.json()[:5]:  # Перевіряємо перші 5 фотографій
                        if "albumId" not in photo or "url" not in photo:
                            response.failure("Відсутні очікувані поля у фотографіях")
                            return
                    response.success()
                else:
                    response.failure("Неправильний формат відповіді для фотографій")
            else:
                response.failure(f"Помилка отримання фотографій: {response.status_code}")

    @tag('todos', 'put')
    @task(1)
    def update_todo(self):
        todo_id = random.randint(1, 200)
        payload = {
            "userId": self.random_user_id,
            "id": todo_id,
            "title": f"Updated todo {random.randint(1, 100)}",
            "completed": True
        }
        with self.client.put(f"/todos/{todo_id}", json=payload, name="PUT /todos/[id]", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Помилка оновлення завдання: {response.status_code}")