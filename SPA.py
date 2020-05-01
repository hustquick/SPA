"""
      Solar Position Algorithm (SPA)     
                   for                   
        Solar Radiation Application      
   NOTICE
   Copyright (C) 2008-2011 Alliance for Sustainable Energy, LLC, All Rights Reserved

The Solar Position Algorithm ("Software") is code in development prepared by employees of the
Alliance for Sustainable Energy, LLC, (hereinafter the "Contractor"), under Contract No.
DE-AC36-08GO28308 ("Contract") with the U.S. Department of Energy (the "DOE"). The United
States Government has been granted for itself and others acting on its behalf a paid-up, non-
exclusive, irrevocable, worldwide license in the Software to reproduce, prepare derivative
works, and perform publicly and display publicly. Beginning five (5) years after the date
permission to assert copyright is obtained from the DOE, and subject to any subsequent five
(5) year renewals, the United States Government is granted for itself and others acting on
its behalf a paid-up, non-exclusive, irrevocable, worldwide license in the Software to
reproduce, prepare derivative works, distribute copies to the public, perform publicly and
display publicly, and to permit others to do so. If the Contractor ceases to make this
computer software available, it may be obtained from DOE's Office of Scientific and Technical
Information's Energy Science and Technology Software Center (ESTSC) at P.O. Box 1020, Oak
Ridge, TN 37831-1020. THIS SOFTWARE IS PROVIDED BY THE CONTRACTOR "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE CONTRACTOR OR THE
U.S. GOVERNMENT BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER, INCLUDING BUT NOT LIMITED TO CLAIMS ASSOCIATED WITH THE LOSS OF DATA OR PROFITS,
WHICH MAY RESULT FROM AN ACTION IN CONTRACT, NEGLIGENCE OR OTHER TORTIOUS CLAIM THAT ARISES
OUT OF OR IN CONNECTION WITH THE ACCESS, USE OR PERFORMANCE OF THIS SOFTWARE.

The Software is being provided for internal, noncommercial purposes only and shall not be
re-distributed. Please contact the NREL Commercialization and Technology Transfer Office
for information concerning a commercial license to use the Software, visit:
http:midcdmz.nrel.gov/spa/ for the contact information.

As a condition of using the Software in an application, the developer of the application
agrees to reference the use of the Software and make this Notice readily accessible to any
end-user in a Help|About screen or equivalent manner.
"""

import numpy as np
from enum import Enum
from copy import deepcopy

PI = np.pi
SUN_RADIUS = 0.26667

L_COUNT = 6
B_COUNT = 2
R_COUNT = 5
Y_COUNT = 63

L_MAX_SUBCOUNT = 64
B_MAX_SUBCOUNT = 5
R_MAX_SUBCOUNT = 40

class spa_data():
        ##----------------------INPUT VALUES------------------------
    year = None            ## 4-digit year,      valid range: -2000 to 6000, error code: 1
    month = None          ## 2-digit month,         valid range: 1 to  12,  error code: 2
    day = None            ## 2-digit day,           valid range: 1 to  31,  error code: 3
    hour = None           ## Observer local hour,   valid range: 0 to  24,  error code: 4
    minute = None         ## Observer local minute, valid range: 0 to  59,  error code: 5
    second = None      ## Observer local second, valid range: 0 to <60,  error code: 6
	
    delta_ut1 = None    ## Fractional second difference between UTC and UT which is used
                         ## to adjust UTC for earth's irregular rotation rate and is derived
	                     ## from observation only and is reported in this bulletin:
	                     ## http:##maia.usno.navy.mil/ser7/ser7.dat,
	                     ## where delta_ut1 = DUT1
	                     ## valid range: -1 to 1 second (exclusive), error code 17

    delta_t = None     ## Difference between earth rotation time and terrestrial time
                         ## It is derived from observation only and is reported in this
                         ## bulletin: http:##maia.usno.navy.mil/ser7/ser7.dat,
                         ## where delta_t = 32.184 + (TAI-UTC) - DUT1
                         ## valid range: -8000 to 8000 seconds, error code: 7

    timezone = None    ## Observer time zone (negative west of Greenwich)
                         ## valid range: -18   to   18 hours,   error code: 8

    longitude = None   ## Observer longitude (negative west of Greenwich)
                         ## valid range: -180  to  180 degrees, error code: 9

    latitude = None    ## Observer latitude (negative south of equator)
                         ## valid range: -90   to   90 degrees, error code: 10

    elevation = None   ## Observer elevation [meters]
                         ## valid range: -6500000 or higher meters,    error code: 11

    pressure = None    ## Annual average local pressure [millibars]
                         ## valid range:    0 to 5000 millibars,       error code: 12

    temperature = None  ## Annual average local temperature [degrees Celsius]
                         ## valid range: -273 to 6000 degrees Celsius, error code 13

    slope = None       ## Surface slope (measured from the horizontal plane)
                         ## valid range: -360 to 360 degrees, error code: 14

    azm_rotation = None ## Surface azimuth rotation (measured from south to projection of
                         ##     surface normal on horizontal plane, negative east)
                         ## valid range: -360 to 360 degrees, error code: 15

    atmos_refract = None ## Atmospheric refraction at sunrise and sunset (0.5667 deg is typical)
                         ## valid range: -5   to   5 degrees, error code: 16

    function = None       ## Switch to choose functions for desired output (from enumeration)

    ##-----------------Intermediate OUTPUT VALUES--------------------

    jd = None         ##Julian day
    jc = None         ##Julian century

    jde = None        ##Julian ephemeris day
    jce = None        ##Julian ephemeris century
    jme = None        ##Julian ephemeris millennium

    l = None          ##earth heliocentric longitude [degrees]
    b = None          ##earth heliocentric latitude [degrees]
    r = None          ##earth radius vector [Astronomical Units, AU]

    theta = None      ##geocentric longitude [degrees]
    beta = None       ##geocentric latitude [degrees]

    x0 = None         ##mean elongation (moon-sun) [degrees]
    x1 = None         ##mean anomaly (sun) [degrees]
    x2 = None         ##mean anomaly (moon) [degrees]
    x3 = None         ##argument latitude (moon) [degrees]
    x4 = None         ##ascending longitude (moon) [degrees]

    del_psi = np.array([0.0])    ##nutation longitude [degrees]
    del_epsilon = np.array([0.0])  ##nutation obliquity [degrees]
    epsilon0 = None   ##ecliptic mean obliquity [arc seconds]
    epsilon = None    ##ecliptic true obliquity  [degrees]

    del_tau = None    ##aberration correction [degrees]
    lamda = None      ##apparent sun longitude [degrees]
    nu0 = None        ##Greenwich mean sidereal time [degrees]
    nu = None         ##Greenwich sidereal time [degrees]

    alpha = None      ##geocentric sun right ascension [degrees]
    delta = None      ##geocentric sun declination [degrees]

    h = None          ##observer hour angle [degrees]
    xi = None         ##sun equatorial horizontal parallax [degrees]
    del_alpha = np.array([0.0])  ##sun right ascension parallax [degrees]
    delta_prime = np.array([0.0]) ##topocentric sun declination [degrees]
    alpha_prime = None ##topocentric sun right ascension [degrees]
    h_prime = None    ##topocentric local hour angle [degrees]

    e0 = None         ##topocentric elevation angle (uncorrected) [degrees]
    del_e = None      ##atmospheric refraction correction [degrees]
    e = None          ##topocentric elevation angle (corrected) [degrees]

    eot = None        ##equation of time [minutes]
    srha = None       ##sunrise hour angle [degrees]
    ssha = None       ##sunset hour angle [degrees]
    sta = None        ##sun transit altitude [degrees]

    ##---------------------Final OUTPUT VALUES------------------------

    zenith = None      ##topocentric zenith angle [degrees]
    azimuth_astro = None##topocentric azimuth angle (westward from south) [for astronomers]
    azimuth = None     ##topocentric azimuth angle (eastward from north) [for navigators and solar radiation]
    incidence = None   ##surface incidence angle [degrees]

    suntransit = None   ##local sun transit time (or solar noon) [fractional hour]
    sunrise = None     ##local sunrise time (+/- 30 seconds) [fractional hour]
    sunset = None      ##local sunset time (+/- 30 seconds) [fractional hour]



