import requests


for i in range(6):
    post_req = requests.post('http://localhost:8888/facade_service', json={"Message": f"message_{str(i)}"})
    print(post_req.text)

get_req = requests.get('http://localhost:8888/facade_service')
print(get_req.text)
