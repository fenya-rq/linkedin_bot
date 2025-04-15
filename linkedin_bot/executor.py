#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

import asyncio
from playwright.async_api import async_playwright, Browser

from bot import LoginManager
from config import DEBUG, LINKEDIN_NAME, LINKEDIN_PASSWORD, LOGIN_URL, logger_dbg
from services import SimpleClient
from utils import check_sys_arg


async def start_activity(headless: bool) -> None:
    # TODO: bring out using factory pattern
    client = SimpleClient(LINKEDIN_NAME, LINKEDIN_PASSWORD, LOGIN_URL)
    manager = LoginManager(client)

    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=headless)
        await manager.start_manage(browser)


if __name__ == '__main__':
    head_off = True
    if check_sys_arg().debug or DEBUG == 'true':
        head_off = False

    asyncio.run(start_activity(head_off))
