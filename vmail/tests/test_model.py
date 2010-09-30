from vmail.tests import test
from vmail.model.classes import *

class TestDatabase(test.DatabaseUnitTest):

    def test_domain(self):
        domain = self.db.query(Domain).get(1)
        self.assertTrue(isinstance(domain, Domain))

    def test_domain_deletion(self):
        domain = self.db.query(Domain).get(1)
        self.db.delete(domain)
        self.db.commit()

        # Check the forwards have been removed
        self.assertEqual(self.db.query(Forward
            ).filter_by(domain_id=1
            ).count(), 0)
        
        # Check the users have been removed
        self.assertEqual(self.db.query(User
            ).filter_by(domain_id=1
            ).count(), 0)

    def test_user(self):
        user = self.db.query(User).get(1)
        self.assertTrue(isinstance(user, User))

    def test_user_creation(self):
        usage = UserQuota()
        usage.bytes = 123123
        usage.messages = 83

        user_count = self.db.query(User).count()

        user = User()
        user.domain_id = 1
        user.email = 'joe.bloggs@example.com'
        user.name = 'Joe Bloggs'
        user.password = 'somesecret'
        user.quota = 52428800
        user.usage = usage
        self.db.add(user)
        self.db.commit()

        _user = self.db.query(User
            ).filter_by(email='joe.bloggs@example.com'
            ).one()
        self.assertTrue(user_count < self.db.query(User).count())
        self.assertEqual(_user.name, 'Joe Bloggs')
        self.assertEqual(_user.usage.bytes, 123123)

    def test_user_deletion(self):
        user_count = self.db.query(User).count()
        user = self.db.query(User).get(4)
        self.db.delete(user)
        self.db.commit()

        # Check that the user has indeed been removed from the database
        self.assertTrue(user_count > self.db.query(User).count())

        # Check that the user_quota entry has also been removed
        self.assertNone(self.db.query(UserQuota
            ).filter_by(email='fred@testing.com'
            ).first())

    def test_vacation(self):
        vacation = self.db.query(Vacation).get(1)
        self.assertTrue(isinstance(vacation, Vacation))

    def test_vacation_deletion(self):
        vacation = self.db.query(Vacation).get(1)
        email = vacation.email

        self.db.delete(vacation)
        self.db.commit()

        self.assertEqual(self.db.query(VacationNotification
            ).filter_by(on_vacation=email
            ).count(), 0)
