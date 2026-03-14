# GLOBAL SYSTEM RULES — BLADINA WORKSTATION

## Hardware (DO NOT MODIFY)
- OS: Ubuntu 24.04
- GPU: NVIDIA RTX 3060 Ti (8GB VRAM)
- CUDA: 12.8
- Driver: nvidia-570.211.01 (LOCKED — never update)
- RAM: 32GB
- Ollama: localhost:11434 (100% GPU)

## Drive Layout
- SSD: ~/Projects (nvme) — ALL active development
- HDD: /media/bladina/Archive (sata) — Storage only
- Models & LoRAs: /media/bladina/Archive/Archives/

## Forbidden Actions
1. Never run apt upgrade or apt dist-upgrade
2. Never install nvidia-*, cuda-*, or driver packages
3. Never modify /etc/, /boot/, /usr/lib/, /sys/
4. Never use pip when uv is available — always use uv pip install
5. Never download >300MB without asking the user
6. Never install to Archive drive
7. Never modify GPU/CUDA/driver config
8. Never use sudo outside ~/Projects without asking
9. Never download models/LoRAs without checking local paths first

## Required Actions
1. Always use uv pip install (not pip)
2. Always create venv before installing Python packages
3. Always install to ~/Projects (SSD)
4. Always test after every install
5. Always verify GPU with nvidia-smi
6. Always ask before system changes
7. Always check Archive for existing assets first
8. Always search local model folders before downloading ANY model

## Existing Assets (DO NOT REDOWNLOAD)
- AnythingLLM: /media/bladina/Archive/home/mo/AnythingLLMDesktop.AppImage
- NLTK Data: /media/bladina/Archive/home/mo/nltk_data/
- Ollama Models: Already installed (llama3.2)

## Local Models and LoRAs (SEARCH HERE FIRST)
- Base path: /media/bladina/Archive/Archives/
- Before downloading ANY model, LoRA, checkpoint, or weights:
  1. Search: find /media/bladina/Archive/Archives/ -name "*<model_name>*"
  2. If found: symlink or copy to ~/Projects/<project>/models/
  3. If NOT found: ASK user before downloading
- Common extensions: .safetensors, .ckpt, .pt, .pth, .bin, .gguf

## Symlink Policy (DO NOT COPY LARGE FILES)
- For models over 100MB, create symlinks instead of copying
- Example: ln -s /media/bladina/Archive/Archives/<model> ~/Projects/ComfyUI/models/<type>/

## Installation Paths
- ComfyUI: ~/Projects/ComfyUI
- AnythingLLM: ~/Projects/AnythingLLM
- Python venvs: ~/Projects/<project>/.venv
- Model symlinks: ~/Projects/<project>/models/ -> /media/bladina/Archive/Archives/

## Post-Install Test Protocol
1. Verify command exists
2. Check version
3. Verify GPU detection
4. Report PASS or FAIL

## Ask User Before
- apt install commands
- Downloads over 300MB
- sudo outside ~/Projects
- Pulling/downloading new models
- Any model not found in /media/bladina/Archive/Archives/

## Current Project
- Name: Autonomous Video Pipeline (OpenClaw MVP)
- Deadline: March 15, 2026
- Stack: ComfyUI + AnythingLLM + Ollama + Cognee
- Cognee MCP Server: ~/Desktop/install_link/cognee/
