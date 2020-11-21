import asyncio
import collections

import aiohttp
from aiohttp import web
import tqdm

from flags2_common import main, HTTPStatus, Result, save_flag

# default set low to avoid errors from remote site, such as
# 503 - Service Temporarily Unavailable
DEFAULT_CONCUR_REQ = 5
MAX_CONCUR_REQ = 1000


class FetchError(Exception):
    def __init__(self, country_code):
        self.country_code = country_code
        
        
async def get_flag(session, base_url, cc):
    url = '{}/{cc}/{cc}.gif'.format(base_url, cc=cc.lower())
    async with session.get(url) as resp:
        if resp.status == 200:
            return await resp.read()
            # 真正执行I/O操作的是最内层的普通的子生成器（通过yield from结构委托给asyncio包或第三方库中的协程）
        elif resp.status == 404:
            raise web.HTTPNotFound()
        else:
            raise aiohttp.HttpProcessingError(code=resp.status, message=resp.reason, header=resp.headers)


async def download_one(session, cc, base_url, semaphore, verbose):
    try:
        async with semaphore:
            image = await get_flag(session, base_url, cc)
    except web.HTTPNotFound:
        status = HTTPStatus.not_found
        msg = 'not found'
    except Exception as exc:
        raise FetchError(cc) from exc
    else:
        loop = asyncio.get_event_loop()
        # 获取事件循环的引用，它在背后维护着一个ThreadPoolExecutor实例
        loop.run_in_executor(None, save_flag, image, cc.lower() + '.gif')
        # 第一个参数是一个Executor实例，如果设为None，则使用事件循环默认的ThreadPoolExecutor实例。
        status = HTTPStatus.ok
        msg = 'OK'
    
    if verbose and msg:
        print(cc, msg)
        
    return Result(status, cc)
            
            
async def download_coro(cc_list, base_url, verbose, concur_req):
    counter = collections.Counter()
    semaphore = asyncio.Semaphore(concur_req)
    async with aiohttp.ClientSession() as session:
        to_do = [download_one(session, cc, base_url, semaphore, verbose) for cc in sorted(cc_list)]
            
        to_do_iter = asyncio.as_completed(to_do)
        if not verbose:
            to_do_iter = tqdm.tqdm(to_do_iter, total=len(cc_list))
            # 为了更新进度条，在future运行结束后立即获取结果   对不起我爱你
        for future in to_do_iter:
            try:
                res = await future
            except FetchError as exc:
                country_code = exc.country_code
                try:
                    error_msg = exc.__cause__.arg[0]
                except IndexError:
                    error_msg = exc.__cause__.__class__.__name__
                if verbose and error_msg:
                    msg = '*** Error for {}:{}'
                    print(msg.format(country_code, error_msg))
                status = HTTPStatus.error
            else:
                status = res.status
        
            counter[status] += 1
            
        return counter
                
                    
def download_many(cc_list, base_url, verbose, concur_req):
    loop = asyncio.get_event_loop()
    coro = download_coro(cc_list, base_url, verbose, concur_req)
    counts = loop.run_until_complete(coro)
    loop.close()
    return counts


if __name__ == '__main__':
    main(download_many, DEFAULT_CONCUR_REQ, MAX_CONCUR_REQ)