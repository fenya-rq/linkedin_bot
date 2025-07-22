#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

import aiofiles
from playwright.async_api import Browser, async_playwright

from linkedin_bot.ai.agents.google_nodes import analyze_posts
from linkedin_bot.ai.utils import GlobalSharedState
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
from linkedin_bot.utilities.async_utils.limiters import TokenLimiter


async def start_activity(headless: bool, **kwargs) -> dict[str, dict[str, str]]:
    """
    Set up client and manager, then perform reposts.

    :param headless: Launch browser in headless mode if True
    :param kwargs: Additional parameters
                  - restrict (int): Max number of posts to repost
    :raises Exception: If `restrict` is less than 1
    """
    client = SimpleClient(LINKEDIN_NAME, LINKEDIN_PASSWORD, LINKEDIN_LOGIN_URL)

    async with async_playwright() as pw:
        # TODO: refactor `acc_managers` to initialize the page here and share to managers
        browser: Browser = await pw.chromium.launch(headless=headless)

        analyst = ManagerFactory.create_analyst_manager(
            client, browser, LinkedInVacancyAnalyzeParser
        )
        return await analyst.add_post_links()


async def main(headless: bool = True, **kwargs):
    token_limiter = TokenLimiter(15000)
    shared_state = GlobalSharedState(spent_tokens=0, target_posts=[])

    posts_data = await start_activity(headless)

    tasks = [
        asyncio.create_task(
            analyze_posts(
                user_input=f'{content}', token_limiter=token_limiter, shared_state=shared_state
            )
        )
        for content in posts_data.values()
    ]

    await asyncio.gather(*tasks)

    last_result = shared_state['target_posts']

    if last_result:
        # Write AI summaries to file
        # TODO: refactor - make as ai tool and call directly from node
        #  NOTE: we can't use it with tool node or naive tool calling for current LLM
        async with aiofiles.open(ROOT_DIR / 'files/vacancies.txt', mode='a', encoding='utf-8') as f:
            for msg in last_result:
                await f.write(f'\n{msg}\n\n')

        log_writer(main_logger, 55, 'Posts analysed and writen.')


if __name__ == '__main__':
    log_writer(main_logger, 55, 'Service started...')
    # Parse CLI args and determine headless mode
    sys_args = check_sys_arg()
    head_off = True
    if sys_args.debug == 'true' or DEBUG == 'true':
        head_off = False

    asyncio.run(main(head_off))