class SPA_FUNC(Enum):
    SPA_ZA = 0      # calculate zenith and azimuth
    SPA_ZA_INC = 1  # calculate zenith, azimuth, and incidence
    SPA_ZA_RTS = 2  # calculate zenith, azimuth, and sun rise / transit / set values
    SPA_ALL = 3     # calculate all SPA output values

class TERM(Enum):
    A = 0
    B = 1
    C = 2
    COUNT = 3

class TERM_X(Enum):
    X0 = 0
    X1 = 1
    X2 = 2
    X3 = 3
    X4 = 4
    COUNT = 5
    Y_COUNT = COUNT

class TERM_P(Enum):
    PSI_A = 0
    PSI_B = 1
    EPS_C = 2
    EPS_D = 3
    PE_COUNT = 4

class JD(Enum):
    MINUS = 0
    ZERO = 1
    PLUS = 2
    COUNT = 3

class SUN(Enum):
    TRANSIT = 0
    RISE = 1
    SET = 2
    COUNT = 3

# enum {TERM_X0, TERM_X1, TERM_X2, TERM_X3, TERM_X4, TERM_X_COUNT}
# enum {TERM_PSI_A, TERM_PSI_B, TERM_EPS_C, TERM_EPS_D, TERM_PE_COUNT}
# enum {JD_MINUS, JD_ZERO, JD_PLUS, JD_COUNT}
# enum {SUN_TRANSIT, SUN_RISE, SUN_SET, SUN_COUNT}

l_subcount = [64, 34, 20, 7, 3, 1]
b_subcount = [5, 2]
r_subcount = [40, 10, 6, 2, 1]

############################
### Earth Periodic Terms
############################

