import os
from typing import Optional

import click
from loguru import logger

from FollowerScrapper import FollowerScrapper

ENVIRONMENT_VARIABLE_NAME = 'GITHUB_TOKEN'


@click.command()
@click.option('--token', default=None, help='Github personal access token')
@click.option('--initial-login', default='singleton11', help='Initial login')
def follow_followers(token: Optional[str], initial_login: str = 'singleton11'):
    logger.info('Starting follow followers job')
    logger.info('Getting token from command line arguments')
    auth_token: str = ''
    if token:
        auth_token = token
        logger.info('Token obtained: {}', auth_token)

    if not auth_token:
        logger.info('Trying to get token from environment variable {}', ENVIRONMENT_VARIABLE_NAME)
        environment_token = os.environ.get(ENVIRONMENT_VARIABLE_NAME)
        if environment_token:
            auth_token = environment_token

    if not auth_token:
        logger.error('Token should be set')
        return

    logger.info('Initializing FollowerScrapper')
    scrapper = FollowerScrapper(initial_login, auth_token)
    scrapper.run()


if __name__ == '__main__':
    follow_followers()
