alerts = []

def trigger_alert(case_id, location):
    alerts.append({
        "case_id": case_id,
        "location": location,
        "status": "ACTIVE MLAT ALERT"
    })
