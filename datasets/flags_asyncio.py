import os
import time
import sys
import asyncio  

import aiohttp  


POP20_CC = ('CN IN US ID BR PK NG BD RU JP '
            'MX PH VN ET EG DE IR TR CD FR').split()

BASE_URL = 'http://flupy.org/data/flags'

DEST_DIR = 'downloads/'


def save_flag(img, filename):
    path = os.path.join(DEST_DIR, filename)
    with open(path, 'wb') as fp:
        fp.write(img)


async def get_flag(session, cc): 
    url = '{}/{cc}/{cc}.gif'.format(BASE_URL, cc=cc.lower())
    async with session.get(url) as resp:    
        return await resp.read() 


def show(text):
    print(text, end=' ')
    sys.stdout.flush()


async def download_one(session, cc):  
    image = await get_flag(session, cc)  
    show(cc)
    save_flag(image, cc.lower() + '.gif')
    return cc


async def download_many(cc_list):
    async with aiohttp.ClientSession() as session: 
        res = await asyncio.gather(               
            *[asyncio.create_task(download_one(session, cc))
                for cc in sorted(cc_list)])

    return len(res)


def main():
    t0 = time.time()
    count = asyncio.run(download_many(POP20_CC))
    elapsed = time.time() - t0
    msg = '\n{} flags downloaded in {:.2f}s'
    print(msg.format(count, elapsed))


if __name__ == '__main__':
    main()