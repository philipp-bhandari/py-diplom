from urllib.parse import urlencode
import requests
from pprint import pprint
import time
from progress import print_progress_bar

# APP_ID = 6784110
# AUTH_URL = 'https://oauth.vk.com/authorize?'
# auth_data = {
#     'client_id':                  APP_ID,
#     'display':                    'page',
#     'redirect_uri':               'https://vk.com',
#     'scope':                      'friends, groups',
#     'response_type':              'token',
#     'v':                          '5.92'
# }
#
# print(AUTH_URL + urlencode(auth_data))


TOKEN = '175d8d9b43c44d0fe9d781082ae5aa23e3c07e3f5a45ac88f3011d6268bf9a563559aa62f9b36106003e0'
USER_ID = '171691064'


class User:

    def api_request(self, method, data):
        response = requests.get(f'https://api.vk.com/method/{method}.get?', urlencode(data))
        return response.json()

    def get_friends(self, data):
        friends_info = self.api_request('friends', data)
        try:
            friend_list = friends_info['response']['items']
        except KeyError:
            friend_list = []
        return friend_list

    def get_user_data(self, data):
        user_info = self.api_request('users', data)
        name, last_name = user_info['response'][0]['first_name'], user_info['response'][0]['last_name']
        return [name, last_name]

    def get_group_list(self, data):
        groups_info = self.api_request('groups', data)
        try:
            group_list = groups_info['response']['items']
        except KeyError:
            group_list = []
        return group_list

    def __init__(self, id, get_friends=False):
        self.id = id
        access_data = {
            'access_token': TOKEN,
            'v': '5.92',
            'user_id': self.id
        }
        self.name, self.last_name = self.get_user_data(access_data)

        self.group_list = self.get_group_list(access_data)

        if get_friends:
            self.friend_list = self.get_friends(access_data)

    def __str__(self):
        string = f'ID: {self.id}\nИмя: {self.name}\nФамилия: {self.last_name}\n***\n'
        return string


class SpyGame:

    def add_friends(self):
        friend_list = []
        friend_id_list = self.victim.friend_list

        list_len = len(friend_id_list)
        print(f'Запущен процесс получения информации о '
              f'друзьях пользователя {self.victim.name} {self.victim.last_name}:')
        print_progress_bar(0, list_len, prefix='Прогресс:', suffix='', length=50)

        for counter, friend_id in enumerate(friend_id_list):
            friend = User(friend_id)
            friend_list.append(friend)
            time.sleep(0.8)
            print_progress_bar(counter + 1, list_len, prefix='Прогресс:', suffix='', length=50)
            if len(friend_list) == 5:
                return friend_list

    def __init__(self, victim):
        self.victim = victim
        self.friend_list = self.add_friends()



user = User(USER_ID, True)
game = SpyGame(user)

for friend in game.friend_list:
    pprint(friend.__dict__)