L_TERMS = [
    [
        [175347046.0,0,0],
        [3341656.0,4.6692568,6283.07585],
        [34894.0,4.6261,12566.1517],
        [3497.0,2.7441,5753.3849],
        [3418.0,2.8289,3.5231],
        [3136.0,3.6277,77713.7715],
        [2676.0,4.4181,7860.4194],
        [2343.0,6.1352,3930.2097],
        [1324.0,0.7425,11506.7698],
        [1273.0,2.0371,529.691],
        [1199.0,1.1096,1577.3435],
        [990,5.233,5884.927],
        [902,2.045,26.298],
        [857,3.508,398.149],
        [780,1.179,5223.694],
        [753,2.533,5507.553],
        [505,4.583,18849.228],
        [492,4.205,775.523],
        [357,2.92,0.067],
        [317,5.849,11790.629],
        [284,1.899,796.298],
        [271,0.315,10977.079],
        [243,0.345,5486.778],
        [206,4.806,2544.314],
        [205,1.869,5573.143],
        [202,2.458,6069.777],
        [156,0.833,213.299],
        [132,3.411,2942.463],
        [126,1.083,20.775],
        [115,0.645,0.98],
        [103,0.636,4694.003],
        [102,0.976,15720.839],
        [102,4.267,7.114],
        [99,6.21,2146.17],
        [98,0.68,155.42],
        [86,5.98,161000.69],
        [85,1.3,6275.96],
        [85,3.67,71430.7],
        [80,1.81,17260.15],
        [79,3.04,12036.46],
        [75,1.76,5088.63],
        [74,3.5,3154.69],
        [74,4.68,801.82],
        [70,0.83,9437.76],
        [62,3.98,8827.39],
        [61,1.82,7084.9],
        [57,2.78,6286.6],
        [56,4.39,14143.5],
        [56,3.47,6279.55],
        [52,0.19,12139.55],
        [52,1.33,1748.02],
        [51,0.28,5856.48],
        [49,0.49,1194.45],
        [41,5.37,8429.24],
        [41,2.4,19651.05],
        [39,6.17,10447.39],
        [37,6.04,10213.29],
        [37,2.57,1059.38],
        [36,1.71,2352.87],
        [36,1.78,6812.77],
        [33,0.59,17789.85],
        [30,0.44,83996.85],
        [30,2.74,1349.87],
        [25,3.16,4690.48]
    ],
    [
        [628331966747.0,0,0],
        [206059.0,2.678235,6283.07585],
        [4303.0,2.6351,12566.1517],
        [425.0,1.59,3.523],
        [119.0,5.796,26.298],
        [109.0,2.966,1577.344],
        [93,2.59,18849.23],
        [72,1.14,529.69],
        [68,1.87,398.15],
        [67,4.41,5507.55],
        [59,2.89,5223.69],
        [56,2.17,155.42],
        [45,0.4,796.3],
        [36,0.47,775.52],
        [29,2.65,7.11],
        [21,5.34,0.98],
        [19,1.85,5486.78],
        [19,4.97,213.3],
        [17,2.99,6275.96],
        [16,0.03,2544.31],
        [16,1.43,2146.17],
        [15,1.21,10977.08],
        [12,2.83,1748.02],
        [12,3.26,5088.63],
        [12,5.27,1194.45],
        [12,2.08,4694],
        [11,0.77,553.57],
        [10,1.3,6286.6],
        [10,4.24,1349.87],
        [9,2.7,242.73],
        [9,5.64,951.72],
        [8,5.3,2352.87],
        [6,2.65,9437.76],
        [6,4.67,4690.48]
    ],
    [
        [52919.0,0,0],
        [8720.0,1.0721,6283.0758],
        [309.0,0.867,12566.152],
        [27,0.05,3.52],
        [16,5.19,26.3],
        [16,3.68,155.42],
        [10,0.76,18849.23],
        [9,2.06,77713.77],
        [7,0.83,775.52],
        [5,4.66,1577.34],
        [4,1.03,7.11],
        [4,3.44,5573.14],
        [3,5.14,796.3],
        [3,6.05,5507.55],
        [3,1.19,242.73],
        [3,6.12,529.69],
        [3,0.31,398.15],
        [3,2.28,553.57],
        [2,4.38,5223.69],
        [2,3.75,0.98]
    ],
    [
        [289.0,5.844,6283.076],
        [35,0,0],
        [17,5.49,12566.15],
        [3,5.2,155.42],
        [1,4.72,3.52],
        [1,5.3,18849.23],
        [1,5.97,242.73]
    ],
    [
        [114.0,3.142,0],
        [8,4.13,6283.08],
        [1,3.84,12566.15]
    ],
    [
        [1,3.14,0]
    ]
]

B_TERMS = [
    [
        [280.0,3.199,84334.662],
        [102.0,5.422,5507.553],
        [80,3.88,5223.69],
        [44,3.7,2352.87],
        [32,4,1577.34]
    ],
    [
        [9,3.9,5507.55],
        [6,1.73,5223.69]
    ]
]

R_TERMS = [
    [
        [100013989.0,0,0],
        [1670700.0,3.0984635,6283.07585],
        [13956.0,3.05525,12566.1517],
        [3084.0,5.1985,77713.7715],
        [1628.0,1.1739,5753.3849],
        [1576.0,2.8469,7860.4194],
        [925.0,5.453,11506.77],
        [542.0,4.564,3930.21],
        [472.0,3.661,5884.927],
        [346.0,0.964,5507.553],
        [329.0,5.9,5223.694],
        [307.0,0.299,5573.143],
        [243.0,4.273,11790.629],
        [212.0,5.847,1577.344],
        [186.0,5.022,10977.079],
        [175.0,3.012,18849.228],
        [110.0,5.055,5486.778],
        [98,0.89,6069.78],
        [86,5.69,15720.84],
        [86,1.27,161000.69],
        [65,0.27,17260.15],
        [63,0.92,529.69],
        [57,2.01,83996.85],
        [56,5.24,71430.7],
        [49,3.25,2544.31],
        [47,2.58,775.52],
        [45,5.54,9437.76],
        [43,6.01,6275.96],
        [39,5.36,4694],
        [38,2.39,8827.39],
        [37,0.83,19651.05],
        [37,4.9,12139.55],
        [36,1.67,12036.46],
        [35,1.84,2942.46],
        [33,0.24,7084.9],
        [32,0.18,5088.63],
        [32,1.78,398.15],
        [28,1.21,6286.6],
        [28,1.9,6279.55],
        [26,4.59,10447.39]
    ],
    [
        [103019.0,1.10749,6283.07585],
        [1721.0,1.0644,12566.1517],
        [702.0,3.142,0],
        [32,1.02,18849.23],
        [31,2.84,5507.55],
        [25,1.32,5223.69],
        [18,1.42,1577.34],
        [10,5.91,10977.08],
        [9,1.42,6275.96],
        [9,0.27,5486.78]
    ],
    [
        [4359.0,5.7846,6283.0758],
        [124.0,5.579,12566.152],
        [12,3.14,0],
        [9,3.63,77713.77],
        [6,1.87,5573.14],
        [3,5.47,18849.23]
    ],
    [
        [145.0,4.273,6283.076],
        [7,3.92,12566.15]
    ],
    [
        [4,2.56,6283.08]
    ]
]


############################
### Periodic Terms for the nutation in longitude and obliquity
############################

