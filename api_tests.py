import typing

import requests
import pytest

API_URL = 'https://demoqa.com/'
ACCOUNT_API_URL = API_URL + 'Account/v1/'
BOOKS_API_URL = API_URL + 'BookStore/v1/'
BOOKS_API_CALL = BOOKS_API_URL + 'Books'
BOOK_API_CALL = BOOKS_API_URL + 'Book'
GENERATE_TOKEN_CALL = ACCOUNT_API_URL + 'GenerateToken'
LOGIN_CALL = ACCOUNT_API_URL + 'Login'
USER_CALL = ACCOUNT_API_URL + 'User'


userName = 'vshakhrai'
userPassword = 'Qwerty1!'

token = ''
headers = {}
userId = ''
userData = {}


@pytest.fixture(scope='class')
def login_session():
    global headers
    res = requests.post(GENERATE_TOKEN_CALL, {"userName": userName, "password": userPassword})
    assert res.status_code == 200
    global token
    token = res.json().get('token')
    global headers
    headers['Authorization'] = f'Bearer {token}'
    res = requests.post(LOGIN_CALL, {"userName": userName, "password": userPassword})
    assert res.status_code == 200
    global userId
    userId = res.json().get('userId')
    global userData
    res = requests.get(USER_CALL + '/' + userId, headers=headers)
    assert res.status_code == 200


@pytest.fixture(scope='class')
def gen_token():
    global token
    res = requests.post(GENERATE_TOKEN_CALL, {"userName": userName, "password": userPassword})
    assert res.status_code == 200
    token = res.json().get('token')
    global headers
    headers['Authorization'] = f'Bearer {token}'


def login_call_routine(user_name, user_password, expected_status_code=200, status: typing.Any = None,
                       result: typing.Any = None):
    res = requests.post(GENERATE_TOKEN_CALL, {"userName": user_name, "password": user_password})
    assert res.status_code == expected_status_code
    assert res.json().get('status') == status
    assert res.json().get('result') == result


class TestAccountGenerateToken:

    def test_wrong_username(self):
        login_call_routine('342Fddss', userPassword, status='Failed', result='User authorization failed.')

    def test_wrong_password(self):
        login_call_routine(userName, 'kf5dfnw787', status='Failed', result='User authorization failed.')

    def test_empty_username(self):
        login_call_routine('', userPassword, 400)

    def test_empty_password(self):
        login_call_routine(userName, '', 400)

    def test_wrong_data_types_username(self):
        """[], {}, None"""
        login_call_routine([], userPassword, 400)
        login_call_routine({}, userPassword, 400)
        login_call_routine(None, userPassword, 400)

    def test_wrong_data_types_password(self):
        """[], {}, None"""
        login_call_routine(userName, [], 400)
        login_call_routine(userName, {}, 400)
        login_call_routine(userName, None, 400)


def token_call_routine(local_token, expected_status_code=200):
    res = requests.post(LOGIN_CALL, {"userName": userName, "password": userPassword})
    user_id = res.json().get('userId')
    res = requests.get(USER_CALL + '/' + user_id, headers={'Authorization': f'Bearer {local_token}'})
    assert res.status_code == expected_status_code


@pytest.mark.usefixtures('gen_token')
class TestAccountToken:

    def test_wrong_token(self):
        token_call_routine('yutysdifuiuy786few7r8364f34fw*&^585ce', 401)

    def test_empty_token(self):
        token_call_routine('', 401)

    def test_wrong_data_types_token(self):
        token_call_routine({}, 401)
        token_call_routine([], 401)
        token_call_routine(None, 401)

    def test_correct_token(self):
        token_call_routine(token, 200)


@pytest.mark.usefixtures('login_session')
class TestAccountGetUser:
    @staticmethod
    def get_user_routine(user_uuid, status_code=200):
        res = requests.get(USER_CALL + '/' + user_uuid, headers=headers)
        assert res.status_code == status_code
        return res

    def test_get_user_with_wrong_uuid(self):
        self.get_user_routine('1e45ea7c-14de-4254-961c-4694743375e8', 401)

    def test_get_user_with_broken_uuid(self):
        self.get_user_routine('abdehhtt-5fgeegteg$%&^233', 401)

    def test_get_user_with_empty_uuid(self):
        self.get_user_routine('', 200)

    def test_get_user_success(self):
        data = self.get_user_routine(userId).json()

        assert data.get('userId') == userId
        assert data.get('username') == userName
        assert isinstance(data.get('books'), list)


@pytest.mark.usefixtures('login_session')
class TestAccountDeleteUser:
    @staticmethod
    def delete_user_routine(user_uuid, status_code=200, message='User Id not correct!'):
        res = requests.delete(USER_CALL + '/' + user_uuid, headers=headers)
        assert res.status_code == status_code
        if status_code == 200:
            assert res.json().get('message') == message
        return res

    def test_delete_user_with_wrong_uuid(self):
        self.delete_user_routine('1e45ea7c-14de-4254-961c-4694743375e8')

    def test_delete_user_with_broken_uuid(self):
        self.delete_user_routine('abdehhtt-5fgeegteg$%&^233')

    def test_delete_user_with_empty_uuid(self):
        self.delete_user_routine('', 404)


