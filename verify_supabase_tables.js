#!/usr/bin/env node

/**
 * Supabase Table Verification Script
 * Checks if all required tables exist and shows their structure
 */

const { createClient } = require('@supabase/supabase-js')

const supabaseUrl = 'https://wnpysodkioaqwculjkfu.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InducHlzb2RraW9hcXdjdWxqa2Z1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyODAwNjgsImV4cCI6MjA3Nzg1NjA2OH0.NbbO3VgNf6MIPEzgIFmJI6Lk1EbmoorPt_LaY20Ob1Y'

const supabase = createClient(supabaseUrl, supabaseKey)

const REQUIRED_TABLES = {
  users: ['user_id', 'username', 'total_xp', 'level', 'created_at'],
  progress: ['user_id', 'topic', 'avg_score', 'quizzes_completed', 'last_completed_at'],
  xp_logs: ['user_id', 'xp_amount', 'source', 'topic', 'created_at'],
  quiz_results: ['user_id', 'topic', 'difficulty', 'score', 'total_questions', 'completed_at']
}

async function verifyTables() {
  console.log('🔍 VERIFYING SUPABASE TABLES...\n')
  console.log('━'.repeat(60))
  
  let allTablesExist = true
  
  for (const [tableName, requiredColumns] of Object.entries(REQUIRED_TABLES)) {
    console.log(`\n📊 Checking table: ${tableName}`)
    console.log('─'.repeat(60))
    
    try {
      // Try to fetch one row to verify table exists and is accessible
      const { data, error, count } = await supabase
        .from(tableName)
        .select('*', { count: 'exact', head: false })
        .limit(1)
      
      if (error) {
        console.log(`❌ ERROR accessing ${tableName}:`)
        console.log(`   ${error.message}`)
        console.log(`   Code: ${error.code}`)
        
        if (error.code === '42P01') {
          console.log(`   → Table does not exist!`)
        } else if (error.code === '42501') {
          console.log(`   → Permission denied (RLS policy issue)`)
        }
        
        allTablesExist = false
        continue
      }
      
      console.log(`✅ Table exists and is accessible`)
      console.log(`   Total rows: ${count ?? 0}`)
      
      // Check if we got data to inspect columns
      if (data && data.length > 0) {
        const actualColumns = Object.keys(data[0])
        console.log(`   Columns found: ${actualColumns.join(', ')}`)
        
        // Check for required columns
        const missingColumns = requiredColumns.filter(col => !actualColumns.includes(col))
        if (missingColumns.length > 0) {
          console.log(`   ⚠️  Missing columns: ${missingColumns.join(', ')}`)
        } else {
          console.log(`   ✅ All required columns present`)
        }
        
        // Show sample data
        console.log(`   Sample row:`)
        console.log(`   ${JSON.stringify(data[0], null, 2).split('\n').join('\n   ')}`)
      } else {
        console.log(`   ℹ️  Table is empty (no sample data to show)`)
        console.log(`   Expected columns: ${requiredColumns.join(', ')}`)
      }
      
    } catch (err) {
      console.log(`❌ Unexpected error checking ${tableName}:`)
      console.log(`   ${err.message}`)
      allTablesExist = false
    }
  }
  
  console.log('\n' + '━'.repeat(60))
  console.log('\n📋 SUMMARY:')
  console.log('━'.repeat(60))
  
  if (allTablesExist) {
    console.log('✅ All required tables exist and are accessible!')
    console.log('\n📝 Next steps:')
    console.log('   1. Enable Realtime on tables (Database → Replication)')
    console.log('   2. Check RLS policies if needed')
    console.log('   3. Restart your Next.js dev server')
  } else {
    console.log('❌ Some tables are missing or inaccessible')
    console.log('\n🔧 To create missing tables, run the SQL schema:')
    console.log('   → Check backend/database/schema.sql or')
    console.log('   → Run migrations in Supabase SQL Editor')
  }
  
  console.log('\n' + '━'.repeat(60))
}

// Run verification
verifyTables().catch(err => {
  console.error('Fatal error:', err)
  process.exit(1)
})
