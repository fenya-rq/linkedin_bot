#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiofiles
import asyncio
from playwright.async_api import Browser, async_playwright

from linkedin_bot.ai import start_graph
from linkedin_bot.bot import LinkedInVacancyAnalyzeParser
from linkedin_bot.config import (
    DEBUG,
    LINKEDIN_LOGIN_URL,
    LINKEDIN_NAME,
    LINKEDIN_PASSWORD,
    ROOT_DIR,
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

    reposts_amount = kwargs.get('restrict', 0)
    if reposts_amount < 1:
        raise Exception('Reposts amount should be at least 1 or greater!')

    async with async_playwright() as pw:
        # TODO: refactor `acc_managers` to initialize the page here and share to managers
        browser: Browser = await pw.chromium.launch(headless=headless)

        analyst = ManagerFactory.create_analyst_manager(client, browser, LinkedInVacancyAnalyzeParser)
        posts_data = await analyst.add_post_links()

    result = None
    for content in posts_data.values():
        log_writer(main_logger, 55, 'AI analysing started...')
        result = await start_graph(user_input=f'{content}')

    if result and (analyzed_posts := result[0].get('chatbot', {}).get('target_posts')):
        log_writer(main_logger, 55, 'Posts analysed and writen.')

        # Write AI summaries to file
        # TODO: refactor - make as ai tool and call directly from node
        #  NOTE: we can't use it with tool node or naive tool calling for current LLM
        async with aiofiles.open(ROOT_DIR / 'files/vacancies.txt', mode='a', encoding='utf-8') as f:
            for msg in analyzed_posts:
                await f.write(f'{msg.content}\n')


if __name__ == '__main__':
    log_writer(main_logger, 55, 'Service started...')
    # Parse CLI args and determine headless mode
    sys_args = check_sys_arg()
    head_off = True
    if sys_args.debug == 'true' or DEBUG == 'true':
        head_off = False

    asyncio.run(start_activity(head_off, restrict=sys_args.posts_restrict))
