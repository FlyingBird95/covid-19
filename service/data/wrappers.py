def with_retry(retry_function, max_retry=3, exceptions=Exception):
    """Calls a function and retries if it doesn't work.
    If it still fails after the max_retry, None is returned."""
    retry = 0

    while retry < max_retry:
        try:
            return retry_function()
        except exceptions:
            retry += 1
    return None
