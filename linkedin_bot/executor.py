#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automate LinkedIn repost activity using Playwright."""

import asyncio

from bot import LinkedInPostsParser, LNPostManager
from config import DEBUG, LINKEDIN_NAME, LINKEDIN_PASSWORD, LOGIN_URL
from playwright.async_api import Browser, async_playwright
from services import SimpleClient
from utils import check_sys_arg


async def start_activity(headless: bool, **kwargs) -> None:
    """
    Set up client and manager, then perform reposts.

    Args:
        headless (bool): Launch browser in headless mode if True.
        **kwargs: Additional parameters.
            restrict (int): Max number of posts to repost.

    Raises:
        Exception: If `restrict` is less than 1.
    """
    # TODO: bring out using factory pattern
    client = SimpleClient(LINKEDIN_NAME, LINKEDIN_PASSWORD, LOGIN_URL)
    manager = LNPostManager(client, LinkedInPostsParser)

    reposts_amount = kwargs.get('restrict', 0)
    if reposts_amount < 1:
        raise Exception('Reposts amount should be at least 1 or greater!')

    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=headless)
        await manager.make_reposts(browser, reposts_amount)

if __name__ == '__main__':
    # Parse CLI args and determine headless mode
    sys_args = check_sys_arg()
    head_off = True
    if sys_args.debug == 'true' or DEBUG == 'true':
        head_off = False

    asyncio.run(start_activity(head_off, restrict=sys_args.posts_restrict))
