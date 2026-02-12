"""YouTube Shorts script generation prompt template."""


def build_user_prompt(
    episode_title: str, episode_id: str, chunks_text: str, outline_text: str
) -> str:
    """Build user prompt for YouTube Shorts scripts.

    Args:
        episode_title: Original German episode title.
        episode_id: Episode identifier for citation format.
        chunks_text: Formatted chunk text with chunk IDs.
        outline_text: Previously generated outline (Markdown).

    Returns:
        User prompt string.
    """
    return f"""\
## GOREV: YouTube Shorts Senaryolari Olustur (6 adet)

Asagidaki taslak ve kaynak parcalarina dayanarak, 6 adet kisa video senaryosu olustur.
Her biri 60-90 saniye uzunlugunda olmali.

### BOLUM: "{episode_title}"

### TASLIK (Outline):
{outline_text}

### KAYNAK PARCALARI:
{chunks_text}

### CIKTI FORMATI: JSON dizisi

Tam olarak 6 short uret. Her biri su yapida olmali:
```json
[
  {{
    "title": "Kisa ve dikkat cekici Turkce baslik",
    "hook": "Ilk 3 saniyedeki dikkat cekici cumle",
    "body": "Ana icerik (60-90 saniye konusma metni)",
    "cta": "Harekete gecirici mesaj (abone ol, yorum yap, vb.)",
    "citations": ["{episode_id}_C0001", "{episode_id}_C0002"]
  }}
]
```

### HATIRLATMA:
- YALNIZCA kaynaklardaki bilgileri kullan
- Her short icin en az 1 kaynak belirt [{episode_id}_C####]
- Kaynakta olmayan bilgi icin "Kaynaklarda yok" yaz
- Fiyat tahmini, alim/satim tavsiyesi VERME
- Kisa, etkili, dikkat cekici Turkce kullan
- JSON ciktisi ver, baska bir sey yazma
"""
