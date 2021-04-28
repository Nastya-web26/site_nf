from requests import delete, get, post

print(delete('https://natalya-filonova.herokuapp.com/api/v2/news/999').json())
# новости с id = 999 нет в базе

print(delete('https://natalya-filonova.herokuapp.com/api/v2/news/1').json())
print(get('https://natalya-filonova.herokuapp.com/api/v2/news/2').json())