Y_TERMS = [
    [0,0,0,0,1],
    [-2,0,0,2,2],
    [0,0,0,2,2],
    [0,0,0,0,2],
    [0,1,0,0,0],
    [0,0,1,0,0],
    [-2,1,0,2,2],
    [0,0,0,2,1],
    [0,0,1,2,2],
    [-2,-1,0,2,2],
    [-2,0,1,0,0],
    [-2,0,0,2,1],
    [0,0,-1,2,2],
    [2,0,0,0,0],
    [0,0,1,0,1],
    [2,0,-1,2,2],
    [0,0,-1,0,1],
    [0,0,1,2,1],
    [-2,0,2,0,0],
    [0,0,-2,2,1],
    [2,0,0,2,2],
    [0,0,2,2,2],
    [0,0,2,0,0],
    [-2,0,1,2,2],
    [0,0,0,2,0],
    [-2,0,0,2,0],
    [0,0,-1,2,1],
    [0,2,0,0,0],
    [2,0,-1,0,1],
    [-2,2,0,2,2],
    [0,1,0,0,1],
    [-2,0,1,0,1],
    [0,-1,0,0,1],
    [0,0,2,-2,0],
    [2,0,-1,2,1],
    [2,0,1,2,2],
    [0,1,0,2,2],
    [-2,1,1,0,0],
    [0,-1,0,2,2],
    [2,0,0,2,1],
    [2,0,1,0,0],
    [-2,0,2,2,2],
    [-2,0,1,2,1],
    [2,0,-2,0,1],
    [2,0,0,0,1],
    [0,-1,1,0,0],
    [-2,-1,0,2,1],
    [-2,0,0,0,1],
    [0,0,2,2,1],
    [-2,0,2,0,1],
    [-2,1,0,2,1],
    [0,0,1,-2,0],
    [-1,0,1,0,0],
    [-2,1,0,0,0],
    [1,0,0,0,0],
    [0,0,1,2,0],
    [0,0,-2,2,2],
    [-1,-1,1,0,0],
    [0,1,1,0,0],
    [0,-1,1,2,2],
    [2,-1,-1,2,2],
    [0,0,3,2,2],
    [2,-1,0,2,2],
]

PE_TERMS = [
    [-171996,-174.2,92025,8.9],
    [-13187,-1.6,5736,-3.1],
    [-2274,-0.2,977,-0.5],
    [2062,0.2,-895,0.5],
    [1426,-3.4,54,-0.1],
    [712,0.1,-7,0],
    [-517,1.2,224,-0.6],
    [-386,-0.4,200,0],
    [-301,0,129,-0.1],
    [217,-0.5,-95,0.3],
    [-158,0,0,0],
    [129,0.1,-70,0],
    [123,0,-53,0],
    [63,0,0,0],
    [63,0.1,-33,0],
    [-59,0,26,0],
    [-58,-0.1,32,0],
    [-51,0,27,0],
    [48,0,0,0],
    [46,0,-24,0],
    [-38,0,16,0],
    [-31,0,13,0],
    [29,0,0,0],
    [29,0,-12,0],
    [26,0,0,0],
    [-22,0,0,0],
    [21,0,-10,0],
    [17,-0.1,0,0],
    [16,0,-8,0],
    [-16,0.1,7,0],
    [-15,0,9,0],
    [-13,0,7,0],
    [-12,0,6,0],
    [11,0,0,0],
    [-10,0,5,0],
    [-8,0,3,0],
    [7,0,-3,0],
    [-7,0,0,0],
    [-7,0,3,0],
    [-7,0,3,0],
    [6,0,0,0],
    [6,0,-3,0],
    [6,0,-3,0],
    [-6,0,3,0],
    [-6,0,3,0],
    [5,0,0,0],
    [-5,0,3,0],
    [-5,0,3,0],
    [-5,0,3,0],
    [4,0,0,0],
    [4,0,0,0],
    [4,0,0,0],
    [-4,0,0,0],
    [-4,0,0,0],
    [-4,0,0,0],
    [3,0,0,0],
    [-3,0,0,0],
    [-3,0,0,0],
    [-3,0,0,0],
    [-3,0,0,0],
    [-3,0,0,0],
    [-3,0,0,0],
    [-3,0,0,0],
]

def limit_degrees(degrees):
    degrees /= 360
    limited = 360 * (degrees - np.floor(degrees))
    if limited < 0:
        limited += 360
    return limited

def limit_degrees180pm(degrees):
    degrees /= 360
    limited = 360 * (degrees - np.floor(degrees))
    if limited < -180:
        limited += 360
    elif limited > 180:
        limited -= 360
    return limited

def limit_degrees180(degrees):
    degrees /= 180
    limited = 180 * (degrees - np.floor(degrees))
    if limited < 0:
        limited += 180
    return limited

def limit_zero2one(value):
    limited = value - np.floor(value)
    if limited < 0:
        limited += 1
    return limited

def limit_minutes(minutes):
    limited = minutes
    if limited < -20:
        limited += 1440
    elif limited > 20:
        limited -= 1440
    return limited

def dayfrac_to_local_hr(dayfrac, timezone):
    return 24.0*limit_zero2one(dayfrac + timezone/24.0)

def third_order_polynomial(a, b, c, d, x):
    return ((a*x + b)*x + c)*x + d

################################

def validate_inputs(spa):
    if spa.year < -2000 or spa.year > 6000:
        return 1
    if spa.month < 1 or spa.month > 12:
        return 2
    if spa.day < 1 or spa.day > 31:
        return 3
    if spa.hour < 0 or spa.hour > 24:
        return 4
    if spa.minute < 0 or spa.minute > 59:
        return 5
    if spa.second < 0 or spa.second >= 60:
        return 6
    if spa.pressure < 0 or spa.pressure > 5000:
        return 12
    if spa.temperature <= -273 or spa.temperature > 6000:
        return 13
    if spa.delta_ut1 <= -1 or spa.delta_ut1 >= 1:
        return 17
    if spa.hour == 24 and spa.minute > 0:
        return 5
    if spa.hour == 24 and spa.second > 0:
        return 6

    if abs(spa.delta_t) > 8000:
        return 7
    if abs(spa.timezone) > 18:
        return 8
    if abs(spa.longitude) > 180:
        return 9
    if abs(spa.latitude) > 90:
        return 10
    if abs(spa.atmos_refract) > 6:
        return 16
    if spa.elevation < -6500000:
        return 11
    if (spa.function == SPA_FUNC.SPA_ZA_INC) or (spa.function == SPA_FUNC.SPA_ALL):
        if abs(spa.slope) > 360:
            return 14
        if abs(spa.azm_rotation) > 360:
            return 15

    return 0

