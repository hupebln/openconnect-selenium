import asyncio
import logging

logger = logging.getLogger('oc.openconnect')


async def run_openconnect(host, cookie, verbose):
    cmd = [
        'sudo',
        'openconnect'
    ]

    if verbose:
        cmd.append('-{}'.format('v' * verbose))

    cmd.extend(
        [
            '--protocol=nc',
            '--cookie={}'.format(cookie)
        ]
    )

    logger.debug('executing "{} {}"'.format(' '.join(cmd), host))
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
    tasks = [t for t in asyncio.Task.all_tasks() if t is not asyncio.Task.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()
