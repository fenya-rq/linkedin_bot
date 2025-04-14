import sys

from config import DEBUG, LINKEDIN_NAME, LINKEDIN_PASSWORD, logger_dbg, logger_prd
from utils import check_sys_arg
from bot import main


async def start_activity():
    await main()


if __name__ == '__main__':

    if check_sys_arg().debug or DEBUG == 'true':
        print('DEBUG IS ON')
        logger_dbg.debug('debug is on.')
        sys.exit(1)

    print('DEBUG IS OFF')

    asyncio.run(start_activity())
