import ephem
import datetime
import geocoder

def get_LatLng():
    g = geocoder.ip('me')
    latlng = g.latlng
    print("\n根据你的IP地址")
    # print("你所在城市为:\n" + g.city)
    print("你的经度为：\t%8.4f \n你的纬度为：\t%8.4f" % (latlng[1], latlng[0]))
    return latlng


lalo = get_LatLng()

gatech = ephem.Observer()
# gatech.pressure = 0
# gatech.horizon = '-0:34'
gatech.lon, gatech.lat = str(lalo[1]), str(lalo[0])
gatech.date = datetime.datetime.utcnow()
print("\n当前时间为:\n%s" % ephem.localtime(gatech.date))
sun, moon = ephem.Sun(), ephem.Moon()
sun.compute(gatech)
moon.compute(gatech)

previous_midnight = ephem.date(datetime.date.today())
next_midnight = ephem.date(datetime.date.today()) + 1


sun_rising = gatech.previous_rising(sun)
sun_rising_local = ephem.date(ephem.localtime(sun_rising))
sun_setting = gatech.next_setting(sun)
sun_setting_local = ephem.date(ephem.localtime(sun_setting))
sun_transit = gatech.previous_transit(sun)
sun_transit_local = ephem.date(ephem.localtime(sun_transit))

if sun_rising_local < previous_midnight:
    sun_rising = gatech.next_rising(sun)
if sun_setting_local > next_midnight:
    sun_setting = gatech.previous_setting(sun)
if sun_transit_local < previous_midnight:
    sun_transit = gatech.next_transit(sun)

print("太阳高度角: %s \n太阳方位角: %s" % (sun.alt, sun.az))
print("日出时间: %s \n日落时间: %s" % (ephem.localtime(sun_rising),
                                                ephem.localtime(sun_setting)))
print("太阳正午时间: %s" % ephem.localtime(sun_transit))


moon_rising = gatech.previous_rising(moon)
moon_rising_local = ephem.date(ephem.localtime(moon_rising))
moon_setting = gatech.next_setting(moon)
moon_setting_local = ephem.date(ephem.localtime(moon_setting))
moon_transit = gatech.previous_transit(moon)
moon_transit_local = ephem.date(ephem.localtime(moon_transit))

if moon_rising_local < previous_midnight:
    moon_rising = gatech.next_rising(moon)
if moon_setting_local > next_midnight:
    moon_setting = gatech.previous_setting(moon)
if moon_transit_local < previous_midnight:
    moon_transit = gatech.next_transit(moon)

print("月球高度角: %s \n月球方位角: %s" % (moon.alt, moon.az))
print("月出时间: %s \n月落时间: %s" % (ephem.localtime(moon_rising),
                                                ephem.localtime(moon_setting)))
print("月球当顶时间: %s" % ephem.localtime(moon_transit))
