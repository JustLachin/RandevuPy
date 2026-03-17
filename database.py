"""
Randevu Sistemi - Database Module (Supabase Sync)
Cloud PostgreSQL with polling-based updates (PyQt6 compatible)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum

from supabase import create_client, Client
from config import AppConfig


class AppointmentStatus(Enum):
    PENDING = "Beklemede"
    ACCEPTED = "Kabul Edildi"
    REJECTED = "Reddedildi"


@dataclass
class Appointment:
    id: int
    queue_number: int
    note: str
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_supabase(cls, data: dict) -> "Appointment":
        """Create Appointment from Supabase row data"""
        created_at = data["created_at"]
        updated_at = data["updated_at"]
        
        # Handle ISO format with or without Z
        if isinstance(created_at, str):
            created_at = created_at.replace("Z", "+00:00")
        if isinstance(updated_at, str):
            updated_at = updated_at.replace("Z", "+00:00")
            
        return cls(
            id=data["id"],
            queue_number=data["queue_number"],
            note=data.get("note", ""),
            status=AppointmentStatus(data["status"]),
            created_at=datetime.fromisoformat(created_at),
            updated_at=datetime.fromisoformat(updated_at)
        )


class DatabaseManager:
    """Sync Supabase database manager (PyQt6 compatible)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        try:
            self.client: Client = create_client(AppConfig.SUPABASE_URL, AppConfig.SUPABASE_KEY)
        except Exception as e:
            print(f"Supabase connection error: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.client is not None
    
    def get_next_queue_number(self) -> int:
        """Get next available queue number for today"""
        if not self.client:
            return 1
           
        today = datetime.now().strftime("%Y-%m-%d")
        
        result = self.client.table("appointments") \
            .select("queue_number") \
            .gte("created_at", f"{today}T00:00:00") \
            .order("queue_number", desc=True) \
            .limit(1) \
            .execute()
        
        if result.data:
            return result.data[0]["queue_number"] + 1
        return 1
    
    def create_appointment(self, note: str = "") -> Optional[Appointment]:
        """Create a new appointment and return it"""
        if not self.client:
            return None
            
        queue_number = self.get_next_queue_number()
        
        data = {
            "queue_number": queue_number,
            "note": note,
            "status": AppointmentStatus.PENDING.value
        }
        
        result = self.client.table("appointments").insert(data).execute()
        
        if result.data:
            return Appointment.from_supabase(result.data[0])
        return None
    
    def get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """Get appointment by ID"""
        if not self.client:
            return None
            
        result = self.client.table("appointments") \
            .select("*") \
            .eq("id", appointment_id) \
            .execute()
        
        if result.data:
            return Appointment.from_supabase(result.data[0])
        return None
    
    def get_all_appointments(self, status: Optional[AppointmentStatus] = None, descending: bool = True) -> List[Appointment]:
        """Get all appointments, optionally filtered by status and sorted"""
        if not self.client:
            return []
            
        query = self.client.table("appointments").select("*")
        
        if status:
            query = query.eq("status", status.value)
        
        result = query.order("created_at", desc=descending).execute()
        
        return [Appointment.from_supabase(row) for row in result.data]
    
    def get_pending_appointments(self) -> List[Appointment]:
        """Get pending appointments"""
        return self.get_all_appointments(AppointmentStatus.PENDING)
    
    def update_appointment_status(self, appointment_id: int, status: AppointmentStatus) -> bool:
        """Update appointment status"""
        if not self.client:
            return False
            
        result = self.client.table("appointments") \
            .update({"status": status.value}) \
            .eq("id", appointment_id) \
            .execute()
        
        return len(result.data) > 0
    
    def delete_appointment(self, appointment_id: int) -> bool:
        """Delete appointment by ID"""
        if not self.client:
            return False
            
        result = self.client.table("appointments") \
            .delete() \
            .eq("id", appointment_id) \
            .execute()
        
        return len(result.data) > 0
    
    def get_statistics(self) -> dict:
        """Get appointment statistics"""
        if not self.client:
            return {"total": 0, "pending": 0, "accepted": 0, "rejected": 0}
            
        result = self.client.table("appointments") \
            .select("status") \
            .execute()
        
        stats = {"total": 0, "pending": 0, "accepted": 0, "rejected": 0}
        
        for row in result.data:
            stats["total"] += 1
            status = row["status"]
            if status == AppointmentStatus.PENDING.value:
                stats["pending"] += 1
            elif status == AppointmentStatus.ACCEPTED.value:
                stats["accepted"] += 1
            elif status == AppointmentStatus.REJECTED.value:
                stats["rejected"] += 1
        
        return stats
    
    def get_today_appointments(self) -> List[Appointment]:
        """Get appointments for today"""
        if not self.client:
            return []
            
        today = datetime.now().strftime("%Y-%m-%d")
        
        result = self.client.table("appointments") \
            .select("*") \
            .gte("created_at", f"{today}T00:00:00") \
            .order("created_at", desc=True) \
            .execute()
        
        return [Appointment.from_supabase(row) for row in result.data]


# Global instance
def get_db() -> DatabaseManager:
    """Get the global database manager instance"""
    return DatabaseManager()
