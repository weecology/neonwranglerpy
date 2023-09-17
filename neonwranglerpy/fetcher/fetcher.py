"""fetcher is responsible for downloading data."""
import asyncio
import aiohttp
import os
from concurrent.futures import ThreadPoolExecutor
from os.path import join as pjoin
import requests
from itertools import repeat

if 'NEONWRANGLER_HOME' in os.environ:
    fury_home = os.environ['NEONWRANGLER_HOME']
else:
    fury_home = pjoin(os.path.expanduser('~'), '.neonwranglerpy')


async def _request(session, url):
    """Asynchronous function to get the request data as json.

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


async def _download(session, url, filename, sem, month, size=None):
    """Asynchronous function to download file from url.

    Parameters
    ----------
    session : ClientSession
        Aiohttp client session
    url : string
        The URL of the downloadable file
    filename : string
        Name of the downloaded file (e.g. BoxTextured.gltf)
    sem: asyncio.Semaphore
        It keeps tracks number of requests.
    size : int, optional
        Length of the content in bytes
    """
    # print(month)
    if not os.path.exists(filename):
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


async def _fetcher(data, rate_limit, headers, files_to_stack_path="filesToStack"):
    """Fetcher for downloading files."""
    sem = asyncio.Semaphore(rate_limit)
    data = data['data']
    dir_name = '.'.join(
        ['NEON', data['productCode'], data['siteCode'], data['month'], data['release']])
    zip_dir_path = os.path.join(files_to_stack_path, f'{dir_name}')
    if not os.path.isdir(zip_dir_path):
        os.mkdir(zip_dir_path)

    d_urls = [f['url'] for f in data["files"]]
    sizes = [f['size'] for f in data["files"]]
    f_names = [f['name'] for f in data["files"]]
    f_paths = [pjoin(zip_dir_path, name) for name in f_names]
    month = [data['month']]
    zip_url = zip(d_urls, f_paths, sizes)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url, name, sz in zip_url:
            task = asyncio.create_task(_download(session, url, name, sem, month, sz))
            tasks.append(task)

        await asyncio.gather(*tasks)


async def vst_fetcher(item, rate_limit, headers, files_to_stack_path="filesToStack"):
    """Vst fetcher gets the urls for the files of vst data."""
    data = requests.get(item).json()
    await _fetcher(data, rate_limit, headers, files_to_stack_path)


def fetcher(batch, data_type, rate_limit, headers, files_to_stack_path):
    """Fetcher calls the vst/aop fetcher according to use case."""
    try:
        if data_type == 'vst':
            asyncio.run(vst_fetcher(batch, rate_limit, headers, files_to_stack_path))
        elif data_type == 'aop':
            asyncio.run(_fetcher(batch, rate_limit, headers, files_to_stack_path))

    except Exception as e:
        print(f"Error processing URLs: {e}")


def run_threaded_batches(batches,
                         data_type,
                         rate_limit,
                         headers=None,
                         savepath='/filesToStack'):
    """Create batches and run the async fetchers."""
    num_cores = os.cpu_count()  # Get the number of CPU cores
    num_threads = min(
        num_cores, len(batches)
    )  # Limit threads to CPU cores or the number of batches, whichever is smaller

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for i in range(num_threads):
            # Distribute the batches evenly among threads
            batch = batches[i::int(num_threads)]
            # executor.submit(fetcher, batch, rate_limit, headers)
            executor.map(fetcher, batch, repeat(data_type), repeat(rate_limit),
                         repeat(headers), repeat(savepath))
