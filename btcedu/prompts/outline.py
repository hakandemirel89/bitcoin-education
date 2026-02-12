"""Outline generation prompt template."""


def build_user_prompt(episode_title: str, episode_id: str, chunks_text: str) -> str:
    """Build user prompt for outline generation.

    Args:
        episode_title: Original German episode title.
        episode_id: Episode identifier for citation format.
        chunks_text: Formatted chunk text with chunk IDs.

    Returns:
        User prompt string.
    """
    return f"""\
## GOREV: Video Taslagi (Outline) Olustur

Asagidaki Almanca podcast transkript parcalarina dayanarak, Turkce bir YouTube video \
taslagi olustur.

### BOLUM: "{episode_title}"

### KAYNAK PARCALARI:
{chunks_text}

### CIKTI FORMATI (Markdown):

Tam olarak su yapida bir taslik olustur:
- 6-8 ana bolum
- Her bolum icin: baslik, 3-5 madde isareti ile ozet, ve kaynak alintilari
- Alinti formati: [{episode_id}_C####]
- Turkce yaz, teknik terimlerin DE/EN karsiligini parantez icinde belirt

### ORNEK YAPI:
```
# [Video Basligi - Turkce]

## 1. Giris
- Ana konu tanitimi [EPID_C0000]
- Neden onemli [EPID_C0001]

## 2. [Bolum Adi]
- Alt konu 1 [EPID_C0002]
- Alt konu 2 [EPID_C0003]
...

## N. Sonuc ve Ozet
- Ana cikarimlar
```

### HATIRLATMA:
- YALNIZCA kaynaklardaki bilgileri kullan
- Her madde icin en az bir kaynak belirt [{episode_id}_C####]
- Kaynakta olmayan bilgi icin "Kaynaklarda yok" yaz
- Finansal tavsiye VERME
"""
