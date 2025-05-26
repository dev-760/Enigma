#!/usr/bin/env python3
import os
import sys
import uuid
import json
import asyncio
import threading
import base64
import time
import socket
import struct
import wave
import secrets
from datetime import datetime
from pathlib import Path

# Crypto
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Audio
import pyaudio

# Signaling & P2P
from aiohttp import ClientSession, WSMsgType
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceServer

# ─── ASCII Header & Menus ────────────────────────────────────────────────────

def display_header():
    print("""
╔══════════════════════════════════════╗
║               Enigma                 ║
║               v0.1                   ║
║                                      ║
║       Developed by: dev-760          ║
╚══════════════════════════════════════╝
* *
""".strip("\n"))

def display_main_menu():
    display_header()
    print("1) Start Group Chat (new room)")
    print("2) Connect to Group Chat")
    print("3) Set Username")
    print("4) Audio Settings")
    print("5) View Key Fingerprint")
    print("6) Help")
    print("7) Exit\n")

def display_chat_menu():
    print("""
╔═════════════ CHAT COMMANDS ════════════╗
║  /voice   - Start/stop live voice chat  ║
║  /record  - Start recording audio       ║
║  /stop    - Stop current recording      ║
║  /play    - Play audio file             ║
║  /send    - Send audio file             ║
║  /file    - Send any file               ║
║  /peers   - List connected peers        ║
║  /clear   - Clear screen                ║
║  /help    - Show this menu              ║
║  /quit    - Exit to main menu           ║
╚════════════════════════════════════════╝
""".strip("\n"))

def display_audio_menu():
    display_header()
    print("""
╔═════════════ AUDIO SETTINGS ═══════════╗
║ 1) List Audio Devices                  ║
║ 2) Test Microphone                     ║
║ 3) Test Speakers                       ║
║ 4) Record Test Audio                   ║
║ 5) Back to Main Menu                   ║
╚════════════════════════════════════════╝
""".strip("\n"))

