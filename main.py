from bs4 import BeautifulSoup
import requests,base64,json

def getSiteToken(session,url):
    try:
        response = session.get(url)
        if response.status_code==200:
            content = BeautifulSoup(response.content, 'html.parser')
            token = content.find("input", {"name": "csrf_token"})["value"]
            return token
        else:
            print("URL bilgisini kontrol ediniz")
    except:
        print("Hata meydana geldi")
        exit()

def loginSite(session,urlLogin,login_data):
    try:
        session.post(urlLogin, login_data)
    except:
        print("loginSite fonksiyonunda hata meydana geldi")
        exit()

def favoriSayfasi(session,urlFavoriler):
    favoriler=[]
    response = session.get(urlFavoriler)
    content = BeautifulSoup(response.content,'lxml')
    div = content.find_all("div", attrs={"class": "AdvertBox-1"})
    for item in div:
        # Resim base64 dönüştürme
        img = item.find("img", attrs={"class": "AdvertBox-Image-1"})
        if (img.has_attr('data-src')):
            response = requests.get(img['data-src'])
            resim64enc=base64.b64encode(response.content).decode("utf-8")

        # Favorileri listeye ekleme
        favoriler.append([item.find("a").get("href"),
                          item.find("div", attrs={"class": "AdvertBox-Price"}).text,
                          item.find("img", attrs={"class": "AdvertBox-Image-1"}).get("data-src"),
                          resim64enc])
    # Listeyi dict dönüştürme
    foviriler = [dict(zip(("Link", "Fiyat","Resim Linki","Resim Base64"), favori)) for favori in favoriler]
    return foviriler

def jsonYazma(favoriler_dict):
    with open("favoriler.json", "w") as outfile:
        json.dump(favoriler_dict, outfile,indent=4)

if __name__=='__main__':
    # Gerekli bilgiler
    url="https://www.itemsatis.com/"
    urlLogin = "https://www.itemsatis.com/api/Login"
    urlFavoriler="https://www.itemsatis.com/favori-ilanlarim.html"
    UserName=input("Kullanıcı adını giriniz...: ")
    Password=input("Şifrenizi giriniz      ...: ")

    # Oturum için bir session oluşturulur
    session=requests.session()

    # Login için gerekli olan token bilgisi ilk get isteğinde alınır
    token=getSiteToken(session,url)

    # Login yaparken gerekli olan bilgiler, csrf_token bilgisi POST yapacağımız için önemli
    login_data = {"UserName": UserName, "Password": Password, "csrf_token": token}

    # Aynı session bilgileri ile login işlemei gerçekleştirilir
    loginSite(session,urlLogin,login_data)

    # Login işleminden sonra favorilerim sayfasına gidilir ve kaç tane favori ürün varsa istenilen bilgiler alınır
    favoriler_dict=favoriSayfasi(session,urlFavoriler)

    # Dict olan bilgiler JSON formatına dönüştürülür ve favoriler.json dosyasına kayıt edilir
    jsonYazma(favoriler_dict)
