from urllib.parse import urlencode
import requests
from pprint import pprint
import time
from progress import print_progress_bar
import json

API_TOKEN = '9c3fb3a79e09ab541e3f69f5a618c0d4cca6089b1b16d4c4bd77566b0e73d53d8ac2740e5f02a3e02b4e4'
USER_ID = '171691064'
VERSION = '5.92'
APP_ID = 6784110
AUTH_URL = 'https://oauth.vk.com/authorize?'
AUTH_DATA = {
    'client_id': APP_ID,
    'display': 'page',
    'redirect_uri': 'https://vk.com',
    'scope': 'friends, groups',
    'response_type': 'token',
    'v': VERSION
    }


def check_token(token):
    access_data = {
        'access_token': token,
        'v': VERSION,
        'user_id': USER_ID
    }
    response = requests.get(f'https://api.vk.com/method/users.get?', urlencode(access_data))
    user_info = response.json()
    try:
        name = user_info['response'][0]['first_name']
        return True
    except KeyError:
        return False


class User:

    def __init__(self, id, get_friends=False):
        self.id = id
        access_data = {
            'access_token': API_TOKEN,
            'v': VERSION,
            'user_id': self.id
        }
        self.name, self.last_name = self.get_user_data(access_data)

        self.group_list = self.get_group_list(access_data)

        if get_friends:
            self.friend_list = self.get_friends(access_data)

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

    def __str__(self):
        string = f'ID: {self.id}\nИмя: {self.name}\nФамилия: {self.last_name}\n***\n'
        return string


class Group:

    def __init__(self, id):
        self.id = id
        info = self.get_info()
        self.name = info['response'][0]['name']
        try:
            self.members_count = info['response'][0]['members_count']
        except KeyError:
            self.members_count = 'Информация скрыта'

    def get_info(self):
        access_data = {
            'access_token': API_TOKEN,
            'v': VERSION,
            'group_id': self.id,
            'fields': 'members_count'
        }
        response = requests.get(f'https://api.vk.com/method/groups.getById?', urlencode(access_data))
        return response.json()


class SpyGame:

    def __init__(self, victim):
        self.victim = victim
        self.victim_group_list = victim.group_list
        self.friend_list = self.add_friends()

        groups = [friend.group_list for friend in self.friend_list]
        groups = [item for row in groups for item in row]  # Делаем плоский массив двойным перебором значений
        self.friends_groups_set = set(groups)

        self.result_set = self.get_result_set(self.victim_group_list, self.friends_groups_set)

        self.result_json = self.get_groups_data(self.result_set)

    def add_friends(self):
        friend_list = []
        friend_id_list = self.victim.friend_list

        list_len = len(friend_id_list)
        print(f'Запущен процесс получения информации о '
              f'друзьях пользователя {self.victim.name} {self.victim.last_name}:')
        try:
            print_progress_bar(0, list_len, prefix='Прогресс:', suffix='', length=30)
        except ZeroDivisionError:
            print('Информация о друзьях недоступна.')
            return friend_list

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

        try:
            print_progress_bar(0, list_len, prefix='Прогресс:', suffix='', length=30)
        except ZeroDivisionError:
            print('Информация о группах недоступна.')
            return result_group_list

        for counter, group_id in enumerate(groups_set):
            group = Group(group_id)
            result_group_list.append(group.__dict__)
            time.sleep(0.8)
            print_progress_bar(counter + 1, list_len, prefix='Прогресс:', suffix='', length=30)
        return result_group_list


if __name__ == '__main__':
    if check_token(API_TOKEN):
        user = User(USER_ID, True)
        game = SpyGame(user)
        file_name = 'data.json'
        with open(file_name, 'w') as outfile:
            json.dump(game.result_json, outfile)
        print(f'Анализ завершен, данные сохранены в {file_name}')
    else:
        print('\nЗамените токен, срок использования истек.\n')
        print(AUTH_URL + urlencode(AUTH_DATA))