@pytest.mark.usefixtures('login_session')
class TestBookStoreGetBooks:

    def test_unauthorized_user(self):
        res = requests.get(BOOKS_API_CALL)
        assert res.status_code == 200

    def test_authorized_user(self):
        res = requests.get(BOOKS_API_CALL, headers=headers)
        assert res.status_code == 200


@pytest.mark.usefixtures('login_session')
class TestBookStorePostBooks:
    @staticmethod
    def post_book_routine(data: dict, local_headers=headers, expected_status_code=401):
        res = requests.post(BOOKS_API_CALL, json=data, headers=local_headers, timeout=2)
        assert res.status_code == expected_status_code

    def test_wrong_user_id(self):
        self.post_book_routine({'userId': '1e45ea7c-14de-4254-961c-4694743375e8',
                                'collectionOfIsbns': [{'isbn': '9781491950296'}]})

    def test_empty_user_id(self):
        self.post_book_routine({'collectionOfIsbns': [{'isbn': '9781491950296'}]})

    def test_wrong_collection_data(self):
        self.post_book_routine({'userId': userId, 'collectionOfIsbns': [{'isbn': '36363636363636'}]})

    def test_empty_collection_data(self):
        self.post_book_routine({'userId': userId})

    def test_wrong_type_of_collection_data(self):
        self.post_book_routine({'userId': userId, 'collectionOfIsbns': None})
        self.post_book_routine({'userId': userId, 'collectionOfIsbns': {}})
        self.post_book_routine({'userId': userId, 'collectionOfIsbns': ''})
        self.post_book_routine({'userId': userId, 'collectionOfIsbns': 54})

    def test_success(self):
        self.post_book_routine({'userId': userId, 'collectionOfIsbns': [{'isbn': '9781491950296'}]},
                               expected_status_code=200)

    def test_unauthorised_user(self):
        self.post_book_routine({'userId': userId, 'collectionOfIsbns': [{'isbn': '9781491950296'}]}, {})


@pytest.mark.usefixtures('login_session')
class TestBookStoreDeleteBooks:

    @staticmethod
    def delete_books_routine(user_id, expected_status_code=200):
        res = requests.delete(BOOKS_API_CALL + f'?UserId={user_id}', headers=headers)
        assert res.status_code == expected_status_code

    def test_empty_user_id(self):
        self.delete_books_routine('', 401)

    def test_without_user_id(self):
        res = requests.delete(BOOK_API_CALL)
        assert res.status_code == 401

    def test_wrong_user_id(self):
        self.delete_books_routine('1e45ea7c-14de-4254-961c-4694743375e8', 401)

    def test_success_delete(self):
        self.delete_books_routine(userId, 204)

    def test_unauthorized_delete(self):
        res = requests.delete(BOOKS_API_CALL + f'?UserId={userId}')
        assert res.status_code == 401


class TestBookStoreGetBook:

    @staticmethod
    def get_book_routine(isbn, expected_status_code=200):
        res = requests.get(BOOK_API_CALL + f'?ISBN={isbn}')
        assert res.status_code == expected_status_code

    def test_get_exist_book(self):
        self.get_book_routine('9781491950296')

    def test_get_not_existed_book(self):
        self.get_book_routine('1111111111111', 400)


@pytest.mark.usefixtures('login_session')
class TestBookStoreDeleteBook:
    @staticmethod
    def get_book_routine(isbn, user_id, expected_status_code=200):
        res = requests.delete(BOOK_API_CALL, data={'isbn': isbn, 'userId': user_id}, headers=headers)
        assert res.status_code == expected_status_code

    def test_delete_exist_book_not_in_collection(self):
        self.get_book_routine('9781491950296', userId, 400)

    def test_selete_not_existed_book(self):
        self.get_book_routine('1111111111111', userId, 400)


@pytest.mark.usefixtures('login_session')
class TestLogicCases:

    @staticmethod
    def add_book_to_collection(isbn, user_id):
        res = requests.post(
            BOOKS_API_CALL,
            json={'userId': user_id, 'collectionOfIsbns': [{'isbn': isbn}]},
            headers=headers,
            timeout=3
        )
        assert res.status_code == 201

    @staticmethod
    def get_user_books(user_id):
        res = requests.get(USER_CALL + '/' + user_id, headers=headers, timeout=3)
        assert res.status_code == 200
        return res.json().get('books')

    @staticmethod
    def remove_user_books(user_id):
        res = requests.delete(BOOKS_API_CALL + f'?UserId={user_id}', headers=headers, timeout=3)
        assert res.status_code == 204

    def test_add_book_to_collection_and_remove(self):
        expected_isbn = '9781449325862'
        self.add_book_to_collection('9781449325862', userId)
        books = self.get_user_books(userId)
        assert len(books) == 1
        actual_isbn = books[0].get('isbn')
        assert actual_isbn == expected_isbn
        self.remove_user_books(userId)
        books = self.get_user_books(userId)
        assert len(books) == 0



