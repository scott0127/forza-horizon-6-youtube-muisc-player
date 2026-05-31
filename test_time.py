import asyncio
import winsdk.windows.media.control as wmc
import datetime

async def m():
    mgr = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
    s = mgr.get_current_session()
    t = s.get_timeline_properties()
    print(repr(t.last_updated_time))
    print(t.last_updated_time.timestamp())
    print(datetime.datetime.now(datetime.timezone.utc).timestamp())

asyncio.run(m())
