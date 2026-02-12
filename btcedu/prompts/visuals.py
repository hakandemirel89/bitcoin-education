"""Visual plan generation prompt template."""


def build_user_prompt(
    episode_title: str, episode_id: str, chunks_text: str, outline_text: str
) -> str:
    """Build user prompt for visual/diagram plan generation.

    Args:
        episode_title: Original German episode title.
        episode_id: Episode identifier for citation format.
        chunks_text: Formatted chunk text with chunk IDs.
        outline_text: Previously generated outline (Markdown).

    Returns:
        User prompt string.
    """
    return f"""\
## GOREV: Gorsel Plan Olustur

Asagidaki taslak ve kaynak parcalarina dayanarak, video icin gorsel bir plan olustur.
Her bolum icin uygun diyagram, grafik veya infografik onerileri yap.

### BOLUM: "{episode_title}"

### TASLIK (Outline):
{outline_text}

### KAYNAK PARCALARI:
{chunks_text}

### CIKTI FORMATI: JSON dizisi

Her bolum icin gorsel onerisi:
```json
[
  {{
    "section": "Bolum adi",
    "visual_type": "diagram|infographic|chart|comparison|timeline|flowchart",
    "description_tr": "Gorselin Turkce aciklamasi",
    "labels_tr": ["Etiket 1", "Etiket 2"],
    "labels_de": ["Deutsches Label 1"],
    "data_points": ["Gorsel icin kullanilacak veri noktalari"],
    "citations": ["{episode_id}_C0001"]
  }}
]
```

### HATIRLATMA:
- YALNIZCA kaynaklardaki bilgilere dayanan gorseller oner
- Her gorsel icin kaynak belirt [{episode_id}_C####]
- Kaynakta olmayan veri icin "Kaynaklarda yok" yaz
- Fiyat grafigi veya yatirim performansi gorseli ONERME
- JSON ciktisi ver, baska bir sey yazma
"""