class Colors:
    RED     = '\033[91m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    BLUE    = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN    = '\033[96m'
    WHITE   = '\033[97m'
    BOLD    = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET   = '\033[0m'

# ─── CRYPTO ENGINE ────────────────────────────────────────────────────────────

class CryptoEngine:
    def __init__(self):
        self.private_key = None
        self.public_key  = None
        self.peer_public_key = None
        self.session_key = None

    def generate_keypair(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=4096, backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def export_public_key(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def import_peer_public_key(self, pem_data):
        self.peer_public_key = serialization.load_pem_public_key(
            pem_data, backend=default_backend()
        )

    def generate_session_key(self):
        self.session_key = secrets.token_bytes(32)

    def encrypt_session_key(self):
        if not self.peer_public_key or not self.session_key:
            raise ValueError("Peer public key or session key missing")
        return self.peer_public_key.encrypt(
            self.session_key,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def decrypt_session_key(self, encrypted_key):
        self.session_key = self.private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def encrypt_data(self, data: bytes):
        if not self.session_key:
            raise ValueError("Session key missing")
        nonce = secrets.token_bytes(12)
        cipher = Cipher(
            algorithms.AES(self.session_key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ct = encryptor.update(data) + encryptor.finalize()
        return {'nonce': nonce, 'ciphertext': ct, 'tag': encryptor.tag}

    def decrypt_data(self, enc):
        cipher = Cipher(
            algorithms.AES(self.session_key),
            modes.GCM(enc['nonce'], enc['tag']),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        return decryptor.update(enc['ciphertext']) + decryptor.finalize()

# ─── AUDIO ENGINE ─────────────────────────────────────────────────────────────

class AudioEngine:
    def __init__(self, crypto: CryptoEngine):
        self.crypto = crypto
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.is_playing_live = False
        self.record_to_file = False
        self.recorded_frames = []
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        Path("recordings").mkdir(exist_ok=True)
        Path("received_audio").mkdir(exist_ok=True)

    # -- live voice, recording, playback, send/receive audio file methods --
    # (Paste your existing AudioEngine implementations here, unchanged,
    #  plus add stop_recording() and stop_live_playback() as described earlier.)
    def stop_recording(self):
        self.is_recording = False
    def stop_live_playback(self):
        if hasattr(self, 'live_play_stream'):
            self.live_play_stream.stop_stream()
            self.live_play_stream.close()
        self.is_playing_live = False

# ─── GROUP-P2P NODE ───────────────────────────────────────────────────────────

class P2PNode:
    def __init__(self, signaling_url):
        # Legacy crypto/audio
        self.crypto = CryptoEngine()
        self.crypto.generate_keypair()
        self.audio = AudioEngine(self.crypto)
        self.username = "Anon"
        self.peers = {}
        self.running = False

        # aiortc group chat
        self.id = str(uuid.uuid4())
        self.room = None
        self.signaling_url = signaling_url.rstrip("/")
        self.ws = None
        self.pc = RTCPeerConnection(
            iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])]
        )
        self.data_channels = {}

        @self.pc.on("icecandidate")
        async def on_ice(evt):
            if evt.candidate:
                await self._send_signal({
                    "type": "candidate", "from": self.id,
                    "candidate": evt.candidate.to_sdp(),
                    "sdpMid": evt.candidate.sdpMid,
                    "sdpMLineIndex": evt.candidate.sdpMLineIndex
                })

        @self.pc.on("datachannel")
        def on_dc(channel):
            peer_id = channel.label
            self._register_channel(peer_id, channel)

    async def _send_signal(self, msg):
        await self.ws.send_str(json.dumps(msg))

    async def _signaling_loop(self):
        from aiortc.sdp import candidate_from_sdp
        async for msg in self.ws:
            if msg.type != WSMsgType.TEXT:
                continue
            data = json.loads(msg.data)
            sender = data.get("from")
            if sender == self.id:
                continue

            t = data["type"]
            if t == "offer":
                offer = RTCSessionDescription(sdp=data["sdp"], type=data["sdpType"])
                await self.pc.setRemoteDescription(offer)
                answer = await self.pc.createAnswer()
                await self.pc.setLocalDescription(answer)
                await self._send_signal({
                    "type": "answer", "from": self.id,
                    "sdp": self.pc.localDescription.sdp,
                    "sdpType": self.pc.localDescription.type
                })
            elif t == "answer":
                ans = RTCSessionDescription(sdp=data["sdp"], type=data["sdpType"])
                await self.pc.setRemoteDescription(ans)
            elif t == "candidate":
                cand = candidate_from_sdp(
                    data["candidate"], data["sdpMid"], data["sdpMLineIndex"]
                )
                await self.pc.addIceCandidate(cand)

    def _run_async(self, coro):
        def target(): asyncio.run(coro)
        threading.Thread(target=target, daemon=True).start()

    def _register_channel(self, peer_id, channel):
        self.data_channels[peer_id] = channel

        @channel.on("open")
        def _():
            print(f"{Colors.CYAN}🔗 Connected to peer {peer_id}{Colors.RESET}")

        @channel.on("message")
        def _(msg):
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"\n{Colors.MAGENTA}[{ts}] {peer_id}: {msg}{Colors.RESET}")
            print(f"{Colors.WHITE}[{self.username}] {Colors.RESET}", end="", flush=True)

    def start_group(self):
        self.room = str(uuid.uuid4())[:8]
        print(f"{Colors.GREEN}🔗 Your room ID: {self.room}{Colors.RESET}")
        self._run_async(self._join_room())

    def connect_to_group(self):
        room = input(f"{Colors.WHITE}Enter room ID: {Colors.RESET}").strip()
        if not room:
            print(f"{Colors.RED}❌ Room ID required{Colors.RESET}")
            return False
        self.room = room
        self._run_async(self._join_room())
        return True

    async def _join_room(self):
        session = ClientSession()
        self.ws = await session.ws_connect(f"{self.signaling_url}/{self.room}")
        asyncio.create_task(self._signaling_loop())

        dc = self.pc.createDataChannel(self.id)
        self._register_channel(self.id, dc)

        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        await self._send_signal({
            "type": "offer", "from": self.id,
            "sdp": self.pc.localDescription.sdp,
            "sdpType": self.pc.localDescription.type
        })

    # override legacy broadcast → use data channels
    def broadcast_message(self, _, content):
        text = content if isinstance(content, str) else json.dumps(content)
        sent = False
        for dc in self.data_channels.values():
            if dc.readyState == "open":
                dc.send(text)
                sent = True
        return sent

    # (legacy handlers: start_chat_interface, list_peers, send_file, etc.)
    # Paste your existing P2PNode methods for chat interface, help, cleanup, audio_settings_menu, etc.

# ─── AUDIO SETTINGS MENU ─────────────────────────────────────────────────────

def audio_settings_menu(node):
    while True:
        display_audio_menu()
        choice = input("Enter choice (1-5): ").strip()
        if choice == '1':
            node.audio.list_audio_devices()
            input("Press Enter to continue…")
        elif choice == '2':
            node.audio.start_audio_recording("test_mic.wav")
            time.sleep(5)
            node.audio.stop_recording()
            node.audio.play_audio_file("test_mic.wav")
            os.remove("test_mic.wav")
        elif choice == '3':
            print("Speaker test not implemented")
            input("Press Enter…")
        elif choice == '4':
            filename = input("Filename (or Enter): ").strip() or None
            node.audio.start_audio_recording(filename)
            input("Press Enter to stop…")
            node.audio.stop_recording()
        elif choice == '5':
            break
        else:
            print("Invalid choice")
            time.sleep(1)

# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    os.system('clear' if os.name=='posix' else 'cls')
    node = P2PNode(signaling_url="ws://your.server:8765/ws")
    try:
        while True:
            display_main_menu()
            choice = input("Enter your choice (1-7): ").strip()
            if choice == '1':
                node.start_group()
                input(f"Joined room {node.room}! Press Enter to chat…")
                node.start_chat_interface()
            elif choice == '2':
                if node.connect_to_group():
                    input(f"Joined room {node.room}! Press Enter to chat…")
                    node.start_chat_interface()
            elif choice == '3':
                username = input("Enter your username: ").strip()
                if username:
                    node.username = username
                    print(f"Username set to: {username}")
                time.sleep(1)
            elif choice == '4':
                audio_settings_menu(node)
            elif choice == '5':
                fp = node.get_key_fingerprint()
                print(f"🔑 Your RSA Key Fingerprint:\n{fp}")
                input("Press Enter…")
            elif choice == '6':
                os.system('clear')
                display_header()
                print("Help: …")  # paste your full help block here
                input("Press Enter…")
            elif choice == '7':
                print("👋 Thank you for using Enigma!")
                break
            else:
                print("Invalid choice")
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    finally:
        node.cleanup()

if __name__ == "__main__":
    main()
