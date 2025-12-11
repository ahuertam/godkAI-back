# godKAI-back

Backend de agente conversacional con soporte de voz y texto. Carga su configuración desde `config.json` y el prompt desde `prompts/`.

## Requisitos
- Python 3.11+
- Servidor LiveKit accesible
- Credenciales:
  - `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
  - `DEEPGRAM_API_KEY` (STT)
  - `OPENAI_API_KEY` (TTS)
  - `GOOGLE_API_KEY` (LLM Gemini)

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U livekit-agents livekit-plugins python-dotenv
```

## Configuración (`config.json`)
```json
{
  "agent_name": "godKAI",
  "base_instructions": "Eres un agente de asistencia que responde por voz y texto.",
  "prompt": "gandalf",
  "llm_model": "gemini-2.5-flash-lite",
  "stt_model": "nova-3",
  "stt_language": "es",
  "tts_model": "gpt-4o-mini-tts",
  "tts_voice": "nova",
  "tts_instructions": "Habla con acento Español de España.",
  "preemptive_generation": true,
  "vad_min_speech_duration": 0.1,
  "vad_min_silence_duration": 0.3,
  "vad_padding_duration": 0.1
}
```
- `prompt`: nombre de un `.txt` en `prompts/` (ej. `gandalf`).
- Si no existe, se usa `prompts/generic.txt`.
- Opcional `prompt_path`: ruta absoluta a un `.txt` externo.

## Prompts
- Coloca prompts en `prompts/` (`generic.txt`, `gandalf.txt`, etc.).
- Ejemplo `prompts/generic.txt`:
```text
Eres un agente conversacional.
Respondes de forma clara y breve.
Aceptas comandos por texto y consultas por voz.
Si no se proporcionan instrucciones específicas, mantén el contexto general.
```

## Variables de entorno
```env
LIVEKIT_URL=https://<tu-livekit-url>
LIVEKIT_API_KEY=<tu-api-key>
LIVEKIT_API_SECRET=<tu-api-secret>
DEEPGRAM_API_KEY=<tu-deepgram-key>
OPENAI_API_KEY=<tu-openai-key>
GOOGLE_API_KEY=<tu-google-key>
```

## Ejecución
```bash
python agent.py
```
- Conecta al servidor LiveKit.
- Acepta:
  - Texto: mensajes `lk.chat` y entradas de `text_input_cb`.
  - Voz: STT (Deepgram), TTS (OpenAI), detección de turnos (MultilingualModel) y VAD (Silero).

## Interacción
- Texto: envía `topic: lk.chat` desde un cliente LiveKit.
- Voz: conéctate a la sala; el agente detecta turnos y responde con TTS.

## Personalización
- Ajusta modelos/idioma/voz en `config.json`.
- Cambia `base_instructions`.
- Usa `prompt_path` para reutilizar prompts externos.

## Troubleshooting
- Conexión: revisa `LIVEKIT_URL` y credenciales.
- STT/TTS: confirma `DEEPGRAM_API_KEY` y `OPENAI_API_KEY`.
- Prompt: verifica `prompts/<nombre>.txt` o `prompt_path`.

## Estructura
- `agent.py`: agente y sesión LiveKit
- `config.json`: configuración del agente
- `prompts/`: ficheros de prompt