def julian_day(year, month, day, hour, minute, second, dut1, tz):
    day_decimal = day + (hour - tz +
                         (minute + (second + dut1) / 60) / 60) /24
    if month < 3:
        month += 12
        year -= 1

    julian_day = int(365.25*(year+4716)) + int(30.6001*(month+1)) + \
                 day_decimal - 1524.5

    if julian_day > 2299160:
        a = int(year/100)
        julian_day += (2 - a + int(a/4))

    return julian_day

def julian_century(jd):
    return (jd-2451545.0)/36525.0

def julian_ephemeris_day(jd, delta_t):
    return jd+delta_t/86400.0

def julian_ephemeris_century(jde):
    return (jde - 2451545.0)/36525.0

def julian_ephemeris_millennium(jce):
    return (jce/10.0)

def earth_periodic_term_summation(terms, count, jme):
    sum = 0
    for i in range(count):
        sum += terms[i][TERM.A.value]*np.cos(terms[i][TERM.B.value]+terms[i][TERM.C.value]*jme)
    return sum

def earth_values(term_sum, count, jme):
    sum=0
    for i in range(count):
        sum += term_sum[i]*np.power(jme, i)
    sum /= 1.0e8
    return sum

def earth_heliocentric_longitude(jme):
    sum = np.zeros(L_COUNT)
    for i in range(L_COUNT):
        sum[i] = earth_periodic_term_summation(L_TERMS[i], l_subcount[i], jme)
    return limit_degrees(np.rad2deg(earth_values(sum, L_COUNT, jme)))

def earth_heliocentric_latitude(jme):
    sum = np.zeros(B_COUNT)
    for i in range(B_COUNT):
        sum[i] = earth_periodic_term_summation(B_TERMS[i], b_subcount[i], jme)
    return np.rad2deg(earth_values(sum, B_COUNT, jme))


def earth_radius_vector(jme):
    sum = np.zeros(R_COUNT)
    for i in range(R_COUNT):
        sum[i] = earth_periodic_term_summation(R_TERMS[i], r_subcount[i], jme)
    return earth_values(sum, R_COUNT, jme)

def geocentric_longitude(l):
    theta = l + 180.0
    if theta >= 360.0:
        theta -= 360.0
    return theta

def geocentric_latitude(b):
    return -b

def mean_elongation_moon_sun(jce):
    return third_order_polynomial(1.0/189474.0, -0.0019142, 445267.11148, 297.85036, jce)

def mean_anomaly_sun(jce):
    return third_order_polynomial(-1.0/300000.0, -0.0001603, 35999.05034, 357.52772, jce)

def mean_anomaly_moon(jce):
    return third_order_polynomial(1.0/56250.0, 0.0086972, 477198.867398, 134.96298, jce)

def argument_latitude_moon(jce):
    return third_order_polynomial(1.0/327270.0, -0.0036825, 483202.017538, 93.27191, jce)

def ascending_longitude_moon(jce):
    return third_order_polynomial(1.0/450000.0, 0.0020708, -1934.136261, 125.04452, jce)

def xy_term_summation(i, x):
    sum=0
    for j in range(TERM_X.Y_COUNT.value):
        sum += x[j]*Y_TERMS[i][j]
    return sum

def nutation_longitude_and_obliquity(jce, x, del_psi, del_epsilon):
    sum_psi=0
    sum_epsilon=0
    for i in range(Y_COUNT):
        xy_term_sum  = np.deg2rad(xy_term_summation(i, x))
        sum_psi     += (PE_TERMS[i][TERM_P.PSI_A.value] + jce*PE_TERMS[i][TERM_P.PSI_B.value])*np.sin(xy_term_sum)
        sum_epsilon += (PE_TERMS[i][TERM_P.EPS_C.value] + jce*PE_TERMS[i][TERM_P.EPS_D.value])*np.cos(xy_term_sum)

    del_psi[0]     = sum_psi     / 36000000.0
    del_epsilon[0] = sum_epsilon / 36000000.0

def ecliptic_mean_obliquity(jme):
    u = jme/10.0

    return 84381.448 + u*(-4680.93 + u*(-1.55 + u*(1999.25 + u*(-51.38 + u*(-249.67 +
                       u*(  -39.05 + u*( 7.12 + u*(  27.87 + u*(  5.79 + u*2.45)))))))))


def ecliptic_true_obliquity(delta_epsilon, epsilon0):
    return delta_epsilon[0] + epsilon0/3600.0

def aberration_correction(r):
    return -20.4898 / (3600.0*r)

def apparent_sun_longitude(theta, delta_psi, delta_tau):
    return theta + delta_psi + delta_tau

def greenwich_mean_sidereal_time (jd, jc):
    return limit_degrees(280.46061837 + 360.98564736629 * (jd - 2451545.0) +
                                       jc*jc*(0.000387933 - jc/38710000.0))

def greenwich_sidereal_time (nu0, delta_psi, epsilon):
    return nu0 + delta_psi[0]*np.cos(np.deg2rad(epsilon))

def geocentric_right_ascension(lamda, epsilon, beta):
    lamda_rad = np.deg2rad(lamda)
    epsilon_rad = np.deg2rad(epsilon)

    return limit_degrees(np.rad2deg(np.arctan2(np.sin(lamda_rad)*np.cos(epsilon_rad) -
                                       np.tan(np.deg2rad(beta))*np.sin(epsilon_rad), np.cos(lamda_rad))))

