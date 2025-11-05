#!/usr/bin/env python3
"""
Supabase Table Verification Script
Checks if all required tables exist using Python
"""

import os
import sys
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://wnpysodkioaqwculjkfu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InducHlzb2RraW9hcXdjdWxqa2Z1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyODAwNjgsImV4cCI6MjA3Nzg1NjA2OH0.NbbO3VgNf6MIPEzgIFmJI6Lk1EbmoorPt_LaY20Ob1Y"

# Required tables and their columns
REQUIRED_TABLES = {
    'users': ['user_id', 'username', 'total_xp', 'level', 'created_at'],
    'progress': ['user_id', 'topic', 'avg_score', 'quizzes_completed', 'last_completed_at'],
    'xp_logs': ['user_id', 'xp_amount', 'source', 'topic', 'created_at'],
    'quiz_results': ['user_id', 'topic', 'difficulty', 'score', 'total_questions', 'completed_at']
}

def verify_tables():
    """Verify all required tables exist and are accessible"""
    
    print("🔍 VERIFYING SUPABASE TABLES...\n")
    print("━" * 60)
    
    try:
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Connected to Supabase: {SUPABASE_URL}\n")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False
    
    all_tables_exist = True
    
    for table_name, required_columns in REQUIRED_TABLES.items():
        print(f"\n📊 Checking table: {table_name}")
        print("─" * 60)
        
        try:
            # Try to fetch one row to verify table exists
            response = supabase.table(table_name).select("*").limit(1).execute()
            
            print(f"✅ Table exists and is accessible")
            print(f"   Total rows: {len(response.data)}")
            
            if response.data:
                # Show actual columns
                actual_columns = list(response.data[0].keys())
                print(f"   Columns found: {', '.join(actual_columns)}")
                
                # Check for required columns
                missing_columns = [col for col in required_columns if col not in actual_columns]
                if missing_columns:
                    print(f"   ⚠️  Missing columns: {', '.join(missing_columns)}")
                else:
                    print(f"   ✅ All required columns present")
                
                # Show sample data
                print(f"   Sample row:")
                for key, value in response.data[0].items():
                    print(f"      {key}: {value}")
            else:
                print(f"   ℹ️  Table is empty (no sample data to show)")
                print(f"   Expected columns: {', '.join(required_columns)}")
                
        except Exception as e:
            print(f"❌ ERROR accessing {table_name}:")
            print(f"   {str(e)}")
            
            # Check for specific error types
            error_msg = str(e).lower()
            if 'does not exist' in error_msg or '42p01' in error_msg:
                print(f"   → Table does not exist!")
            elif 'permission denied' in error_msg or '42501' in error_msg:
                print(f"   → Permission denied (RLS policy issue)")
            
            all_tables_exist = False
    
    # Summary
    print("\n" + "━" * 60)
    print("\n📋 SUMMARY:")
    print("━" * 60)
    
    if all_tables_exist:
        print("✅ All required tables exist and are accessible!")
        print("\n📝 Next steps:")
        print("   1. Enable Realtime on tables (Database → Replication)")
        print("      Tables: users, progress, xp_logs, quiz_results")
        print("   2. Configure RLS policies if needed")
        print("   3. Restart your Next.js dev server")
    else:
        print("❌ Some tables are missing or inaccessible")
        print("\n🔧 To create missing tables:")
        print("   1. Go to Supabase SQL Editor")
        print("   2. Run the schema from backend/database/schema.sql")
        print("   3. Or use the provided SQL migration scripts")
    
    print("\n" + "━" * 60)
    return all_tables_exist

if __name__ == "__main__":
    try:
        success = verify_tables()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
