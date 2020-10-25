import random

from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from loguru import logger

from GithubFollowerGetter import GithubFollowerGetter


class FollowerScrapper:
    _current_login: str
    _previous_login: str
    _client: Client
    _current_getter: GithubFollowerGetter

    def __init__(self, initial_login: str, auth_token: str) -> None:
        self._current_login = self._previous_login = initial_login
        logger.info('Initializing transport')
        transport = RequestsHTTPTransport(url="https://api.github.com/graphql",
                                          headers={'Authorization': f'bearer {auth_token}'})
        logger.info('Creating client')
        client = Client(transport=transport, fetch_schema_from_transport=True)
        self._client = client
        super().__init__()

    def run(self):
        while True:
            logger.info('Initializing GithubFollowerGetter for {}', self._current_login)
            self._current_getter = GithubFollowerGetter(self._current_login, self._client)

            logger.info('Collecting logins')
            logins_collected: list[dict[str, str]] = []
            logins, has_next_page = self._current_getter.get_next_page()
            logins_collected += logins
            while has_next_page:
                logins, has_next_page = self._current_getter.get_next_page()
                logins_collected += logins

            for login in logins_collected:
                if login['login'] != 'singleton11':
                    logger.info('Following {}', login['login'])
                    self._current_getter.follow(login['id'])

            logger.info("Logins collected: {}", logins_collected)
            if not logins_collected:
                logger.warning('Reverting previous login {}', self._previous_login)
                self._current_login = self._previous_login
                continue

            logger.info("Choosing random login to go next")

            random_login = random.choice(logins_collected)
            logger.info('Random login chosen: {}', random_login)
            self._previous_login = self._current_login
            self._current_login = random_login['login']
