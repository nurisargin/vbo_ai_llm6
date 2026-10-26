from langchain_typesafe import Choice, Noul, Score, TypeSafeClassifier

# No API key is checked locally, but the client refuses an empty one
classifier = TypeSafeClassifier(base_url="http://localhost:8000", model="tau-4b",
                                api_key="local", timeout=120)

QUESTIONS = {
    "intent": Choice(
        instructions="Müşteri ne istiyor?",
        criteria={
            "siparis_durumu": "Siparişim nerede, teslimat tarihi, kargo takibi",
            "iade_degisim": "Ürünü iade etmek veya değiştirmek",
            "urun_sorusu": "Ürün özellikleri, beden, stok soruları",
        },
    ),
    "complaint": Noul(instructions="Müşteri bir şeyden şikayet ediyor"),
    "frustration": Score(
        instructions="Müşteri ne kadar kızgın görünüyor?",
        criteria=["Sakin", "Kızgın ama kibar", "Çok kızgın"],
    ),
}

messages = [
    "Merhaba, mavi ceketin L bedeni var mı?",
    "Siparişim geçen hafta gelmesi gerekiyordu. Üçüncü kez yazıyorum, "
    "kimse cevap vermiyor. Kabul edilemez!",
    "Ayakkabıları geri gönderebilir miyim? Biraz küçük geldi.",
]

for text in messages:
    r = classifier.invoke({"state": text, "questions": QUESTIONS})
    intent = r.choices["intent"]
    complaint = r.nouls["complaint"].noul
    frustration = r.scores["frustration"].score

    print(f"\nMüşteri: {text}")
    print(f"  intent={intent.choice} (confidence {intent.confidence:.2f})"
          f"  complaint={complaint:.2f}  frustration={frustration:.2f}")

    # Same rules as main1: the model reports numbers, the code decides
    if intent.confidence < 0.5:
        print("  -> ne istediği belli değil, bir insana yönlendir")
    elif complaint > 0.5 and frustration > 1:
        print("  -> öfkeli şikayet, kıdemli temsilciye aktar")
    else:
        print(f"  -> otomatik işle: {intent.choice}")