import unittest

from app import create_app, db
from app.models import User
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(name="Potato", username="potato_user", email="potato@example.com")
        u.set_password("i_like_potatoes")
        self.assertFalse(u.check_password("potatoes"))
        self.assertTrue(u.check_password("i_like_potatoes"))

    def test_email_hashing(self):
        u = User(name="Pop Potato", username="pop_potato", email="pop@potato.com")
        email_hash = u.hash_email("potato@pop.com")
        self.assertNotEqual(u.email_hash, email_hash)

        email_hash = u.hash_email("pop@potato.com")
        self.assertEqual(u.email_hash, email_hash)


if __name__ == "__main__":
    unittest.main(verbosity=2)
