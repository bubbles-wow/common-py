import time
import string
import base64
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
    log_info = f"url={url}, method={method}, params={params}, json={json}, "
    if isinstance(data, str):
        log_info += f"data={data}, "
    if isinstance(data, bytes) and str(data).isprintable():
        log_info += f"data={data.decode()}, "
    else:
        log_info += f"data_base64={base64.b64encode(data).decode()}..." if data else "data=None"
    log_info += f", **kwargs={kwargs}"
    for retry_time in range(retries):
        try:
            response = session.request(method=method, url=url, params=params, data=data, json=json, timeout=timeout, **kwargs)
            if response.status_code != target_status:
                raise ValueError(f"Unexpected status code: {response.status_code}")
            
            if data_verify and not data_verify(response):
                log_info_dv = log_info + f", target_status={target_status}"
                if isinstance(response.content, str):
                    log_info_dv += f", response_content={response.content}"
                elif isinstance(response.content, bytes) and str(response.content).isprintable():
                    log_info_dv += f", response_content={response.content.decode()}"
                else:
                    log_info_dv += f", response_content_base64={base64.b64encode(response.content).decode()}..."
                logger.warning(93, f"Data verification failed for response. ({log_info_dv})")
                return None
            
            return response
        except Exception as e:
            log_info_exception = log_info + f", target_status={target_status}"
            local_response = locals().get("response")
            if isinstance(local_response, Response):
                if isinstance(response.content, str):
                    log_info_exception += f", response_content={response.content}"
                elif isinstance(response.content, bytes) and str(response.content).isprintable():
                    log_info_exception += f", response_content={response.content.decode()}"
                else:
                    log_info_exception += f", response_content_base64={base64.b64encode(response.content).decode()}..."
            log_info_exception += f", exception={e}"
            if retry_time + 1 >= retries:
                logger.error(91, f"Error fetching request, attempt {retry_time + 1}. ({log_info_exception})")
            else:
                logger.warning(92, f"Retrying request, attempt {retry_time + 1}. ({log_info_exception})")
                time.sleep(random.randint(0, 3000) / 1000.0)
    return None
