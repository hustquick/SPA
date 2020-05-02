from SPA import *
from get_IP_LatLng import get_LatLng
from get_date_time import get_current_datetime

spa = spa_data()  # define a spa object

latlng = get_LatLng()
now = get_current_datetime()
print("")

year = now.date().year
# first_day = parse(str(year) + "/1/1")
# difference = now - first_day
# date = difference.days + 1
# time1 = now.time()
# hour = time1.hour + time1.minute / 60 + time1.second / 3600
# hour_angle = np.pi / 12 * (hour - 12)   # omega

spa.year = now.date().year
spa.month = now.date().month
spa.day = now.date().day
spa.hour = now.time().hour
spa.minute = now.time().minute
spa.second = now.time().second
spa.timezone = +8.0
spa.delta_ut1 = 0
""" Fractional second difference between UTC and UT which is used
    to adjust UTC for earth's irregular rotation rate and is derived 
    from observation only and is reported in this bulletin:
    http:##maia.usno.navy.mil/ser7/ser7.dat,
    where delta_ut1 = DUT1
    valid range: -1 to 1 second (exclusive)
"""
spa.delta_t = 67
""" Difference between earth rotation time and terrestrial time
    It is derived from observation only and is reported in this
    bulletin: http:##maia.usno.navy.mil/ser7/ser7.dat,
    where delta_t = 32.184 + (TAI-UTC) - DUT1
    valid range: -8000 to 8000 seconds
"""
spa.longitude = latlng[1]
spa.latitude = latlng[0]
spa.elevation = 10
spa.pressure = 760                  # Annual average local pressure [millibars], valid range: 0 to 5000 millibars
spa.temperature = 26                # Annual average local temperature [degrees Celsius], valid range: -273 to 6000
# degrees Celsius
spa.slope = 0                       # Surface slope (measured from the horizontal plane), valid range: -360 to 360
# degrees
spa.azm_rotation = -10              # Surface azimuth rotation (measured from south to projection of
# surface normal on horizontal plane, negative east) valid range: -360 to 360 degrees
spa.atmos_refract = 0.5667          # Atmospheric refraction at sunrise and sunset (0.5667 deg is typical)
# valid range: -5   to   5 degrees
spa.function = SPA_FUNC.SPA_ALL     # Switch to choose functions for desired output (from enumeration)

# call the SPA calculate function and pass the SPA structure

result = spa_calculate(spa)

if result == 0:  # check for SPA errors
    # display the results inside the SPA structure

    print("儒略日：        %.6f\n" % spa.jd)
    print("地球日心经度：   %.6f 度\n" % spa.l)
    print("地球日心纬度：   %.6e 度\n" % spa.b)
    print("地日距离：       %.6f 天文长度\n" % spa.r)
    print("观察者时角：     %.6f 度\n" % spa.h)
    print("章动经度：       %.6e 度\n" % spa.del_psi[0])
    print("章动倾斜角：     %.6e 度\n" % spa.del_epsilon[0])
    print("黄道倾斜度：     %.6f 度\n" % spa.epsilon)
    print("赤纬角：        %.6f 度\n" % spa.delta_prime[0])
    print("天顶角：        %.6f 度\n" % spa.zenith)
    print("高度角：        %.6f 度\n" % spa.e)
    print("方位角：        %.6f 度\n" % spa.azimuth)

    min = 60.0 * (spa.suntransit - int(spa.suntransit))
    sec = 60.0 * (min - int(min))
    print("太阳正午时间：   %02d:%02d:%02d 当地时间\n" % (int(spa.suntransit), int(min), int(sec)))

    min = 60.0 * (spa.sunrise - int(spa.sunrise))
    sec = 60.0 * (min - int(min))
    print("日出：          %02d:%02d:%02d 当地时间\n" % (int(spa.sunrise), int(min), int(sec)))

    min = 60.0 * (spa.sunset - int(spa.sunset))
    sec = 60.0 * (min - int(min))
    print("日落：          %02d:%02d:%02d 当地时间\n" % (int(spa.sunset), int(min), int(sec)))

else:
    print("SPA错误代码: %d\n" % result)
