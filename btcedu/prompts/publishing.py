"""Publishing package generation prompt template."""


def build_user_prompt(
    episode_title: str, episode_id: str, outline_text: str, script_text: str
) -> str:
    """Build user prompt for publishing package (title, description, tags, etc.).

    Args:
        episode_title: Original German episode title.
        episode_id: Episode identifier.
        outline_text: Previously generated outline (Markdown).
        script_text: Previously generated script text.

    Returns:
        User prompt string.
    """
    return f"""\
## GOREV: YouTube Yayinlama Paketi Olustur

Asagidaki taslik ve senaryo metnine dayanarak, YouTube yayinlama icin gerekli \
tum metadatayi olustur.

### BOLUM: "{episode_title}" (orijinal Almanca baslik)

### TASLIK (Outline):
{outline_text}

### SENARYO (kisaltilmis):
{script_text[:3000]}

### CIKTI FORMATI: JSON

```json
{{
  "title_tr": "Turkce video basligi (maks 70 karakter, dikkat cekici)",
  "description_tr": "YouTube aciklama metni (300-500 kelime, SEO uyumlu, Turkce)",
  "chapters": [
    {{"timestamp": "0:00", "title": "Giris"}},
    {{"timestamp": "1:30", "title": "Bolum adi"}}
  ],
  "tags": ["bitcoin", "kripto", "blockchain", "turkce", "egitim"],
  "seo_keywords": ["bitcoin nedir", "bitcoin nasil calisir"],
  "thumbnail_text": "Thumbnail uzerindeki kisa metin (maks 5 kelime)",
  "category": "Education",
  "language": "tr"
}}
```

### HATIRLATMA:
- Baslik Turkce, dikkat cekici ama clickbait OLMASIN
- Aciklamada kaynak podcast'e atif yap
- Tags: Turkce + Ingilizce karisik, Bitcoin/kripto odakli
- Chapters: Taslaktaki bolumleri kullan, tahmini zaman damgalari ver
- Fiyat tahmini veya yatirim vaadi ICERMESIN
- JSON ciktisi ver, baska bir sey yazma
"""
