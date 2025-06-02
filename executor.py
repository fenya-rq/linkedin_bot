#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automate LinkedIn repost activity using Playwright."""

import asyncio

from playwright.async_api import Browser, async_playwright

from linkedin_bot.bot import LinkedInPostsParser, LNRepostManager
from linkedin_bot.config import (
    DEBUG,
    LINKEDIN_LOGIN_URL,
    LINKEDIN_NAME,
    LINKEDIN_PASSWORD,
    main_logger,
)
from linkedin_bot.services import SimpleClient
from linkedin_bot.utilities import check_sys_arg, log_writer


async def start_activity(headless: bool, **kwargs) -> None:
    """
    Set up client and manager, then perform reposts.

    :param headless: Launch browser in headless mode if True
    :param kwargs: Additional parameters
                  - restrict (int): Max number of posts to repost
    :raises Exception: If `restrict` is less than 1
    """
    # TODO: bring out using factory pattern
    client = SimpleClient(LINKEDIN_NAME, LINKEDIN_PASSWORD, LINKEDIN_LOGIN_URL)
    manager = LNRepostManager(client, LinkedInPostsParser)

    reposts_amount = kwargs.get('restrict', 0)
    if reposts_amount < 1:
        raise Exception('Reposts amount should be at least 1 or greater!')

    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=headless)
        await manager.make_reposts(browser, reposts_amount)


if __name__ == '__main__':
    # TODO: implement check `default` value in passed credentials
    log_writer(main_logger, 55, 'Service started...')
    # Parse CLI args and determine headless mode
    sys_args = check_sys_arg()
    head_off = True
    if sys_args.debug == 'true' or DEBUG == 'true':
        head_off = False

    asyncio.run(start_activity(head_off, restrict=sys_args.posts_restrict))
