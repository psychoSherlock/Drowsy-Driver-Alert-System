import winsdk.windows.devices.geolocation as wdg
import asyncio


async def getCoords():
    locator = wdg.Geolocator()
    pos = await locator.get_geoposition_async()
    return [pos.coordinate.latitude, pos.coordinate.longitude]


def getLoc():
    return asyncio.run(getCoords())


location = getLoc()
lat = location[0]
lon = location[1]
print(lat)
print(lon)
