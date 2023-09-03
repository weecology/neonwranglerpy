import asyncio
import aiohttp
import os
from concurrent.futures import ThreadPoolExecutor
from os.path import join as pjoin, dirname


if 'NEONWRANGLER_HOME' in os.environ:
    fury_home = os.environ['NEONWRANGLER_HOME']
else:
    fury_home = pjoin(os.path.expanduser('~'), '.neonwranglerpy')


async def _request(session, url):
    """An asynchronous function to get the request data as json.

    Parameters
    ----------
    session : ClientSession
        Aiohttp client session.
    url : string
        The URL from which _request gets the response

    Returns
    -------
    response : dictionary
        The response of url request.
    """
    async with session.get(url) as response:
        if not response.status == 200:
            raise aiohttp.InvalidURL(url)

        return await response.json()


async def _download(session, url, filename, sem, size=None):
    """An asynchronous function to download file from url.

    Parameters
    ----------
    session : ClientSession
        Aiohttp client session
    url : string
        The URL of the downloadable file
    filename : string
        Name of the downloaded file (e.g. BoxTextured.gltf)
    size : int, optional
        Length of the content in bytes
    """
    if not os.path.exists(filename):
        print(f'Downloading: {filename}')
        async with sem:
            async with session.get(url) as response:
                size = response.content_length if not size else size
                block = size
                copied = 0
                with open(filename, mode='wb') as f:
                    async for chunk in response.content.iter_chunked(block):
                        f.write(chunk)
                        copied += len(chunk)
                        # progress = float(copied)/float(size)
                        # update_progressbar(progress, size)


async def _fetcher(batch, headers, rate_limit):
    """Fetcher for downloading files."""
    sem = asyncio.Semaphore(rate_limit)
    dir_name = '.'.join([
                'NEON', batch['productCode'], batch['siteCode'], batch['month'],
                batch['release']
            ])
    d_urls = [file['url'] for file in batch["files"]]
    sizes = [file['size'] for file in batch["files"]]
    f_names = [file['name'] for file in batch["files"]]
    f_paths = [pjoin(dir_name, name) for name in f_names]
    zip_url = zip(d_urls, f_paths, sizes)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url, name, sz in zip_url:
            task = asyncio.create_task(_download(session, url, name, sem, sz))
            tasks.append(task)

        await asyncio.gather(*tasks)


async def fetcher(batch, headers, rate_limit):
    try:
        asyncio.run(_fetcher(batch, headers, rate_limit))
    except Exception as e:
        print(f"Error processing URLs: {e}")


def run_threaded_batches(batches, headers, batch_size, rate_limit):
    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        for i in range(batch_size):
            batch = batches[i * batch_size : min((i + 1) * batch_size, len(batches))]
            executor.map(fetcher, range(batch_size), batch, headers, rate_limit)
