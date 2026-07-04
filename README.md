# Autonomous Security Orchestration & Incident Response Pipeline

An automated system that detects, investigates, and blocks cyberattacks on a web server without human intervention — running entirely on your local machine using Docker.

---

## What It Does

When an attacker hits the server, the system:

1. **Detects** the attack by monitoring Nginx access logs in real time
2. **Investigates** by cross-referencing the attacker's IP with a global threat database (AbuseIPDB) and analyzing the logs with a local AI model (Ollama)
3. **Remediates** by automatically blocking the IP at the firewall level and sending an incident report to Slack

All of this happens in seconds, with zero human intervention.

---

## Architecture

```
Attacker
   │
   ▼
┌─────────────────────────────────────────────────────────┐
│                   Docker Network (security-net)          │
│                                                          │
│  ┌──────────┐    logs     ┌─────────────┐               │
│  │  Nginx   │ ──────────► │ Log Watcher │               │
│  │ :80      │             │  (Python)   │               │
│  └──────────┘             └──────┬──────┘               │
│                                  │ webhook               │
│                                  ▼                       │
│                           ┌─────────────┐               │
│                           │     n8n     │               │
│                           │  :5678      │               │
│                           └──────┬──────┘               │
│                    ┌─────────────┼─────────────┐        │
│                    ▼             ▼             ▼        │
│             ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│             │AbuseIPDB │  │  Ollama  │  │ Firewall │   │
│             │  (API)   │  │ :11434   │  │ API :5000│   │
│             └──────────┘  └──────────┘  └──────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                            Slack #incidents
```

---

## Stack

| Component | Tool | Purpose |
|---|---|---|
| Web server | Nginx | Target server being protected |
| Orchestration | n8n | Connects all services into a workflow |
| AI analysis | Ollama (llama3.2) | Rates attack severity 1-10 |
| Log monitoring | Python | Tails Nginx logs, detects attacks |
| Firewall | Flask + iptables | Blocks malicious IPs at network level |
| Threat intel | AbuseIPDB | IP reputation database (0-100 score) |
| Alerting | Slack | Incident notifications |

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com/download) with `llama3.2` pulled
- AbuseIPDB API key (free at [abuseipdb.com](https://www.abuseipdb.com/register))
- Slack incoming webhook URL

---

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/kalbe-raza/Autonomous-Security-Orchestration.git
cd Autonomous-Security-Orchestration
```

**2. Create the `.env` file**
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
ABUSEIPDB_API_KEY=your_api_key_here
```

**3. Pull the AI model**
```bash
ollama pull llama3.2
```

**4. Start all services**
```bash
docker-compose up --build
```

**5. Configure the n8n workflow**

Open `http://localhost:5678` and import the workflow (see [n8n Workflow](#n8n-workflow) below).

---

## n8n Workflow

The workflow is triggered by a webhook and runs the following nodes in sequence:

1. **Webhook** — receives alert from log-watcher `{ attacker_ip, reason, log_sample }`
2. **AbuseIPDB lookup** — checks IP reputation score and country
3. **Ollama analysis** — AI rates severity 1-10 based on logs + reputation
4. **IF node** — branches on severity > 6
5. **Block IP** — calls firewall-api to apply iptables rule
6. **Slack alert** — posts incident report to `#incidents`

---

## Testing

Run the attack simulator to trigger the full pipeline:

```bash
python simulate_attack.py
```

Options:
- `1` — Brute force (rate limit trigger: 50 requests in ~5 seconds)
- `2` — Pattern attacks (SQLi, XSS, path traversal, file inclusion)
- `3` — Both simultaneously

Watch the pipeline fire: logs → detection → AI analysis → IP block → Slack alert.

---

## Project Structure

```
.
├── docker-compose.yml       # Orchestrates all services
├── simulate_attack.py       # Attack simulation script
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf           # Web server config with access logging
├── log-watcher/
│   ├── Dockerfile
│   └── watcher.py           # Monitors logs, fires webhook on attack
├── firewall-api/
│   ├── Dockerfile
│   ├── app.py               # Flask API wrapping iptables
│   └── requirements.txt
└── n8n/                     # n8n workflow data (auto-generated)
```