def geocentric_declination(beta, epsilon, lamda):
    beta_rad    = np.deg2rad(beta)
    epsilon_rad = np.deg2rad(epsilon)

    return np.rad2deg(np.arcsin(np.sin(beta_rad)*np.cos(epsilon_rad) +
                        np.cos(beta_rad)*np.sin(epsilon_rad)*np.sin(np.deg2rad(lamda))))

def observer_hour_angle(nu, longitude, alpha_deg):
    return limit_degrees(nu + longitude - alpha_deg)

def sun_equatorial_horizontal_parallax(r):
    return 8.794 / (3600.0 * r)


def right_ascension_parallax_and_topocentric_dec(latitude, elevation,
	       xi, h, delta, delta_alpha, delta_prime):
    lat_rad   = np.deg2rad(latitude)
    xi_rad    = np.deg2rad(xi)
    h_rad     = np.deg2rad(h)
    delta_rad = np.deg2rad(delta)
    u = np.arctan(0.99664719 * np.tan(lat_rad))
    y = 0.99664719 * np.sin(u) + elevation*np.sin(lat_rad)/6378140.0
    x =              np.cos(u) + elevation*np.cos(lat_rad)/6378140.0

    delta_alpha_rad =      np.arctan2(                - x*np.sin(xi_rad) *np.sin(h_rad),
                                  np.cos(delta_rad) - x*np.sin(xi_rad) *np.cos(h_rad));

    delta_prime[0] = np.rad2deg(np.arctan2((np.sin(delta_rad) - y*np.sin(xi_rad))*np.cos(delta_alpha_rad),
                                  np.cos(delta_rad) - x*np.sin(xi_rad) *np.cos(h_rad)))

    delta_alpha[0] = np.rad2deg(delta_alpha_rad)


def topocentric_right_ascension(alpha_deg, delta_alpha):

    return alpha_deg + delta_alpha


def topocentric_local_hour_angle(h, delta_alpha):

    return h - delta_alpha


def topocentric_elevation_angle(latitude, delta_prime, h_prime):

    lat_rad         = np.deg2rad(latitude)
    delta_prime_rad = np.deg2rad(delta_prime)

    return np.rad2deg(np.arcsin(np.sin(lat_rad)*np.sin(delta_prime_rad) +
                        np.cos(lat_rad)*np.cos(delta_prime_rad) * np.cos(np.deg2rad(h_prime))))


def atmospheric_refraction_correction(pressure, temperature,
	                                     atmos_refract, e0):

    del_e = 0

    if (e0 >= -1*(SUN_RADIUS + atmos_refract)):
        del_e = (pressure / 1010.0) * (283.0 / (273.0 + temperature)) * \
                 1.02 / (60.0 * np.tan(np.deg2rad(e0 + 10.3/(e0 + 5.11))))

    return del_e


def topocentric_elevation_angle_corrected(e0, delta_e):

    return e0 + delta_e


def topocentric_zenith_angle(e):

    return 90.0 - e


def topocentric_azimuth_angle_astro(h_prime, latitude, delta_prime):

    h_prime_rad = np.deg2rad(h_prime)
    lat_rad     = np.deg2rad(latitude)

    return limit_degrees(np.rad2deg(np.arctan2(np.sin(h_prime_rad),
                         np.cos(h_prime_rad)*np.sin(lat_rad) - np.tan(np.deg2rad(delta_prime))*np.cos(lat_rad))))


def topocentric_azimuth_angle(azimuth_astro):

    return limit_degrees(azimuth_astro + 180.0)


def surface_incidence_angle(zenith, azimuth_astro, azm_rotation, slope):
    zenith_rad = np.deg2rad(zenith)
    slope_rad  = np.deg2rad(slope)
    return np.rad2deg(np.arccos(np.cos(zenith_rad)*np.cos(slope_rad)  +
                        np.sin(slope_rad )*np.sin(zenith_rad) * np.cos(np.deg2rad(azimuth_astro - azm_rotation))))


def sun_mean_longitude(jme):

    return limit_degrees(280.4664567 + jme*(360007.6982779 + jme*(0.03032028 +
                    jme*(1/49931.0   + jme*(-1/15300.0     + jme*(-1/2000000.0))))))


def eot(m, alpha, del_psi, epsilon):

    return limit_minutes(4.0*(m - 0.0057183 - alpha + del_psi[0]*np.cos(np.deg2rad(epsilon))))


def approx_sun_transit_time(alpha_zero, longitude, nu):

    return (alpha_zero - longitude - nu) / 360.0


def sun_hour_angle_at_rise_set(latitude, delta_zero, h0_prime):

    h0             = -99999
    latitude_rad   = np.deg2rad(latitude)
    delta_zero_rad = np.deg2rad(delta_zero)
    argument       = (np.sin(np.deg2rad(h0_prime)) - np.sin(latitude_rad)*np.sin(delta_zero_rad)) / \
                                                     (np.cos(latitude_rad)*np.cos(delta_zero_rad))

    if (abs(argument) <= 1):
        h0 = limit_degrees180(np.rad2deg(np.arccos(argument)))

    return h0


def approx_sun_rise_and_set(m_rts, h0):

    h0_dfrac = h0/360.0

    m_rts[SUN.RISE.value]    = limit_zero2one(m_rts[SUN.TRANSIT.value] - h0_dfrac)
    m_rts[SUN.SET.value]     = limit_zero2one(m_rts[SUN.TRANSIT.value] + h0_dfrac)
    m_rts[SUN.TRANSIT.value] = limit_zero2one(m_rts[SUN.TRANSIT.value])


def rts_alpha_delta_prime(ad, n):

    a = ad[JD.ZERO.value] - ad[JD.MINUS.value]
    b = ad[JD.PLUS.value] - ad[JD.ZERO.value]

    if (abs(a) >= 2.0):
        a = limit_zero2one(a)
    if (abs(b) >= 2.0):
        b = limit_zero2one(b)

    return ad[JD.ZERO.value] + n * (a + b + (b-a)*n)/2.0


