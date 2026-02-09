from app.api.adapters import TelegramAdapter, EmailAdapter, WhatsAppAdapter
from datetime import datetime

def test_adapters():
    # Telegram
    tg = TelegramAdapter()
    tg_payload = {"message": {"from": {"id": 123}, "text": "tg text", "date": 1700000000}}
    tg_out = tg.transform(tg_payload)
    print(f"Telegram: {tg_out}")
    assert tg_out.source == "telegram"
    assert tg_out.content == "tg text"

    # Email
    em = EmailAdapter()
    em_payload = {"from": "user@test.com", "body": "email body", "date": "2024-02-08T12:00:00"}
    em_out = em.transform(em_payload)
    print(f"Email: {em_out}")
    assert em_out.source == "email"
    assert em_out.content == "email body"

    # WhatsApp
    wa = WhatsAppAdapter()
    wa_payload = {"sender_number": "12345", "message_text": "wa text"}
    wa_out = wa.transform(wa_payload)
    print(f"WhatsApp: {wa_out}")
    assert wa_out.source == "whatsapp"
    assert wa_out.content == "wa text"

if __name__ == "__main__":
    test_adapters()
    print("All adapter tests passed!")
