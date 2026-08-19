import os
import json
import base64
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

load_dotenv()
genai_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
for m in genai_client.models.list():
    print(m.name)
def generate_with_fallback(contents):
    """
    Tries a few models in order, since Gemini's free tier models
    frequently return 503 (high demand). Falls back automatically
    instead of failing the whole request.
    """
    models_to_try = ["gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-flash-lite-latest"]
    last_error = None

    for model_name in models_to_try:
        try:
            response = genai_client.models.generate_content(
                model=model_name,
                contents=contents,
            )
            return response
        except Exception as exc:
            last_error = exc
            continue

    raise last_error    

from model import Breadboard
from wiring import NetlistBuilder
from components import Resistor, LED, Battery, Capacitor, Switch, Diode, Inductor, Transistor
from comparision import compare_netlists
from hole_utils import parse_hole_key

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://wyrdly-frontend.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Define the SHAPE of incoming data (pydantic validates it automatically) ---

class HoleRef(BaseModel):
    key: str

class WireInput(BaseModel):
    from_hole: HoleRef
    to_hole: HoleRef

class ComponentInput(BaseModel):
    type: str
    id: str
    from_hole: HoleRef
    to_hole: HoleRef
    value: Optional[float] = None

class CircuitCheckRequest(BaseModel):
    wires: List[WireInput]
    components: List[ComponentInput]
    reference_circuit_name: Optional[str] = None
    custom_reference: Optional[dict] = None
    
class ExplainRequest(BaseModel):
    faults: List[dict]
    skill_level: str = "beginner"  # "beginner" | "intermediate" | "advanced"


@app.post("/explain-faults")
def explain_faults(request: ExplainRequest):
    if not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="GOOGLE_API_KEY is not set. Add it to breadboard/.env and restart the server.",
        )

    fault_summary = "\n".join(
        f"- [{f['type']}] {f['detail']}" for f in request.faults
    )

    system_prompt = (
        "You are a friendly electronics tutor helping a student debug a breadboard circuit. "
        "You will be given a list of VERIFIED faults found by a separate, reliable circuit-checking "
        "system. Do NOT invent any additional faults or claims beyond what is listed. "
        "Explain each fault clearly, why it matters electrically, and how to fix it. "
        f"Adjust your explanation depth for a {request.skill_level} student. "
        "Keep it concise -- a few sentences per fault, no long preamble."
    )

    full_prompt = f"{system_prompt}\n\nHere are the detected faults:\n{fault_summary}"

    try:
        response = generate_with_fallback(full_prompt)
        
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not generate explanation: {exc}",
        ) from exc

    return {"explanation": response.text}
@app.post("/parse-schematic")
async def parse_schematic(file: UploadFile = File(...)):
    image_bytes = await file.read()

    prompt = (
        "You are reading a hand-drawn or textbook circuit schematic diagram. "
        "Identify each component (resistor, LED, battery, capacitor, switch) and how "
        "they connect. Output ONLY valid JSON in this exact shape, no other text:\n"
        '{"circuit_name": "...", "components": [{"name": "R1", "type": "resistor", '
        '"resistance_ohms": 220}], "expected_nets": [{"pins": [["BAT1","positive"],'
        '["R1","pin1"]]}]}\n'
        "Use component name conventions: R for resistor, LED for LED (pins: anode/cathode), "
        "BAT for battery (pins: positive/negative), C for capacitor, SW for switch (pins: pin1/pin2)."
    )

    try:
        response = generate_with_fallback([
            types.Part.from_bytes(data=image_bytes, mime_type=file.content_type),
            prompt
        ])
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1].replace("json", "", 1).strip()
        parsed = json.loads(text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not parse schematic: {exc}") from exc

    return parsed


@app.get("/ping")
def ping():
    return {"status": "backend is alive"}


@app.post("/check-circuit")
def check_circuit(request: CircuitCheckRequest):
    board = Breadboard()
    netlist = NetlistBuilder(board)

    # 1. Place all user wires
    for wire in request.wires:
        from_hole = parse_hole_key(wire.from_hole.key)
        to_hole = parse_hole_key(wire.to_hole.key)
        netlist.add_wire(from_hole, to_hole)

    # 2. Place all user components
    component_classes = {
        "resistor": Resistor,
        "led": LED,
        "battery": Battery,
        "capacitor": Capacitor,
        "switch": Switch,
        "diode": Diode,
        "inductor": Inductor,
        "transistor": Transistor
    }

    for comp in request.components:
        from_hole = parse_hole_key(comp.from_hole.key)
        to_hole = parse_hole_key(comp.to_hole.key)

        if comp.type == "resistor":
            obj = Resistor(comp.id, from_hole, to_hole, resistance_ohms=comp.value or 220)
        elif comp.type == "led":
            obj = LED(comp.id, from_hole, to_hole)
        elif comp.type == "battery":
            obj = Battery(comp.id, from_hole, to_hole, voltage=comp.value or 5.0)
        elif comp.type == "capacitor":
            obj = Capacitor(comp.id, from_hole, to_hole, capacitance_farads=comp.value or 0.0001)
        elif comp.type == "switch":
            obj = Switch(comp.id, from_hole, to_hole)
        elif comp.type == "diode":
            obj = Diode(comp.id, from_hole, to_hole)
        elif comp.type == "inductor":
            obj = Inductor(comp.id, from_hole, to_hole, inductance_henries=comp.value or 0.001)
        elif comp.type == "transistor":
            obj = Transistor(comp.id, from_hole, to_hole)
        else:
            continue  # unknown type, skip

        netlist.add_component(obj)

    # 3. Build the user's netlist
    user_result = netlist.build_netlist()

    # 4. Load the requested reference circuit
    if request.custom_reference:
        reference = request.custom_reference
    else:
        ref_path = f"reference_circuits/{request.reference_circuit_name}.json"
        with open(ref_path) as f:
            reference = json.load(f)
    # 5. Compare and return the report
    report = compare_netlists(user_result, reference["expected_nets"])

    return {
        "correct": report["correct"],
        "faults": report["faults"]
    }
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)    