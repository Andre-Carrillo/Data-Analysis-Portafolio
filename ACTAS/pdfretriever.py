import requests
import urllib3
import lxml.html as html
import re

urllib3.disable_warnings()

versiones = ["1.1.1", "1.1.2", "1.2.1", "1.2.2", "1.2.3", "1.3.1", "1.3.2", "1.4.1", "1.4.2"]
url = "https://www2.congreso.gob.pe/sicr/RedacActas/Actas.nsf/new_ActasPlenoAct?OpenForm&Start=1&Count=1000&Expand="

# for version in versiones:
#     response = requests.get(url+version, verify=False)
#     print(response.status_code)
for version in versiones:
    response = requests.get(url+version, verify=False)
    home = response.content.decode('utf-8')
    parsed = html.fromstring(home)
    listapdfurls = parsed.xpath('//a[contains(@href, ".pdf")]/@href')

    pdfurlscleaned = [re.search("(?<=')(.*/.*?)(?=')", string).group() for string in listapdfurls]
    url_pdf = "https://www2.congreso.gob.pe/sicr/RedacActas/Actas.nsf/"
    print(f"Descargando la página {version}")
    for pdf in pdfurlscleaned:
        name=re.search(r"(?<=\$FILE/).*", pdf).group()
        r = requests.get(url_pdf+pdf, verify=False)
        with open(f"ACTAS/{version}/{name}", "wb") as f:
            f.write(r.content)
        print(f"Escrito el pdf {name}")