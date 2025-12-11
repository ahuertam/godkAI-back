import os
import json
import asyncio
from datetime import datetime
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext, JobProcess, WorkerOptions, cli
from livekit.agents.voice.room_io import RoomInputOptions, RoomOutputOptions

try:
    from livekit.plugins import deepgram, google, openai as lk_openai, noise_cancellation, silero
    from livekit.plugins.turn_detector.multilingual import MultilingualModel
    _PLUGINS_AVAILABLE = True
except ImportError:
    _PLUGINS_AVAILABLE = False
    deepgram = google = lk_openai = noise_cancellation = silero = MultilingualModel = None

load_dotenv(".env", override=True)
load_dotenv(".env.local", override=True)

def _read_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

CONFIG = _read_json(CONFIG_PATH)

def _read_prompt() -> str:
    name = CONFIG.get("prompt", "generic")
    custom_path = CONFIG.get("prompt_path")
    if custom_path and os.path.exists(custom_path):
        try:
            with open(custom_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass

    ppath = os.path.join(PROMPTS_DIR, f"{name}.txt")
    if os.path.exists(ppath):
        try:
            with open(ppath, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass

    gpath = os.path.join(PROMPTS_DIR, "generic.txt")
    if os.path.exists(gpath):
        try:
            with open(gpath, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return ""

def _b(v) -> bool:
    return str(v).strip().lower() in {"1", "true", "yes", "on"}

class GodkAgent(Agent):
    def __init__(self, name: str):
        base = CONFIG.get("base_instructions", "Eres un agente de asistencia.")
        prompt = _read_prompt()
        super().__init__(instructions=f"{base}\n\n{prompt}")
        self.name = name
        self.session_id = datetime.now().strftime("%Y%m%d%H%M%S")

async def prewarm(proc: JobProcess):
    if not _PLUGINS_AVAILABLE:
        return

    try:
        msd = float(CONFIG.get("vad_min_speech_duration", 0.1))
        msl = float(CONFIG.get("vad_min_silence_duration", 0.3))
        pad = float(CONFIG.get("vad_padding_duration", 0.1))
        if silero:
            proc.userdata["vad"] = silero.VAD.load(
                min_speech_duration=msd,
                min_silence_duration=msl,
                padding_duration=pad,
            )
    except Exception:
        proc.userdata["vad"] = None

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    room = ctx.room

    llm_model = CONFIG.get("llm_model", "gemini-1.5-flash-latest")
    stt_model = CONFIG.get("stt_model", "nova-2")
    stt_lang = CONFIG.get("stt_language", "es")

    tts_instr = CONFIG.get("tts_instructions", "Habla con acento Español de España.")
    pregen = _b(CONFIG.get("preemptive_generation", True))

    agent = GodkAgent(CONFIG.get("agent_name", "godKAI"))

    llm_provider = None
    if _PLUGINS_AVAILABLE:
        if google:
            llm_provider = google.LLM(model=llm_model)
        elif lk_openai:
            llm_provider = lk_openai.LLM()

    stt_provider = deepgram.STT(model=stt_model, language=stt_lang) if deepgram else None
    tts_provider_name = CONFIG.get("tts_provider", "openai")
    tts_provider = None
    if _PLUGINS_AVAILABLE:
        if tts_provider_name == "google" and google:
            tts_provider = google.TTS(voice=Voice(name=CONFIG.get("tts_voice_name", "es-ES-Standard-A")))
        elif tts_provider_name == "openai" and lk_openai:
            tts_provider = lk_openai.TTS(model=CONFIG.get("tts_model", "tts-1-hd"), voice=CONFIG.get("tts_voice", "fable"))
    turn_provider = MultilingualModel() if MultilingualModel else None
    vad_provider = ctx.proc.userdata.get("vad")

    session = AgentSession(
        llm=llm_provider,
        stt=stt_provider,
        tts=tts_provider,
        turn_detection=turn_provider,
        vad=vad_provider,
        preemptive_generation=pregen,
    )

    @room.on("data_received")
    def on_data_received(packet):
        if packet.topic == "lk-chat-topic":
            msg = json.loads(packet.data)
            if llm_provider:
                asyncio.create_task(session.generate_reply(user_input=msg["message"]))

    nc_provider = noise_cancellation.BVC() if noise_cancellation else None

    await session.start(
        agent=agent,
        room=room,
        room_input_options=RoomInputOptions(
            noise_cancellation=nc_provider,
            close_on_disconnect=True,
        ),
        room_output_options=RoomOutputOptions(audio_enabled=True),
    )

    shutdown_event = asyncio.Event()
    @room.on("disconnected")
    def on_disconnected(_):
        shutdown_event.set()

    await shutdown_event.wait()
    await session.close()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
