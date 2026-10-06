from datetime import datetime, timezone
from typing import Literal, Optional
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from pydantic import BaseModel
 
app = FastAPI()
Role = Literal["doctor", "nurse", "patient", "billing"]
 
class User(BaseModel):
    id: str
    role: Role
    patient_id: Optional[str] = None  # set only for role == "patient"
 
# ---- Provided: stand-ins for real auth and database ----
TOKENS = {
    "tok-doctor": User(id="u1", role="doctor"),
    "tok-nurse": User(id="u2", role="nurse"),
    "tok-other-doctor": User(id="u3", role="doctor"),
    "tok-billing": User(id="u4", role="billing"),
    "tok-patient": User(id="u5", role="patient", patient_id="p100"),
}
CARE_TEAM = {"p100": {"u1", "u2"}}
RECORDS = {
    "p100": {
        "patient_id": "p100", "name": "Jane Doe", "dob": "1980-02-01",
        "diagnoses": ["E11.9"], "clinical_notes": "Recheck A1C in 3 months.",
        "insurance_id": "INS-555", "balance_due": 120.00,
    }
}
AUDIT_LOG: list[dict] = []

def get_current_user(authorization: Optional[str] = Header(default=None)) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    token = authorization.split(" ")[1]
    user = TOKENS.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user

def audit_log(user: User, action: str, patient_id: Optional[str] = None):
    AUDIT_LOG.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user.id,
        "role": user.role,
        "action": action,
        "patient_id": patient_id,
    })

def can_view_patient_record(user: User, patient_id: str) -> bool:
    if user.role in {"doctor", "nurse"}:
        return user.id in CARE_TEAM.get(patient_id, set())
    elif user.role == "patient":
        return user.patient_id == patient_id
    return False

def can_update_clinical_notes(user: User, patient_id: str) -> bool:
    if user.role in {"doctor", "nurse"}:
        return user.id in CARE_TEAM.get(patient_id, set())
    return False

def can_view_billing(user: User, patient_id: str) -> bool:
    if user.role == "billing":
        return True
    elif user.role == "patient":
        return user.patient_id == patient_id
    return False

# ---- Pydantic models for requests ----
class ClinicalNotesUpdate(BaseModel):
    clinical_notes: str

class BillingUpdate(BaseModel):
    balance_due: float

# ---- Endpoints ----
@app.get("/records/{patient_id}")
def get_record(patient_id: str, user: User = Depends(get_current_user)):
    if not can_view_patient_record(user, patient_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this record")
    
    record = RECORDS.get(patient_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    audit_log(user, "view_record", patient_id)
    
    # Patients and clinical staff see clinical data; billing sees financial data
    if user.role == "billing":
        return {
            "patient_id": record["patient_id"],
            "name": record["name"],
            "insurance_id": record["insurance_id"],
            "balance_due": record["balance_due"]
        }
    elif user.role == "patient":
        return {
            "patient_id": record["patient_id"],
            "name": record["name"],
            "dob": record["dob"],
            "diagnoses": record["diagnoses"],
            "clinical_notes": record["clinical_notes"]
        }
    else:  # doctor, nurse
        return record

@app.patch("/records/{patient_id}/clinical-notes")
def update_clinical_notes(patient_id: str, update: ClinicalNotesUpdate, user: User = Depends(get_current_user)):
    if not can_update_clinical_notes(user, patient_id):
        raise HTTPException(status_code=403, detail="Not authorized to update clinical notes")
    
    record = RECORDS.get(patient_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    record["clinical_notes"] = update.clinical_notes
    audit_log(user, "update_clinical_notes", patient_id)
    
    return {"message": "Clinical notes updated", "clinical_notes": record["clinical_notes"]}

@app.get("/records/{patient_id}/billing")
def get_billing(patient_id: str, user: User = Depends(get_current_user)):
    if not can_view_billing(user, patient_id):
        raise HTTPException(status_code=403, detail="Not authorized to view billing")
    
    record = RECORDS.get(patient_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    audit_log(user, "view_billing", patient_id)
    
    return {
        "patient_id": record["patient_id"],
        "name": record["name"],
        "insurance_id": record["insurance_id"],
        "balance_due": record["balance_due"]
    }

@app.patch("/records/{patient_id}/billing")
def update_billing(patient_id: str, update: BillingUpdate, user: User = Depends(get_current_user)):
    if user.role != "billing":
        raise HTTPException(status_code=403, detail="Only billing role can update billing")
    
    record = RECORDS.get(patient_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    record["balance_due"] = update.balance_due
    audit_log(user, "update_billing", patient_id)
    
    return {"message": "Billing updated", "balance_due": record["balance_due"]}

@app.get("/audit-log")
def get_audit_log(user: User = Depends(get_current_user)):
    if user.role not in {"doctor", "nurse", "billing"}:
        raise HTTPException(status_code=403, detail="Not authorized to view audit log")
    
    audit_log(user, "view_audit_log")
    return AUDIT_LOG
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)