def rts_sun_altitude(latitude, delta_prime, h_prime):

    latitude_rad    = np.deg2rad(latitude)
    delta_prime_rad = np.deg2rad(delta_prime)

    return np.rad2deg(np.arcsin(np.sin(latitude_rad)*np.sin(delta_prime_rad) +
                        np.cos(latitude_rad)*np.cos(delta_prime_rad)*np.cos(np.deg2rad(h_prime))))


def sun_rise_and_set(m_rts,   h_rts,   delta_prime, latitude,
                        h_prime, h0_prime, sun):

    return m_rts[sun.value] + (h_rts[sun.value] - h0_prime) / \
          (360.0*np.cos(np.deg2rad(delta_prime[sun.value]))*
           np.cos(np.deg2rad(latitude))*np.sin(np.deg2rad(h_prime[sun.value])))


################################################################################################
## Calculate required SPA parameters to get the right ascension (alpha) and declination (delta)
## Note: JD must be already calculated and in structure
################################################################################################

def calculate_geocentric_sun_right_ascension_and_declination(spa):

    spa.jc = julian_century(spa.jd)

    spa.jde = julian_ephemeris_day(spa.jd, spa.delta_t)
    spa.jce = julian_ephemeris_century(spa.jde)
    spa.jme = julian_ephemeris_millennium(spa.jce)

    spa.l = earth_heliocentric_longitude(spa.jme)
    spa.b = earth_heliocentric_latitude(spa.jme)
    spa.r = earth_radius_vector(spa.jme)

    spa.theta = geocentric_longitude(spa.l)
    spa.beta  = geocentric_latitude(spa.b)

    x = np.zeros(TERM_X.COUNT.value)

    x[TERM_X.X0.value] = spa.x0 = mean_elongation_moon_sun(spa.jce)
    x[TERM_X.X1.value] = spa.x1 = mean_anomaly_sun(spa.jce)
    x[TERM_X.X2.value] = spa.x2 = mean_anomaly_moon(spa.jce)
    x[TERM_X.X3.value] = spa.x3 = argument_latitude_moon(spa.jce)
    x[TERM_X.X4.value] = spa.x4 = ascending_longitude_moon(spa.jce)

    nutation_longitude_and_obliquity(spa.jce, x, spa.del_psi, spa.del_epsilon)

    spa.epsilon0 = ecliptic_mean_obliquity(spa.jme)
    spa.epsilon  = ecliptic_true_obliquity(spa.del_epsilon, spa.epsilon0)

    spa.del_tau   = aberration_correction(spa.r)
    spa.lamda     = apparent_sun_longitude(spa.theta, spa.del_psi, spa.del_tau)
    spa.nu0       = greenwich_mean_sidereal_time (spa.jd, spa.jc)
    spa.nu        = greenwich_sidereal_time (spa.nu0, spa.del_psi, spa.epsilon)

    spa.alpha = geocentric_right_ascension(spa.lamda, spa.epsilon, spa.beta)
    spa.delta = geocentric_declination(spa.beta, spa.epsilon, spa.lamda)


########################################################################
## Calculate Equation of Time (EOT) and Sun Rise, Transit, & Set (RTS)
########################################################################

def calculate_eot_and_sun_rise_transit_set(spa):
    h0_prime = -1*(SUN_RADIUS + spa.atmos_refract)
    sun_rts  = deepcopy(spa)
    m = sun_mean_longitude(spa.jme)
    spa.eot = eot(m, spa.alpha, spa.del_psi, spa.epsilon)

    sun_rts.hour = sun_rts.minute = sun_rts.second = 0
    sun_rts.delta_ut1 = sun_rts.timezone = 0.0

    sun_rts.jd = julian_day(sun_rts.year,   sun_rts.month,  sun_rts.day,       sun_rts.hour,
		                     sun_rts.minute, sun_rts.second, sun_rts.delta_ut1, sun_rts.timezone)

    calculate_geocentric_sun_right_ascension_and_declination(sun_rts)
    nu = sun_rts.nu

    sun_rts.delta_t = 0
    sun_rts.jd -= 1
    alpha = np.zeros(JD.COUNT.value)
    delta = np.zeros(JD.COUNT.value)
    for i in range(JD.COUNT.value):
        calculate_geocentric_sun_right_ascension_and_declination(sun_rts)
        alpha[i] = sun_rts.alpha
        delta[i] = sun_rts.delta
        sun_rts.jd += 1

    m_rts = np.zeros(SUN.COUNT.value)
    m_rts[SUN.TRANSIT.value] = approx_sun_transit_time(alpha[JD.ZERO.value], spa.longitude, nu)
    h0 = sun_hour_angle_at_rise_set(spa.latitude, delta[JD.ZERO.value], h0_prime)

    if h0 >= 0:

        approx_sun_rise_and_set(m_rts, h0)

        nu_rts = np.zeros(SUN.COUNT.value)
        alpha_prime = np.zeros(SUN.COUNT.value)
        delta_prime = np.zeros(SUN.COUNT.value)
        h_prime = np.zeros(SUN.COUNT.value)
        h_rts = np.zeros(SUN.COUNT.value)
        for i in range(SUN.COUNT.value):

            nu_rts[i]      = nu + 360.985647*m_rts[i]

            n              = m_rts[i] + spa.delta_t/86400.0
            alpha_prime[i] = rts_alpha_delta_prime(alpha, n)
            delta_prime[i] = rts_alpha_delta_prime(delta, n)

            h_prime[i]     = limit_degrees180pm(nu_rts[i] + spa.longitude - alpha_prime[i])

            h_rts[i]       = rts_sun_altitude(spa.latitude, delta_prime[i], h_prime[i])


        spa.srha = h_prime[SUN.RISE.value]
        spa.ssha = h_prime[SUN.SET.value]
        spa.sta  = h_rts[SUN.TRANSIT.value]

        spa.suntransit = dayfrac_to_local_hr(m_rts[SUN.TRANSIT.value] - h_prime[SUN.TRANSIT.value] / 360.0,
                                              spa.timezone)

        spa.sunrise = dayfrac_to_local_hr(sun_rise_and_set(m_rts, h_rts, delta_prime,
                          spa.latitude, h_prime, h0_prime, SUN.RISE), spa.timezone)

        spa.sunset  = dayfrac_to_local_hr(sun_rise_and_set(m_rts, h_rts, delta_prime,
                          spa.latitude, h_prime, h0_prime, SUN.SET),  spa.timezone)

    else:
        spa.srha = spa.ssha = spa.sta = spa.suntransit = spa.sunrise = spa.sunset = -99999



