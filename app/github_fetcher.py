import requests


def fetch_repository(owner, repo_name):
    url = f"https://api.github.com/repos/{owner}/{repo_name}"

    response = requests.get(url)

    if response.status_code != 200:
        return None

    return response.json()


# if __name__ == "__main__":
#     data = fetch_repository("apache", "kafka")

#     print(data["name"])
#     print(data["owner"]["login"])

def fetch_repository_events(owner, repo_name):

    url = f"https://api.github.com/repos/{owner}/{repo_name}/events"

    response = requests.get(url)

    if response.status_code != 200:
        return None

    return response.json()