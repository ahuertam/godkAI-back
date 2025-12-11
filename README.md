# godKAI-back

Backend de agente conversacional con soporte de voz y texto. Carga su configuración desde `config.json` y el prompt desde `prompts/`.

#  Cómo funciona
En resumen, el flujo es así:
1. Tú hablas.
2. El STT (oído) escucha tu voz y la convierte en texto.
3. El LLM (cerebro) lee ese texto, piensa una respuesta y la escribe.
4. El TTS (boca) lee la respuesta del LLM en voz alta para que la escuches.
Estos tres componentes trabajan juntos en tiempo real para crear la ilusión de que estás conversando con una entidad inteligente.

## Requisitos
- Python 3.11+
- Servidor LiveKit accesible
- Credenciales:
  - `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
  - `DEEPGRAM_API_KEY` (STT)
  - `OPENAI_API_KEY` (TTS)
  - `GOOGLE_API_KEY` (LLM Gemini)

## Instalación

### Usando Google Gemini (Recomendado)

Para usar los modelos de Google Gemini, sigue estos pasos:

1.  **Instala el plugin de Google:**

    ```bash
    uv pip install livekit-plugins-google
    ```

2.  **Configura tu API Key de Google:**

    -   Obtén una API Key desde [Google AI Studio](https://aistudio.google.com/).
    -   Añádela a tu fichero `.env` o `.env.local`:

        ```env
        GOOGLE_API_KEY="tu_api_key_de_google"
        ```

3.  **Actualiza tu `config.json`:**

    Asegúrate de que el `llm_model` en tu fichero de configuración (`config.json` o uno dentro de `/configs`) apunte a un modelo de Gemini:

    ```json
    "llm_model": "gemini-1.5-flash-latest"
    ```

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


### Running the Agent

To run the agent with a specific configuration, use the `--config` argument:

```bash
# Run with the Gandalf configuration
uv run agent.py --config gandalf console

# Run with the generic configuration
uv run agent.py --config generic dev

# Run with the default configuration (config.json)
uv run agent.py console
```

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

## Notas en detalle
- STT (Speech-to-Text / Habla a Texto):

- ¿Qué es? Es el "oído" del agente. Su única función es convertir el audio de la voz (lo que tú dices) en texto escrito.
- En nuestro proyecto: Cuando hablas con el agente, el sistema STT (como nova-2 de Deepgram configurado) transcribe tus palabras a texto para que el "cerebro" pueda entenderlas.
- LLM (Large Language Model / Gran Modelo de Lenguaje):

- ¿Qué es? Es el "cerebro" del agente. Es un modelo de inteligencia artificial muy avanzado (como gemini-1.5-flash-latest ) que ha sido entrenado para entender y generar lenguaje humano.
- En nuestro proyecto: Una vez que el STT le pasa el texto de lo que dijiste, el LLM lo procesa, piensa en una respuesta siguiendo las instrucciones que le dimos (ser Gandalf, proteger el secreto, hablar en español, etc.) y genera una respuesta en formato de texto.
- TTS (Text-to-Speech / Texto a Habla):

- ¿Qué es? Es la "boca" o la "voz" del agente. Hace lo contrario del STT: toma un texto escrito y lo convierte en audio hablado.
- En nuestro proyecto: El sistema TTS (ahora usando Google) recibe la respuesta en texto del LLM y la lee en voz alta, usando la voz que hemos configurado ( es-ES-Standard-A ) y siguiendo las instrucciones de estilo ( Voz masculina grave y profunda... ).