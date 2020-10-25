import uuid
from typing import Any

from gql import Client, gql
from loguru import logger


class GithubFollowerGetter:
    _username: str
    _client: Client
    _cursor: str

    _page_size = 100

    def __init__(self, username: str, client: Client) -> None:
        self._username = username
        self._client = client
        self._cursor = ''
        super().__init__()

    def get_next_page(self) -> (list[dict[str, str]], bool):
        if not self._cursor:
            query = gql(f"""
query {{
  user(login: "{self._username}") {{
    followers(first: {self._page_size}) {{
      edges {{
        node {{
          id
          login
        }}
      }}
      pageInfo {{
        endCursor
        startCursor
        hasNextPage
      }}
    }}
  }}
}}
        """)
        else:
            query = gql(f"""
query {{
  user(login: "{self._username}") {{
    followers(first: {self._page_size}, , after: "{self._cursor}") {{
      edges {{
        node {{
          id
          login
        }}
      }}
      pageInfo {{
        endCursor
        startCursor
        hasNextPage
      }}
    }}
  }}
}}
                    """)

        result: dict[str, Any] = self._client.execute(query)
        logger.trace('Got response: {}', result)

        self._cursor = result['user']['followers']['pageInfo']['endCursor']
        edges = result['user']['followers']['edges']
        logins: list[dict[str, str]] = [
            {'login': element['node']['login'], 'id': element['node']['id']} for element in edges
        ]
        has_next_page: bool = result['user']['followers']['pageInfo']['hasNextPage']
        return logins, has_next_page

    def follow(self, user_id: str):
        query = gql(f"""
mutation {{
  followUser(input: {{userId: "{user_id}", clientMutationId: "{uuid.uuid4()}"}}) {{
    clientMutationId
  }}
}}
                """)

        self._client.execute(query)
