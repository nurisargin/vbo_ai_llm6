# Week 2 Ödevi: Şema Farkındalıklı Veritabanı MCP Sunucusu

## 1. Proje Özeti

Bu projede bir PostgreSQL veritabanı, **MCP (Model Context Protocol) sunucusunun** arkasına yerleştirilmiştir. Bir **yapay zeka ajanı** bu sunucuya bağlanarak doğal dilde sorulan soruları (örn. *"Engineering departmanındaki en yüksek maaşlı çalışanın adını ve maaşını ver."*) SQL yazarak kendisi cevaplar.

Ajan veritabanına doğrudan erişmez; tüm işlemler MCP araçları üzerinden yapılır.

## 2. Mimari

```
Kullanıcı sorusu → Ajan ──MCP (HTTP)──→ MCP Sunucusu ──SQL──→ PostgreSQL
```

## 3. Proje Yapısı

| Dosya | Görevi |
|---|---|
| `hw_db.py` | Veritabanı bağlantısını oluşturur (`PG_DSN` değerini `.env` dosyasından okur) |
| `hw_db_seed.py` | `departments` ve `employees` tablolarını örnek verilerle oluşturur |
| `hw_db_server.py` | MCP sunucusu (3 araç) ve tasarım sorularının cevapları (yorum olarak) |
| `hw_db_client.py` | Sunucuya bağlanan ve soruyu cevaplayan ajan |
| `requirements.txt` | Bağımlılık listesi |
| `README.md` | Proje dokümantasyonu |

## 4. MCP Araçları

Ajan, işe yeni başlayan bir analist gibi çalışır: önce tablolara, sonra sütunlara bakar, en son sorguyu yazar. Sunucu bu üç adımı üç araç olarak sunar. Tablolara ait hiçbir bilgi koda yazılmamıştır; ajan bunları araçları çağırarak öğrenir.

| Araç | Açıklama |
|---|---|
| `list_tables()` | Veritabanındaki tablo adlarını listeler |
| `describe_table(table_name)` | Bir tablonun sütunlarını ve tiplerini veritabanından okur |
| `run_select(sql)` | Yalnızca `SELECT` sorgusu çalıştırır, en fazla 50 satır döndürür |

Departman adı `departments`, maaş bilgisi `employees` tablosunda bulunduğu için ajan iki tabloyu birleştirmek (JOIN) zorundadır.

## 5. Kurulum

### 5.1 Bağımlılıklar (uv)

```bash
uv add -r requirements.txt
```

> `requirements.txt` içinde `mcp<2` olarak sabitlenmiştir. MCP 2.x'te `FastMCP` sınıfı kaldırıldığı için kod 1.x API'sini kullanır.

### 5.2 Veritabanı (Docker)

```bash
docker run --name langgraph-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=langgraph_db -p 5432:5432 -d postgres:16
```

Sonraki kullanımlarda yalnızca `docker start langgraph-postgres` yeterlidir.

### 5.3 Ortam Değişkenleri

Proje dizinindeki `.env` dosyasına şu satırlar eklenir:

```
PG_DSN=postgresql://postgres:postgres@localhost:5432/langgraph_db
OPENROUTER_API_KEY=kendi_anahtarin
```

## 6. Çalıştırma

Tüm dosyaların bulunduğu klasörde sırasıyla:

```bash
uv run python hw_db_seed.py      # Bir kez: tabloları oluştur ve doldur
uv run python hw_db_server.py    # Terminal 1: MCP sunucusu (açık kalmalı)
uv run python hw_db_client.py    # Terminal 2: ajan
```

## 7. Beklenen Sonuç

Ajan sorguyu yazmadan önce tabloları inceler; araç çağrı sırası `list_tables` → `describe_table` → `run_select` şeklindedir. Nihai cevap:

> **Alice Johnson, 145000**

## 8. Tasarım Soruları ve Cevaplar

Cevaplar `hw_db_server.py` dosyasının sonunda yorum satırı olarak yer alır:

```python
# CEVAPLAR
# 1. Neden tek bir run_sql yerine üç araç?
#    Yeni başlayan bir analist gibi, ajanın da önce hangi tabloların olduğuna
#    (list_tables), sonra sütunlarına (describe_table) bakıp en son sorguyu
#    (run_select) yazması gerekir. Tek run_sql aracında bu adımlar yoktur:
#    model tablo ve sütun adlarını tahmin eder, hatalı veya uydurma sorgular
#    yazar. Ayrıca genel bir run_sql INSERT/DROP gibi tehlikeli komutları da
#    çalıştırabilir. Küçük ve tek amaçlı araçlar daha güvenli ve kontrol
#    etmesi daha kolaydır.
#
# 2. Neden sütunları araç açıklamasına yazmak yerine veritabanından okuyoruz?
#    Tablolarla ilgili hiçbir bilgi koda yazılmaz, ajan bunları araçları
#    çağırarak öğrenir. Elle yazılan şema veritabanının bir kopyasıdır ve
#    sütun eklenince/silinince eskir. Canlı okumak her zaman doğru bilgiyi
#    verir (tek doğru kaynak veritabanı). Ayrıca kod başka bir veritabanında
#    da değişmeden çalışır ve prompt şişmez.
#
# 3. Sadece SELECT kabul etmek yetmez; ne ters gidebilir? Ek bir koruma nedir?
#    SELECT ile de çok ağır sorgular çalıştırılıp veritabanı yavaşlatılabilir,
#    hassas veriler (şifre, kişisel bilgi) okunup modele gönderilebilir.
#    Anahtar kelime filtresi de aşılabilir.
#    Ek koruma: Sadece SELECT yetkisi olan salt okunur bir veritabanı kullanıcısı
#    ile bağlanmak. Böylece doğrulama aşılsa bile veritabanı yazmayı reddeder.
#    (Kodda ayrıca salt okunur transaction, zaman aşımı ve 50 satır sınırı var.)
```

## 9. Kontrol Listesi

- [x] Ajan doğru cevabı veriyor: **Alice Johnson, 145000**
- [x] `describe_table` sütunları veritabanından okuyor (elle yazılmış sütun adı yok)
- [x] `run_select` `SELECT` dışındaki sorguları reddediyor ve en fazla 50 satır döndürüyor
- [x] Yazdırılan mesajlarda ajan, sorguyu çalıştırmadan önce tabloları inceliyor
- [x] Üç soru, kod içinde yorum olarak cevaplandı

## 10. Sorun Giderme

| Hata | Çözüm |
|---|---|
| `No module named 'mcp.server.fastmcp'` | `mcp` 2.x kurulmuş demektir. `uv add "mcp<2"` komutuyla 1.x sürümüne dönün |
| `No module named 'psycopg'` | `uv add "psycopg[binary]"` komutunu çalıştırın |
| Bağlantı hatası (5432 veya 8005) | PostgreSQL konteyneri (`docker start langgraph-postgres`) ve MCP sunucusu çalışıyor olmalıdır |
| `relation "employees" does not exist` | `uv run python hw_db_seed.py` komutunu çalıştırın |