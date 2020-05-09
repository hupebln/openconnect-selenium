import asyncio
import logging

logger = logging.getLogger('oc.openconnect')


async def run_openconnect(host, cookie):
    cmd = [
        'sudo',
        'openconnect',
        '--protocol=nc',
        '--cookie={}'.format(cookie)
    ]
    logger.debug('executing "{}"'.format(' '.join(cmd)))
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        host,
        stdin=asyncio.subprocess.PIPE,
        stdout=None,
        stderr=None
    )

    await proc.wait()


async def stop_vpn(sig, loop):
    logger.info('received SIGNAL "{}"'.format(sig.name))
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()
