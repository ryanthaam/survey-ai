import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Dict, List, Optional
import json

load_dotenv()

class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.client: Client = create_client(url, key)
    
    def save_analysis(self, user_id: str, analysis_data: Dict, filename: str) -> str:
        """Save analysis results to Supabase."""
        try:
            data = {
                "user_id": user_id,
                "filename": filename,
                "clusters": json.dumps(analysis_data.get("clusters", {})),
                "summaries": json.dumps(analysis_data.get("summaries", {})),
                "sentiments": json.dumps(analysis_data.get("sentiments", {})),
                "total_responses": analysis_data.get("total_responses", 0),
                "created_at": "now()"
            }
            
            result = self.client.table("analyses").insert(data).execute()
            return result.data[0]["id"]
        except Exception as e:
            raise Exception(f"Failed to save analysis: {str(e)}")
    
    def get_user_analyses(self, user_id: str) -> List[Dict]:
        """Get all analyses for a user."""
        try:
            result = self.client.table("analyses").select("*").eq("user_id", user_id).execute()
            return result.data
        except Exception as e:
            raise Exception(f"Failed to fetch analyses: {str(e)}")
    
    def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        """Get a specific analysis by ID."""
        try:
            result = self.client.table("analyses").select("*").eq("id", analysis_id).execute()
            if result.data:
                analysis = result.data[0]
                # Parse JSON fields
                analysis["clusters"] = json.loads(analysis["clusters"])
                analysis["summaries"] = json.loads(analysis["summaries"])
                analysis["sentiments"] = json.loads(analysis["sentiments"])
                return analysis
            return None
        except Exception as e:
            raise Exception(f"Failed to fetch analysis: {str(e)}")
    
    def delete_analysis(self, analysis_id: str, user_id: str) -> bool:
        """Delete an analysis (only if user owns it)."""
        try:
            result = self.client.table("analyses").delete().eq("id", analysis_id).eq("user_id", user_id).execute()
            return len(result.data) > 0
        except Exception as e:
            raise Exception(f"Failed to delete analysis: {str(e)}")
    
    def authenticate_user(self, email: str, password: str) -> Dict:
        """Authenticate user with Supabase Auth."""
        try:
            result = self.client.auth.sign_in_with_password({"email": email, "password": password})
            return {"success": True, "user": result.user, "session": result.session}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def register_user(self, email: str, password: str) -> Dict:
        """Register new user with Supabase Auth."""
        try:
            result = self.client.auth.sign_up({"email": email, "password": password})
            return {"success": True, "user": result.user, "session": result.session}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sign_out(self) -> Dict:
        """Sign out current user."""
        try:
            self.client.auth.sign_out()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}