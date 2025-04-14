#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import asyncio
import random
import sys

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page
)

from config import DEBUG, LINKEDIN_NAME, LINKEDIN_PASSWORD, logger_dbg
from utils import check_sys_arg
from .bs_parser import PageParser, LinkedInLoginFormParser


USER_AGENTS = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/91.0.864.59 Safari/537.36 Edg/91.0.864.59',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
    ' (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 OPR/76.0.4017.177',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Vivaldi/4.0'
)


class LinkedInClient:
    __slots__ = ('signup_url', 'name', 'password')

    def __init__(self, name: str, password: str) -> None:
        self.name = name
        self.password = password
        self.signup_url = 'https://www.linkedin.com/login/ru?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'

    @staticmethod
    async def get_and_fill_login_form(page_content: str, parser: PageParser):
        return parser.parse_signin_page(page_content)

    @staticmethod
    async def create_context(browser: Browser) -> BrowserContext:
        user_agent = random.choice(USER_AGENTS)
        return await browser.new_context(java_script_enabled=True, user_agent=user_agent)

    @staticmethod
    async def get_page_content(page: Page, url: str) -> str:
        await page.goto(url)
        await page.wait_for_load_state('load')
        return await page.content()

    async def start_webdriver(self, parser: PageParser) -> None:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=False)
            context = await self.create_context(browser)
            page = await context.new_page()
            content = await self.get_page_content(page, self.signup_url)

            filled_form = await self.get_and_fill_login_form(content, parser)


async def main():
    parser = LinkedInLoginFormParser
    client = LinkedInClient(LINKEDIN_NAME, LINKEDIN_PASSWORD)
    await client.start_webdriver(parser)


if __name__ == '__main__':

    if check_sys_arg().debug or DEBUG == 'true':
        print('DEBUG IS ON')
        logger_dbg.debug('debug is on.')
        sys.exit(1)

    print('DEBUG IS OFF')

    asyncio.run(main())
