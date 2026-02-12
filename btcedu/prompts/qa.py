"""QA/fact-check report generation prompt template."""


def build_user_prompt(
    episode_title: str, episode_id: str, chunks_text: str, script_text: str
) -> str:
    """Build user prompt for QA/fact-check report.

    Args:
        episode_title: Original German episode title.
        episode_id: Episode identifier for citation format.
        chunks_text: Formatted chunk text with chunk IDs.
        script_text: Previously generated script text.

    Returns:
        User prompt string.
    """
    return f"""\
## GOREV: Kalite Kontrol ve Dogrulama Raporu Olustur

Asagidaki senaryo metnindeki her onemli iddiayi kaynak parcalariyla karsilastir.
Her iddia icin dogrulama durumunu belirle.

### BOLUM: "{episode_title}"

### SENARYO METNI:
{script_text}

### KAYNAK PARCALARI:
{chunks_text}

### CIKTI FORMATI: JSON dizisi

Her iddia icin:
```json
[
  {{
    "claim": "Senaryodaki iddia (Turkce)",
    "status": "verified|unsupported|kaynaklarda_yok",
    "source_citations": ["{episode_id}_C0001"],
    "source_text_de": "Kaynaktaki Almanca orijinal metin",
    "notes": "Ek aciklamalar (opsiyonel)"
  }}
]
```

### DURUM TANIMLARI:
- **verified**: Iddia kaynaklarda dogrudan destekleniyor
- **unsupported**: Iddia kaynaklarda bulunamadi veya celistiyor
- **kaynaklarda_yok**: Bu konu kaynaklarda hic gecmiyor

### HATIRLATMA:
- Her onemli teknik iddia ve sayi icin dogrulama yap
- Fiyat veya yatirim ile ilgili ifadeler varsa "unsupported" olarak isaretle
- JSON ciktisi ver, baska bir sey yazma
"""
