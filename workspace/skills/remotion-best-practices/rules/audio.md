
## AI Sound Generation (ElevenLabs)

Generate custom tracks for your video using the ElevenLabs API.

### API Endpoint
`POST https://api.elevenlabs.io/v1/sound-generation`

### Example Request
```bash
curl -X POST https://api.elevenlabs.io/v1/sound-generation \
  -H "xi-api-key: <YOUR_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Cinematic tech promo intro, deep bass rumble start, glitchy typing sounds, then high energy cyberpunk beat kicks in at 2 seconds, ends with a digital power down sound",
    "duration_seconds": 12,
    "prompt_influence": 0.7
  }' \
  --output public/background.mp3
```

### Prompt Engineering Tips
- **Structure:** Describe the flow over time (Start -> Middle -> End).
- **Keywords:** Use "Cinematic", "Rhythmic", "Glitchy", "Build-up".
- **Duration:** Match `duration_seconds` to your video length to avoid awkward loops.
- **Influence:** `prompt_influence` (0.0-1.0). Higher = stricter adherence to text. ~0.7 is a good balance.

### Troubleshooting AI Audio
- **"Silent then Loud":** Prompts like "deep rumble" may produce sub-bass that sounds silent on small speakers, followed by loud beats.
- **Fix:** Use `FadeIn` volume automation in Remotion to smooth entry.
- **Fix:** Avoid "rumble" or "silence" in prompts; use "atmospheric" or "pad" instead.
