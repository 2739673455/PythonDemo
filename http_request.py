import requests
import json

# url = "http://192.168.33.22:80"
url = "http://127.0.0.1:80"
suffix_url = "/tableMetaInfo/table-list"
post_data = {"id": 1, "tecOwnerUserName": "我"}
headers = {
    "Content-Type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
}
response = requests.get(url + suffix_url, data=json.dumps(post_data), headers=headers)
print(response.text)
