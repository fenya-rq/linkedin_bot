#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automate LinkedIn repost activity using Playwright."""

import asyncio

from playwright.async_api import Browser, async_playwright

from linkedin_bot.bot import LinkedInPostsParser, LinkedInVacancyAnalyzeParser
from linkedin_bot.config import (
    DEBUG,
    LINKEDIN_LOGIN_URL,
    LINKEDIN_NAME,
    LINKEDIN_PASSWORD,
    main_logger,
)
from linkedin_bot.factories import ManagerFactory
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
    client = SimpleClient(LINKEDIN_NAME, LINKEDIN_PASSWORD, LINKEDIN_LOGIN_URL)

    # repost = ManagerFactory.create_repost_manager(client, LinkedInPostsParser)
    # analyst = ManagerFactory.create_analyst_manager(client, LinkedInVacancyAnalyzeParser)

    reposts_amount = kwargs.get('restrict', 0)
    if reposts_amount < 1:
        raise Exception('Reposts amount should be at least 1 or greater!')

    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=headless)

        # repost = ManagerFactory.create_repost_manager(client, browser, LinkedInPostsParser)
        analyst = ManagerFactory.create_analyst_manager(client, browser, LinkedInVacancyAnalyzeParser)

        # await repost.make_reposts(reposts_amount)
        result = await analyst.get_post_data()

        with open('test.txt', mode='w', encoding='utf-8') as f:
            for t in result:
                f.write(t)


if __name__ == '__main__':
    log_writer(main_logger, 55, 'Service started...')
    # Parse CLI args and determine headless mode
    sys_args = check_sys_arg()
    head_off = True
    if sys_args.debug == 'true' or DEBUG == 'true':
        head_off = False

    asyncio.run(start_activity(head_off, restrict=sys_args.posts_restrict))
