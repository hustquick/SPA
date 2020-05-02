import requests
import geocoder


def get_IP():
    res = requests.get('http://jsonip.com', timeout=10)
    ip = res.json()['ip']
    print("你的IP地址为:\n" + ip)
    return ip


def get_LatLng():
    ip = get_IP()
    g = geocoder.ip(ip)
    # g = geocoder.ip('me')
    latlng = g.latlng
    print("\n根据你的IP地址")
    # print("你所在城市为:\n" + g.city)
    print("你的经度为：\t%8.4f \n你的纬度为：\t%8.4f" % (latlng[1], latlng[0]))
    return latlng


if __name__ == '__main__':
    latlng_data = get_LatLng()
