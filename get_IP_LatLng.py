import requests
import geocoder


def get_IP():
    res = requests.get('http://jsonip.com', timeout=10)
    ip = res.json()['ip']
    print("Your IP address is:\n" + ip)
    return ip


def get_LatLng():
    ip = get_IP()
    g = geocoder.ip(ip)
    # g = geocoder.ip('me')
    latlng = g.latlng
    print("Your latitude is %s\nYour longitude is %s" % (latlng[0], latlng[1]))
    return latlng


if __name__ == '__main__':
    latlng_data = get_LatLng()
