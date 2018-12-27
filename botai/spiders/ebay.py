import scrapy
from scrapy_splash import SplashRequest
import base64
from urllib.parse import urlparse
from .database import db

script = """
function main(splash, args)
    splash:set_viewport_size(1920, 1080)
    local url = splash.args.url
    assert(splash:go(args.url))
    assert(splash:wait(10))
    return {
        html = splash:html(),
        png = splash:png{render_all=true},
    }
end
"""

class EbaySpider(scrapy.Spider):
    name = 'ebay'
    allowed_domains = ["ebay.com"]

    start_urls = [
        f"https://www.ebay.com/itm/Alienware-17-R5-17-3-Gaming-Notebook-i7-8750H-8GB-RAM-1TB-HDD-256GB-SSD-GTX1060/302747803879",
        f"https://www.ebay.com/itm/Alienware-17-R4-17-3-LCD-Gaming-Notebook-Dell-Gaming-23-6-LED-LCD-Monitor/292464759956?_trkparms=aid%3D444000%26algo%3DSOI.DEFAULT%26ao%3D1%26asc%3D55165%26meid%3D17245fbf894e4af5994927ee53b61e9e%26pid%3D100752%26rk%3D1%26rkt%3D6%26sd%3D302747803879%26itm%3D292464759956&_trksid=p2047675.c100752.m1982",
        f"https://www.ebay.com/itm/HP-EliteBook-x360-1030-13-3-Touch-LCD-2-in-1-Intel-Core-i7-16GB-512GB-SSD/302915606096?_trkparms=aid%3D444000%26algo%3DSOI.DEFAULT%26ao%3D1%26asc%3D55165%26meid%3D17245fbf894e4af5994927ee53b61e9e%26pid%3D100752%26rk%3D2%26rkt%3D6%26sd%3D302747803879%26itm%3D302915606096&_trksid=p2047675.c100752.m1982",
        f"https://www.ebay.com/itm/Alienware-17-R5-17-3-Gaming-Notebook-i7-8750H-16GB-RAM-1TB-HDD-8GB-SSD-GTX1070/123491786215?_trkparms=aid%3D444000%26algo%3DSOI.DEFAULT%26ao%3D1%26asc%3D55165%26meid%3D17245fbf894e4af5994927ee53b61e9e%26pid%3D100752%26rk%3D3%26rkt%3D6%26sd%3D302747803879%26itm%3D123491786215&_trksid=p2047675.c100752.m1982",
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': script})

    def parse(self, response):
        imgdata = base64.b64decode(response.data['png'])
        filename = 'screenshot.png'
        with open(filename, 'wb') as f:
            f.write(imgdata)
        
        data = {
            'title': response.xpath('//*[@id="itemTitle"]/text()').extract_first().strip(),
            'condition': response.xpath('//*[@id="vi-itm-cond"]/text()').extract_first().strip(),
            'listPrice': {
                'price': response.xpath('//*[@id="orgPrc"]/text()').extract_first().strip(),
                'salePrice': response.xpath('//*[@id="prcIsum"]/text()').extract_first().strip(),
            },
        }
        
        table = response.xpath('//*[@id="viTabs_0_is"]/div/table/tbody')

        numRow = len(response.xpath('//*[@id="viTabs_0_is"]/div/table/tbody/tr').extract())

        if numRow > 0:
            data['description'] = {}
            for i in range(1, numRow+1):
                numCol = len(response.xpath(f'//*[@id="viTabs_0_is"]/div/table/tbody/tr[{i}]/td').extract())
                for j in range(1, numCol):
                    try:
                        item = response.xpath(f'//*[@id="viTabs_0_is"]/div/table/tbody/tr[{i}]/td[{j}]//text()').extract_first().strip()
                        j += 1
                        content = response.xpath(f'//*[@id="viTabs_0_is"]/div/table/tbody/tr[{i}]/td[{j}]/node()//text()').extract_first().strip()
                        if type(content) is not None:
                            data.get('description')[item] = content
                    except:
                        continue
    
        iframe = response.xpath('//*[@id="desc_ifr"]/@src').extract_first()
        if iframe is not None:
            data.get('description')['iframe'] = iframe

        # db.ebay.insert(data)

        yield data