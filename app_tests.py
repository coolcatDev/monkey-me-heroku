import os
import app
import unittest
import tempfile
import StringIO
from StringIO import *


class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_01_login_logout(self):
        # login
        rv = self.login('Alex', 'passwordAlex')
        assert 'Friends' in rv.data
        # logout
        rv = self.logout()
        assert 'You have logged out' in rv.data
        # login no password
        rv = self.login('Alex', 'noPassword')
        assert 'You have to Login' in rv.data
        # login no username
        rv = self.login('WrongName', 'passwordAlex')
        assert 'You have to Login' in rv.data

    def test_02_register_page(self):
        # enter register
        rv = self.app.get('/register')
        assert 'Register' in rv.data

    def registering(self, username, email, password, passwordCheck, phone):
        with open('static/images/test.jpg') as test:
            imgStringIO = StringIO(test.read())

        return self.app.post(
            '/registering',
            content_type='multipart/form-data',
            data=dict(
                {'file': (imgStringIO, 'test.jpg')},
                username=username,
                email=email,
                password=password,
                passwordCheck=passwordCheck,
                phone=phone
            ), follow_redirects=True
        )

    def test_03_registering(self):
        # new username
        rv = self.registering(
            'TestUser',
            'test@test.com',
            'passwordTest',
            'passwordTest',
            '900102030'
        )
        assert 'Registered Successfully' in rv.data
        # existing username/user
        rv = self.registering(
            'Hulda',
            'hulda@hulda.com',
            'passwordHulda',
            'passwordHulda',
            '900102030'
        )
        assert 'Username Taken' in rv.data
        # no username
        rv = self.registering(
            '',
            'santana@santana.com',
            'passwordSantana',
            'passwordSantana',
            '900102030'
        )
        assert 'Username required' in rv.data
        # no email
        rv = self.registering(
            'Santana',
            '',
            'passwordSantana',
            'passwordSantana',
            '900102030'
        )
        assert 'Email required' in rv.data
        # no password
        rv = self.registering(
            'Santana',
            'santana@santana.com',
            '',
            'passwordSantana',
            '900102030'
        )
        assert 'Password required' in rv.data
        # no password confirmation
        rv = self.registering(
            'Santana',
            'santana@santana.com',
            'passwordSantana',
            '',
            '900102030'
        )
        assert 'Confirm password' in rv.data
        # no password match on form
        rv = self.registering(
            'Santana',
            'santana@santana.com',
            'passwordSantana',
            'passwordSsssssntana',
            '900102030'
        )
        assert 'Retype passwords' in rv.data
        # no phone
        rv = self.registering(
            'Santana',
            'santana@santana.com',
            'passwordSantana',
            'passwordSantana',
            ''
        )
        assert 'Phone required' in rv.data

    def test_04_editAccount(self):
        # enter edit account (TestUser)
        self.login('Alex', 'passwordAlex')
        rv = self.app.get('/editAccount')
        assert 'Edit profile' in rv.data

    def saveEditAccount(
        self,
        userName,
        userEmail,
        userPhone,
        userPassA,
        userPassB
    ):
        # save edited account(TestUser)
        self.login('TestUser', 'passwordTest')
        with open('static/images/test.jpg') as test:
            imgStringIO = StringIO(test.read())

        return self.app.post(
            '/saveEditAccount',
            content_type=
            'multipart/form-data',
            data=dict(
                {'file': (imgStringIO, 'test.jpg')},
                userName=userName,
                userEmail=userEmail,
                userPhone=userPhone,
                userPassA=userPassA,
                userPassB=userPassB
            ), follow_redirects=True
        )

    def test_05_saveEditAccount(self):
        # successfully changed with same username
        rv = self.saveEditAccount(
            'TestUser',
            'user@user.com',
            '1800102030',
            'passwordTest',
            'passwordTest'
        )
        assert 'Saved' in rv.data
        # successfully changed with different(not taken) username
        rv = self.saveEditAccount(
            'BetaUser',
            'test@test.com',
            '900102030',
            'passwordTest',
            'passwordTest'
        )
        assert 'Saved' in rv.data
        # existing username/user
        rv = self.saveEditAccount(
            'Alex',
            'test@test.com',
            '900102030',
            'passwordTest',
            'passwordTest'
        )
        assert 'Username Taken' in rv.data
        # no username
        rv = self.saveEditAccount(
            '',
            'test@test.com',
            '900102030',
            'passwordTest',
            'passwordTest'
        )
        assert 'Username required' in rv.data
        # no email
        rv = self.saveEditAccount(
            'BetaUser',
            '',
            '900102030',
            'passwordTest',
            'passwordTest'
        )
        assert 'Email required' in rv.data
        # no password
        rv = self.saveEditAccount(
            'BetaUser',
            'test@test.com',
            '900102030',
            '',
            'passwordTest'
        )
        assert 'Password required' in rv.data
        # no password confirmation
        rv = self.saveEditAccount(
            'BetaUser',
            'test@test.com',
            '900102030',
            'passwordTest',
            ''
        )
        assert 'Confirm password' in rv.data
        # no password match
        rv = self.saveEditAccount(
            'BetaUser',
            'test@test.com',
            '900102030',
            'passsssxcwordTest',
            'passwordTest'
        )
        assert 'Retype passwords' in rv.data
        # no phone
        rv = self.saveEditAccount(
            'BetaUser',
            'test@test.com',
            '',
            'passwordTest',
            'passwordTest'
        )
        assert 'Phone required' in rv.data

    def test_06_index_page(self):
        # index redirect
        self.login('Alex', 'passwordAlex')
        rv = self.app.get('/', follow_redirects=True)
        assert 'Friends' in rv.data

    def test_07_myProfile_page(self):
        # enter my profile
        self.login('Alex', 'passwordAlex')
        rv = self.app.get('/myProfile')
        assert 'My Profile' in rv.data

    def test_08_users_page(self):
        # enter users
        self.login('Alex', 'passwordAlex')
        rv = self.app.get('/users')
        assert 'Users' in rv.data

    def test_09_friends_page(self):
        # enter friends
        self.login('Alex', 'passwordAlex')
        rv = self.app.get('/friends')
        assert 'Friends' in rv.data

    def test_10_profile_page(self):
        # enter profile
        self.login('Alex', 'passwordAlex')
        rv = self.app.get('/profile1')
        assert 'Profile' in rv.data

    def test_11_addFriend(self):
        # add existing friend(Alex(id=1) & Pedro(id=8))
        self.login('Alex', 'passwordAlex')
        rv = self.app.get('/addFriend/8', follow_redirects=True)
        assert 'Friendship exists' in rv.data

    def test_12_removeFriend(self):
        # remove friend(Alex(1) & Sara(2))
        self.login('Alex', 'passwordAlex')
        rv = self.app.get('/removeFriend/2', follow_redirects=True)
        assert 'Friendship removed' in rv.data

    def test_13_addFriendNew(self):
        # add new friend(Alex(1) & Sara(2))
        self.login('Alex', 'passwordAlex')
        rv = self.app.get('/addFriend/2', follow_redirects=True)
        assert 'Friendship Created' in rv.data

    def test_14_deleteAccount(self):
        self.login('BetaUser', 'passwordTest')
        rv = self.app.get('/deleteAccount', follow_redirects=True)
        assert 'Account deleted' in rv.data


if __name__ == '__main__':
    unittest.main()