###########################################################################################
## Calculate all SPA parameters and put into structure
## Note: All inputs values (listed in header file) must already be in structure
###########################################################################################
def spa_calculate(spa):

    result = validate_inputs(spa)

    if result == 0:
        spa.jd = julian_day(spa.year,   spa.month,  spa.day,       spa.hour,
			                  spa.minute, spa.second, spa.delta_ut1, spa.timezone)

        calculate_geocentric_sun_right_ascension_and_declination(spa)

        spa.h  = observer_hour_angle(spa.nu, spa.longitude, spa.alpha)
        spa.xi = sun_equatorial_horizontal_parallax(spa.r)

        right_ascension_parallax_and_topocentric_dec(spa.latitude, spa.elevation, spa.xi,
                                spa.h, spa.delta, spa.del_alpha, spa.delta_prime)

        spa.alpha_prime = topocentric_right_ascension(spa.alpha, spa.del_alpha)
        spa.h_prime     = topocentric_local_hour_angle(spa.h, spa.del_alpha)

        spa.e0      = topocentric_elevation_angle(spa.latitude, spa.delta_prime, spa.h_prime)
        spa.del_e   = atmospheric_refraction_correction(spa.pressure, spa.temperature,
                                                         spa.atmos_refract, spa.e0)
        spa.e       = topocentric_elevation_angle_corrected(spa.e0, spa.del_e)

        spa.zenith        = topocentric_zenith_angle(spa.e)
        spa.azimuth_astro = topocentric_azimuth_angle_astro(spa.h_prime, spa.latitude,
                                                                           spa.delta_prime)
        spa.azimuth       = topocentric_azimuth_angle(spa.azimuth_astro)

        if (spa.function == SPA_FUNC.SPA_ZA_INC) or (spa.function == SPA_FUNC.SPA_ALL):
            spa.incidence  = surface_incidence_angle(spa.zenith, spa.azimuth_astro,
                                                      spa.azm_rotation, spa.slope)

        if (spa.function == SPA_FUNC.SPA_ZA_RTS) or (spa.function == SPA_FUNC.SPA_ALL):
            calculate_eot_and_sun_rise_transit_set(spa)


    return result


if __name__ == '__main__':
    spa = spa_data();  ##declare the SPA structure

    ##enter required input values into SPA structure

    spa.year          = 2003
    spa.month         = 10
    spa.day           = 17
    spa.hour          = 12
    spa.minute        = 30
    spa.second        = 30
    spa.timezone      = -7.0
    spa.delta_ut1     = 0
    spa.delta_t       = 67
    spa.longitude     = -105.1786
    spa.latitude      = 39.742476
    spa.elevation     = 1830.14
    spa.pressure      = 820
    spa.temperature   = 11
    spa.slope         = 30
    spa.azm_rotation  = -10
    spa.atmos_refract = 0.5667
    spa.function      = SPA_FUNC.SPA_ALL

    ##call the SPA calculate function and pass the SPA structure

    result = spa_calculate(spa)

    if result == 0:  ##check for SPA errors
        ##display the results inside the SPA structure

        print("Julian Day:    %.6f\n"%spa.jd)
        print("L:             %.6e degrees\n"%spa.l)
        print("B:             %.6e degrees\n"%spa.b)
        print("R:             %.6f AU\n"%spa.r)
        print("H:             %.6f degrees\n"%spa.h)
        print("Delta Psi:     %.6e degrees\n"%spa.del_psi[0])
        print("Delta Epsilon: %.6e degrees\n"%spa.del_epsilon[0])
        print("Epsilon:       %.6f degrees\n"%spa.epsilon)
        print("Zenith:        %.6f degrees\n"%spa.zenith)
        print("Azimuth:       %.6f degrees\n"%spa.azimuth)
        print("Incidence:     %.6f degrees\n"%spa.incidence)

        min = 60.0*(spa.sunrise - int(spa.sunrise))
        sec = 60.0*(min - int(min))
        print("Sunrise:       %02d:%02d:%02d Local Time\n"%(int(spa.sunrise), int(min), int(sec)))

        min = 60.0*(spa.sunset - int(spa.sunset))
        sec = 60.0*(min - int(min))
        print("Sunset:        %02d:%02d:%02d Local Time\n"%(int(spa.sunset), int(min), int(sec)))

    else:
        print("SPA Error Code: %d\n"%result)

#
# /////////////////////////////////////////////
# // The output of this program should be:
# //
# //Julian Day:    2452930.312847
# //L:             2.401826e+01 degrees
# //B:             -1.011219e-04 degrees
# //R:             0.996542 AU
# //H:             11.105902 degrees
# //Delta Psi:     -3.998404e-03 degrees
# //Delta Epsilon: 1.666568e-03 degrees
# //Epsilon:       23.440465 degrees
# //Zenith:        50.111622 degrees
# //Azimuth:       194.340241 degrees
# //Incidence:     25.187000 degrees
# //Sunrise:       06:12:43 Local Time
# //Sunset:        17:20:19 Local Time
# //
# /////////////////////////////////////////////
#
