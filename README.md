
╔══════════════════════════════════════╗
║              Enigma                 ║
║               v0.1                  ║
║                                      ║
║        Developed by: dev-760         ║
╚══════════════════════════════════════╝

---

# Enigma

**Enigma** is a secure peer-to-peer communication system that supports encrypted group messaging, live voice chat, and NAT traversal using STUN/TURN. Built using Python, WebRTC (`aiortc`), and a custom signaling server, Enigma provides a full-mesh encrypted network with no centralized data storage.

---

## ✨ Features

- ✅ **End-to-End Encryption**
  - RSA-4096 for key exchange
  - AES-256-GCM for encrypted messages and files

- 💬 **Group Chat Support**
  - Full-mesh P2P communication between multiple participants
  - CLI chat interface with user handles and peer tracking

- 🔊 **Real-Time Voice Chat**
  - Encrypted live voice communication between users
  - Optional audio recording and playback functionality

- 🌍 **NAT Traversal with STUN/TURN**
  - STUN server for NAT punchthrough
  - TURN server configuration supported

- 🔗 **WebSocket Signaling**
  - Minimal signaling server to exchange SDP and ICE candidates

- 🛠️ **Command Line Interface**
  - `/help`, `/voice`, `/record`, `/file`, `/play`, `/quit`, and more

---

## 📦 Project Structure

```

Enigma/
├── enigma.py           # Main client application
├── signaling.py        # WebSocket signaling server
├── README.md           # This file
├── recordings/         # Audio recordings directory
├── received\_audio/     # Received audio files
└── received\_files/     # General received files

````

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/dev-760/Enigma.git
cd Enigma
````

### 2. Install Requirements

Install all required dependencies:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install cryptography pyaudio aiohttp aiortc
```

> You may need to install PortAudio on your system to use `pyaudio`. On Ubuntu:
> `sudo apt install portaudio19-dev`

---

## 🧪 Running the System

### 1. Start the Signaling Server

```bash
python signaling.py
```

By default, it runs on `ws://localhost:8765`.

### 2. Start the Enigma Client

In another terminal window:

```bash
python enigma.py
```

You'll be prompted to:

* Create a room (host)
* Join a room (connect)
* Set your display name
* Use voice & audio tools
* View your public key fingerprint

---

## 💬 Chat Commands (In-Session)

Use the following commands after joining a room:

| Command   | Description                          |
| --------- | ------------------------------------ |
| `/voice`  | Start/stop real-time encrypted voice |
| `/record` | Begin recording your microphone      |
| `/stop`   | Stop current recording               |
| `/play`   | Play a `.wav` file                   |
| `/send`   | Send an audio file                   |
| `/file`   | Send any general file                |
| `/peers`  | List currently connected users       |
| `/clear`  | Clear the screen                     |
| `/help`   | Display all available commands       |
| `/quit`   | Exit chat and return to main menu    |

---

## 🧱 Configuration

You can customize certain system behaviors:

### Modify STUN/TURN Servers

Edit the ICE server list in `enigma.py`:

```python
self.pc = RTCPeerConnection(iceServers=[
    RTCIceServer(urls=["stun:stun.l.google.com:19302"]),
    RTCIceServer(
        urls=["turn:turn.example.com:3478"],
        username="user",
        credential="pass"
    )
])
```

### Change Signaling Server

Update the signaling server URL in the `P2PNode` constructor:

```python
node = P2PNode(signaling_url="ws://your-host.com:8765/ws")
```

---

## 📸 Screenshots

```
╔══════════════════════════════════════╗
║              Enigma                 ║
║               v0.1                  ║
║                                      ║
║        Developed by: dev-760         ║
╚══════════════════════════════════════╝

1) Start New Room
2) Join Room
3) Set Username
4) Audio Tools
5) View Key Fingerprint
6) Help
7) Exit

>> Connected to Room ID: 3f8a91
>> Peer connected: Alice
>> /voice to start speaking
```

---

## 🙏 Credits

* Designed & Developed by **dev-760**
* Enigma v0.1
* Built with Python, WebRTC (aiortc), and AES/RSA crypto

```

Let me know if you'd like me to generate a `requirements.txt`, add deployment instructions, or make a versioned badge f
