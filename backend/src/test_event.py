
from core.database import SessionLocal
from core.models import User, Event
from core.tenant_models import Tenant
from datetime import datetime

db = SessionLocal()
try:
    u = db.query(User).first()
    if u:
        e = Event(user_id=u.user_id, tenant_id=u.tenant_id, event_type='test', timestamp=datetime.now())
        db.add(e)
        db.commit()
        print("1 event added")
    else:
        print("No user found")
finally:
    db.close()
