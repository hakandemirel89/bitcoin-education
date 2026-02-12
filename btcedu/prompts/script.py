"""Long-form script generation prompt template."""


def build_user_prompt(
    episode_title: str, episode_id: str, chunks_text: str, outline_text: str
) -> str:
    """Build user prompt for long-form script generation.

    Args:
        episode_title: Original German episode title.
        episode_id: Episode identifier for citation format.
        chunks_text: Formatted chunk text with chunk IDs.
        outline_text: Previously generated outline (Markdown).

    Returns:
        User prompt string.
    """
    return f"""\
## GOREV: Uzun Video Senaryosu Olustur (12-15 dakika)

Asagidaki taslak ve kaynak parcalarina dayanarak, Turkce bir YouTube video senaryosu yaz.
Senaryo yaklasik 12-15 dakikalik bir video icin uygun olmali (~2000-2500 kelime).

### BOLUM: "{episode_title}"

### TASLIK (Outline):
{outline_text}

### KAYNAK PARCALARI:
{chunks_text}

### CIKTI FORMATI (Markdown):

Taslaktaki bolumleri takip et. Her bolum icin:
1. Konusmaci metni (dogal, sohbet tarzinda)
2. Her onemli iddia icin kaynak alintisi [{episode_id}_C####]
3. Teknik terimlerin aciklamasi (Turkce, parantez icinde DE/EN)

### YAPI:
```
# [Video Basligi]

## Giris
[Seyirciye hitap, konuyu tanit, neden onemli...]

## [Bolum 1 Adi]
[Aciklama, ornekler, kaynaklar...]

## [Bolum 2 Adi]
...

## Sonuc
[Ozet, ana cikarimlar, harekete gecirici mesaj]

---
Bu icerik yalnizca egitim amaclidir...
```

### HATIRLATMA:
- YALNIZCA kaynaklardaki bilgileri kullan
- Her bolumdeki her iddia icin kaynak belirt [{episode_id}_C####]
- Kaynakta olmayan bilgi icin "Kaynaklarda yok" yaz
- Fiyat tahmini, alim/satim tavsiyesi VERME
- Dogal Turkce kullan, tercume havasi verme
"""
