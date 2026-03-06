import time
import random

from typing import Any, Callable, Optional
from requests import Session, Response
from logging import Logger

def request(
    logger: Logger, 
    session: Session, 
    method: str, 
    url: str, 
    params: Optional[dict | bytes] = None,
    data: Optional[Any] = None,
    json: Optional[dict] = None,
    target_status: int = 200,
    retries: int = 3, 
    timeout: int = 5,
    data_verify: Optional[Callable[[Response], bool]] = None, 
    **kwargs
) -> Response | None:
    for retry_time in range(retries):
        try:
            response = session.request(method=method, url=url, params=params, data=data, json=json, timeout=timeout, **kwargs)
            if response.status_code != target_status:
                raise ValueError(f"Unexpected status code: {response.status_code}")
            
            if data_verify and not data_verify(response):
                return None
            
            return response
        except Exception as e:
            if retry_time + 1 >= retries:
                logger.error(91, f"Error fetching request, attempt {retry_time + 1}. (url={url}, method={method}, params={params}, data={data}, json={json}, exception={e})")
            else:
                logger.warning(92, f"Retrying request, attempt {retry_time + 1}. (url={url}, method={method}, params={params}, data={data}, json={json}, exception={e})")
                time.sleep(random.randint(0, 3000) / 1000.0)
    return None
