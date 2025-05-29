import requests
from bs4 import BeautifulSoup
import re


def get_best_result_snippet(query, max_results=3):
    """
    Google Custom Search API ile arama yapar, max_results kadar sonuç alır,
    en anlamlı snippet, sayfa başlığı ve içeriği döner.
    """

    GOOGLE_API_KEY = "APIKEY"
    CX = "CX"

    url = "https://customsearch.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "q": query,
        "cx": CX,
        "num": max_results,
        "lr": "lang_tr"  # Türkçe arama
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        items = data.get("items", [])
        if not items:
            return "Sonuç bulunamadı."

        # En iyi sonuçları tek tek işleyelim, anlamlı içerik döndürmeye çalışacağız
        for item in items:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")

            # Sayfa içeriğini çek
            page_text = fetch_page_content(link)
            if page_text:
                # Çok uzun içerik döndürmek istemiyoruz, snippet + anlamlı içerik kısa tutulabilir
                combined_text = f"{title}\n{snippet}\n\n{page_text[:700]}"
                return combined_text

        # Hiçbir sayfa içeriği alınamadıysa snippet ile döneriz
        return items[0].get("snippet", "Sonuç bulunamadı.")

    except requests.RequestException as e:
        return f"API isteğinde hata oluştu: {str(e)}"
    except Exception as e:
        return f"Bilinmeyen hata: {str(e)}"


def fetch_page_content(url):
    """
    Verilen URL'den anlamlı metin içerik çeker.
    Reklam, link ve kısa paragrafları elemeye çalışır.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Sayfa başlığı (isteğe bağlı)
        # title = soup.title.string if soup.title else ""

        # Meta description
        meta_desc = ""
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"]

        paragraphs = soup.find_all('p')
        clean_paragraphs = []

        for para in paragraphs:
            text = para.get_text().strip()

            # Filtreleme: minimum uzunluk, reklam/link içermemesi, aşırı kısa olmaması
            if len(text) > 100 and not re.search(r'http|www\.|@|facebook|instagram|twitter', text, re.I):
                clean_paragraphs.append(text)

        # En uzun veya en anlamlı paragrafı seçebiliriz
        if clean_paragraphs:
            best_para = max(clean_paragraphs, key=len)
        else:
            best_para = ""

        # Sonuç olarak meta description + en iyi paragraf dönebiliriz
        combined = meta_desc + "\n\n" + best_para if meta_desc else best_para
        return combined.strip()

    except requests.RequestException:
        return ""
    except Exception:
        return ""


# Test örneği
if __name__ == "__main__":
    query = "Türkiye'nin başkenti nedir?"
    result = get_best_result_snippet(query)
    print("Araştırma sonucu:\n", result)
