import httpx
import logging

async def retrieve_resource_from_url(url, max_retry_times=5, proxy=None):
    # Creates an httpx client
    client = None
    if proxy:
        client = httpx.AsyncClient(http2=True, proxies= {
            'http://': proxy,
            'https://': proxy,
        })
    else: 
        client = httpx.AsyncClient(http2=True)
    
    response_header_state, byted_response_content = {'response_code': -1}, None

    num_retry = 0
    while num_retry < max_retry_times:
        try:
            # We start a request using the async context manager.
            async with client.stream("GET", url) as response:
                # Make sure the request was successful
                if response.status_code == 200:
                    # If successful, we read the response in chunks
                    byted_response_content = await response.aread()
                    response_header_state = {
                        'response_code': response.status_code,
                        'response_headers': dict(response.headers),
                        'content_length': len(byted_response_content)
                    }
                    return response_header_state, byted_response_content

        except httpx.RequestError as exc:
            logging.debug(f'request failed: {url}, and caused reason is {str(exc)}')

        num_retry += 1

    client.close()
    return response_header_state, None
