from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Proverb, Category, Profile

class ProverbModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='О труде', slug='o-trude'
        )
        self.proverb = Proverb.objects.create(
            text='Без труда не вытащишь рыбку из пруда',
            meaning='Для достижения цели необходимы усилия',
            status='approved',
            difficulty=1
        )
        self.proverb.categories.add(self.category)

    def test_proverb_created(self):
        """Пословица корректно сохраняется в базе данных"""
        self.assertEqual(Proverb.objects.count(), 1)
        self.assertEqual(self.proverb.text,
                         'Без труда не вытащишь рыбку из пруда')

    def test_proverb_status_default(self):
        """Статус новой пословицы по умолчанию — approved"""
        self.assertEqual(self.proverb.status, 'approved')

    def test_index_page_returns_200(self):
        """Главная страница возвращает код 200"""
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_only_approved_shown(self):
        """На главной странице отображаются только
        одобренные пословицы"""
        Proverb.objects.create(
            text='Тестовая пословица',
            meaning='Тестовое значение',
            status='pending'
        )
        client = Client()
        response = client.get('/')
        proverbs = response.context['proverbs']
        for p in proverbs:
            self.assertEqual(p.status, 'approved')