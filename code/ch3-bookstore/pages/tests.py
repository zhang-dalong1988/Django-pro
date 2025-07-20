from django.test import SimpleTestCase
from django.urls import reverse, resolve
from pages.views import HomePageView


class HomepageTests(SimpleTestCase):
    def setUp(self):  # new
        url = reverse("home")
        self.response = self.client.get(url)

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

    def test_homepage_template(self):
        self.assertTemplateUsed(self.response, "home.html")

    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, "这是我们的主页")

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")

    def test_homepage_url_resolves_homepageview(self):  # new
        view = resolve("/")  # 使用 resolve() 解析 URL
        self.assertEqual(
            view.func.__name__, HomePageView.as_view().__name__
        )  # 断言解析结果的视图函数名称与HomePageView的视图函数名称相匹配