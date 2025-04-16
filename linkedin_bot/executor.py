#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

from bot import LinkedInPostsParser, PostManager
from config import DEBUG, LINKEDIN_NAME, LINKEDIN_PASSWORD, LOGIN_URL
from playwright.async_api import Browser, async_playwright
from services import SimpleClient
from utils import check_sys_arg


async def start_activity(headless: bool) -> None:
    # TODO: bring out using factory pattern
    client = SimpleClient(LINKEDIN_NAME, LINKEDIN_PASSWORD, LOGIN_URL)
    manager = PostManager(client, LinkedInPostsParser)

    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=headless)
        res = await manager.get_posts_id(browser)
        print(res)

if __name__ == "__main__":
    head_off = True
    if check_sys_arg().debug or DEBUG == "true":
        head_off = False

    asyncio.run(start_activity(head_off))
