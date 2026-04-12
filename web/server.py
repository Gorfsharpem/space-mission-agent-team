"""
Web Dashboard Server
---------------------
A local web server that provides a browser UI for the space mission agent team.
Agents run in background threads; the UI shows live progress and outputs.

Run:
    python web/server.py
    Open: http://localhost:5000
"""

import json
import os
import sys
import threading
import queue
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv

load_dotenv()

from core import MessageBus, AgentNetwork, SessionState
from core.universal_start import UniversalStartEngine, AGENT_ACTION_MAP
from core.milestone_review import MilestoneReview, MILESTONE_DELIVERABLES
from core.change_request import ChangeRequest, Severity, SourceType
from core.change_propagator import ChangePropagator
from agents import (
    MissionDirectorAgent, ProjectManagerAgent, MissionAnalysisAgent,
    PayloadAgent, EPSAgent, ADCSAgent, ThermalAgent, StructuresAgent,
    TTCAgent, OBSWAgent, PropulsionAgent, MechanicalAgent,
    ElectricalAgent, AntennaAgent, QAPAAgent, DocumentManagerAgent,
    ProjectControllerAgent, RnDManagerAgent, ProposalManagerAgent, BidManagerAgent,
)

from agents.safety_engineer import SafetyEngineerAgent
from agents.ground_segment import GroundSegmentAgent
from agents.launch_campaign import LaunchCampaignAgent
EXTRA_AGENTS = True

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.urandom(24)

OUTPUT_DIR = "outputs"
SESSION_FILE = f"{OUTPUT_DIR}/session_state.json"

# Global event queue for SSE streaming
event_queue: queue.Queue = queue.Queue()
run_lock = threading.Lock()
current_run: dict = {"active": False, "log": [], "results": {}}


# ── Agent network factory ────────────────────────────────────────────────────

def build_network(session: SessionState) -> tuple[AgentNetwork, MessageBus]:
    bus = MessageBus()
    network = AgentNetwork(bus)
    agents = [
        MissionDirectorAgent(), ProjectManagerAgent(), MissionAnalysisAgent(),
        PayloadAgent(), EPSAgent(), ADCSAgent(), ThermalAgent(), StructuresAgent(),
        TTCAgent(), OBSWAgent(), PropulsionAgent(), MechanicalAgent(),
        ElectricalAgent(), AntennaAgent(), QAPAAgent(), DocumentManagerAgent(),
        ProjectControllerAgent(), RnDManagerAgent(), ProposalManagerAgent(), BidManagerAgent(),
    ]
    agents += [SafetyEngineerAgent(), GroundSegmentAgent(), LaunchCampaignAgent()]
    for agent in agents:
        agent.network = network
        network.register(agent)
    return network, bus


# ── SSE log streaming ────────────────────────────────────────────────────────

def log_event(message: str, level: str = "info"):
    entry = {"ts": datetime.utcnow().strftime("%H:%M:%S"), "msg": message, "level": level}
    current_run["log"].append(entry)
    event_queue.put(json.dumps(entry))


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    session = SessionState.load(SESSION_FILE)
    agents = list(AGENT_ACTION_MAP.keys())
    milestones = list(MILESTONE_DELIVERABLES.keys())
    return render_template(
        "index.html",
        session=session,
        agents=sorted(agents),
        milestones=milestones,
        has_api_key=bool(os.environ.get("ANTHROPIC_API_KEY")),
    )


@app.route("/api/session")
def get_session():
    session = SessionState.load(SESSION_FILE)
    return jsonify({
        "mission_name": session.mission_name,
        "phase": session.phase,
        "last_milestone": session.last_milestone,
        "sections": list(session.results.keys()),
        "change_count": len(session.change_log),
        "last_updated": session.last_updated[:19],
    })


@app.route("/api/section/<path:title>")
def get_section(title):
    session = SessionState.load(SESSION_FILE)
    content = session.results.get(title, "")
    return jsonify({"title": title, "content": content})


@app.route("/api/outputs")
def list_outputs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = sorted(
        [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".md")],
        reverse=True,
    )
    return jsonify({"files": files[:50]})


@app.route("/api/output/<filename>")
def get_output(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(path):
        return jsonify({"error": "File not found"}), 404
    with open(path) as f:
        return jsonify({"filename": filename, "content": f.read()})


@app.route("/api/run", methods=["POST"])
def run_agent():
    if current_run["active"]:
        return jsonify({"error": "A run is already in progress"}), 409

    data = request.json
    from_agent = data.get("from_agent", "")
    description = data.get("description", "")
    milestone = data.get("milestone", "")
    severity = data.get("severity", "MAJOR")
    mission_name = data.get("mission_name", "")

    def background_run():
        current_run["active"] = True
        current_run["log"] = []
        current_run["results"] = {}

        try:
            session = SessionState.load(SESSION_FILE)
            if mission_name:
                session.mission_name = mission_name

            log_event(f"Starting: {from_agent or 'Milestone'} | {session.mission_name}", "start")
            network, bus = build_network(session)
            engine = UniversalStartEngine(network, bus, session, output_dir=OUTPUT_DIR)

            if milestone and not from_agent:
                log_event(f"Running {milestone} review — all agents producing deliverables...", "info")
                reviewer = MilestoneReview(network, bus, OUTPUT_DIR)
                session.last_milestone = milestone
                session.save(SESSION_FILE)
                package = reviewer.run(milestone, session.mission_name, context=session.get_context())
                log_event(f"{milestone} complete — {len(package.deliverables)} deliverables", "success")
                current_run["results"] = {d.agent_name: d.content[:500] for d in package.deliverables}
            else:
                engine.start(
                    from_agent=from_agent,
                    description=description,
                    milestone=milestone,
                    severity=severity,
                )
                log_event("Run complete", "success")
                current_run["results"] = {k: v[:500] for k, v in session.results.items()}

            session.save(SESSION_FILE)

        except Exception as e:
            log_event(f"Error: {str(e)}", "error")
        finally:
            current_run["active"] = False
            event_queue.put("__DONE__")

    thread = threading.Thread(target=background_run, daemon=True)
    thread.start()
    return jsonify({"status": "started"})


@app.route("/api/stream")
def stream():
    def generate():
        while True:
            try:
                msg = event_queue.get(timeout=30)
                if msg == "__DONE__":
                    yield f"data: {json.dumps({'done': True})}\n\n"
                    break
                yield f"data: {msg}\n\n"
            except queue.Empty:
                yield "data: {\"ping\": true}\n\n"
    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/status")
def status():
    return jsonify({
        "active": current_run["active"],
        "log": current_run["log"][-20:],
    })


@app.route("/api/clear-session", methods=["POST"])
def clear_session():
    if os.path.isfile(SESSION_FILE):
        os.remove(SESSION_FILE)
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("web/templates", exist_ok=True)
    os.makedirs("web/static", exist_ok=True)
    print("\n🛰  Space Mission Agent Team — Web Dashboard")
    print("   http://localhost:5000\n")
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
