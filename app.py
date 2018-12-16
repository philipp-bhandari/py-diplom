from urllib.parse import urlencode
import requests
from pprint import pprint
import time
from progress import print_progress_bar
import json

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


TOKEN = 'f39396467a3268f80f7f949759413d52d11a40a0bc8eade9053138bd29a45c1246bddbdb9e66f78855fb3'
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


class Group:

    def get_info(self):
        access_data = {
            'access_token': TOKEN,
            'v': '5.92',
            'group_id': self.id,
            'fields': 'members_count'
        }
        response = requests.get(f'https://api.vk.com/method/groups.getById?', urlencode(access_data))
        return response.json()

    def __init__(self, id):
        self.id = id
        info = self.get_info()
        self.name = info['response'][0]['name']
        self.members_count = info['response'][0]['members_count']


class SpyGame:

    def add_friends(self):
        friend_list = []
        friend_id_list = self.victim.friend_list

        list_len = len(friend_id_list)
        print(f'Запущен процесс получения информации о '
              f'друзьях пользователя {self.victim.name} {self.victim.last_name}:')
        print_progress_bar(0, list_len, prefix='Прогресс:', suffix='', length=30)

        for counter, friend_id in enumerate(friend_id_list):
            friend = User(friend_id)
            friend_list.append(friend)
            time.sleep(0.8)
            print_progress_bar(counter + 1, list_len, prefix='Прогресс:', suffix='', length=30)
        print('Данные получены!')
        return friend_list


    def get_result_set(self, group_list, groups_set):
        victim_group_set = set(group_list)
        return victim_group_set.difference(groups_set)

    def get_groups_data(self, groups_set):
        print('Запущен анализ результирующего списка групп:')
        list_len = len(groups_set)
        result_group_list = []

        print_progress_bar(0, list_len, prefix='Прогресс:', suffix='', length=30)
        for counter, group_id in enumerate(groups_set):
            group = Group(group_id)
            result_group_list.append(group.__dict__)
            time.sleep(0.8)
            print_progress_bar(counter + 1, list_len, prefix='Прогресс:', suffix='', length=30)
        return result_group_list

    def __init__(self, victim):
        self.victim = victim
        self.victim_group_list = victim.group_list
        self.friend_list = self.add_friends()

        groups = [friend.group_list for friend in self.friend_list]
        groups = [item for row in groups for item in row]  # Делаем плоский массив двойным перебором значений
        self.friends_groups_set = set(groups)

        self.result_set = self.get_result_set(self.victim_group_list, self.friends_groups_set)

        self.result_json = self.get_groups_data(self.result_set)


if __name__ == '__main__':
    user = User(USER_ID, True)
    game = SpyGame(user)
    file_name = 'data.json'
    with open(file_name, 'w') as outfile:
        json.dump(game.result_json, outfile)
    print(f'Анализ завершен, данные сохранены в {file_name}')
