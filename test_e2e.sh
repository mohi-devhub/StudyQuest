#!/bin/bash
# Quick E2E Testing Script for StudyQuest
# Run this to perform rapid validation of key features

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         StudyQuest - End-to-End Testing Script               ║"
echo "║         Minimalist UI Flow Validation                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for terminal output (ironic for a B/W app!)
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_URL="http://localhost:3001"
BACKEND_URL="http://localhost:8000"

# Check if environment variables are set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo -e "${RED}❌ ERROR: SUPABASE_URL and SUPABASE_KEY environment variables must be set${NC}"
    echo ""
    echo "Usage:"
    echo "  export SUPABASE_URL='your-supabase-url'"
    echo "  export SUPABASE_KEY='your-anon-key'"
    echo "  ./test_e2e.sh"
    exit 1
fi

echo "📋 Test 1: Service Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check frontend
echo -n "  Checking Frontend (Next.js)... "
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL)
if [ "$FRONTEND_STATUS" -eq 200 ]; then
  echo -e "${GREEN}✅ ONLINE${NC} (HTTP $FRONTEND_STATUS)"
else
  echo -e "${RED}❌ OFFLINE${NC} (HTTP $FRONTEND_STATUS)"
  echo -e "${YELLOW}  → Run: cd frontend && npm run dev${NC}"
fi

# Check backend
echo -n "  Checking Backend (FastAPI)... "
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/health 2>/dev/null || echo "000")
if [ "$BACKEND_STATUS" -eq 200 ]; then
  echo -e "${GREEN}✅ ONLINE${NC} (HTTP $BACKEND_STATUS)"
else
  echo -e "${YELLOW}⚠️  OFFLINE${NC} (HTTP $BACKEND_STATUS)"
  echo -e "${YELLOW}  → Run: cd backend && uvicorn main:app --reload${NC}"
fi

# Check Supabase
echo -n "  Checking Supabase Database... "
SUPABASE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  "$SUPABASE_URL/rest/v1/users?select=user_id&limit=1" \
  -H "apikey: $SUPABASE_KEY")
if [ "$SUPABASE_STATUS" -eq 200 ]; then
  echo -e "${GREEN}✅ CONNECTED${NC} (HTTP $SUPABASE_STATUS)"
else
  echo -e "${RED}❌ FAILED${NC} (HTTP $SUPABASE_STATUS)"
fi

echo ""
echo "📋 Test 2: Database Connectivity"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Fetch demo user
echo -n "  Fetching demo_user data... "
DEMO_USER=$(curl -s "$SUPABASE_URL/rest/v1/users?select=username,total_xp,level&user_id=eq.demo_user" \
  -H "apikey: $SUPABASE_KEY")

if echo "$DEMO_USER" | grep -q "demo_user"; then
  USERNAME=$(echo "$DEMO_USER" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
  TOTAL_XP=$(echo "$DEMO_USER" | grep -o '"total_xp":[0-9]*' | cut -d':' -f2)
  LEVEL=$(echo "$DEMO_USER" | grep -o '"level":[0-9]*' | cut -d':' -f2)
  echo -e "${GREEN}✅ SUCCESS${NC}"
  echo "     Username: $USERNAME"
  echo "     Total XP: $TOTAL_XP"
  echo "     Level:    $LEVEL"
else
  echo -e "${RED}❌ FAILED${NC}"
  echo "     Response: $DEMO_USER"
fi

# Check leaderboard data
echo -n "  Checking leaderboard (top 3)... "
LEADERBOARD=$(curl -s "$SUPABASE_URL/rest/v1/users?select=username,total_xp&order=total_xp.desc&limit=3" \
  -H "apikey: $SUPABASE_KEY")

if echo "$LEADERBOARD" | grep -q "total_xp"; then
  echo -e "${GREEN}✅ SUCCESS${NC}"
  echo "$LEADERBOARD" | grep -o '"username":"[^"]*","total_xp":[0-9]*' | \
    sed 's/"username":"\([^"]*\)","total_xp":\([0-9]*\)/     #\1 - \2 XP/' | \
    head -3
else
  echo -e "${RED}❌ FAILED${NC}"
fi

echo ""
echo "📋 Test 3: Real-time Capabilities Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${YELLOW}  ⚡ This test requires manual verification${NC}"
echo ""
echo "  1. Open your browser to: $FRONTEND_URL"
echo "  2. Open browser DevTools (F12) → Console tab"
echo "  3. Run the following SQL in Supabase SQL Editor:"
echo ""
echo "     ${GREEN}-- Test XP Gain (triggers toast)${NC}"
echo "     INSERT INTO public.xp_logs (user_id, xp_amount, source, topic)"
echo "     VALUES ('demo_user', 100, 'quiz_complete', 'E2E Test');"
echo ""
echo "     ${GREEN}-- Update User (updates leaderboard)${NC}"
echo "     UPDATE public.users"
echo "     SET total_xp = total_xp + 100,"
echo "         level = FLOOR((total_xp + 100) / 500) + 1"
echo "     WHERE user_id = 'demo_user';"
echo ""
echo "  4. Expected Results:"
echo "     ✅ Toast notification appears: 'XP +100 earned!'"
echo "     ✅ XP bar animates smoothly"
echo "     ✅ Console logs: '🎉 New XP gained: 100'"
echo "     ✅ Leaderboard updates automatically (if on /leaderboard)"
echo ""
echo -n "  Press Enter after running the SQL test... "
read

echo ""
echo "📋 Test 4: Visual Design Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${YELLOW}  👁️  Manual inspection required${NC}"
echo ""
echo "  Open: $FRONTEND_URL"
echo ""
echo "  Checklist:"
echo "  ☐ Background is black (#000000)"
echo "  ☐ Text is white (#FFFFFF) or gray (#808080)"
echo "  ☐ NO color leaks (no reds, blues, greens)"
echo "  ☐ Font is JetBrains Mono (monospace)"
echo "  ☐ Borders are 1px or 2px white"
echo "  ☐ Terminal aesthetic maintained"
echo ""
echo -n "  Confirm visual design is correct (y/n): "
read VISUAL_CONFIRM

if [ "$VISUAL_CONFIRM" = "y" ] || [ "$VISUAL_CONFIRM" = "Y" ]; then
  echo -e "  ${GREEN}✅ Visual design validated${NC}"
else
  echo -e "  ${RED}❌ Visual design issues found${NC}"
fi

echo ""
echo "📋 Test 5: Performance Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${YELLOW}  ⏱️  Use browser DevTools for precise measurement${NC}"
echo ""
echo "  Required Metrics:"
echo "  • Toast animation: <200ms"
echo "  • XP bar fill: <200ms"
echo "  • Button hover: <100ms"
echo "  • Real-time latency: <1000ms"
echo ""
echo "  To measure:"
echo "  1. Open DevTools → Performance tab"
echo "  2. Click 'Record'"
echo "  3. Trigger animation (hover button, XP update)"
echo "  4. Stop recording"
echo "  5. Check flame graph for duration"
echo ""
echo -n "  Confirm all animations < 200ms (y/n): "
read PERF_CONFIRM

if [ "$PERF_CONFIRM" = "y" ] || [ "$PERF_CONFIRM" = "Y" ]; then
  echo -e "  ${GREEN}✅ Performance targets met${NC}"
else
  echo -e "  ${YELLOW}⚠️  Performance needs optimization${NC}"
fi

echo ""
echo "📋 Test 6: Mobile Responsiveness"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${YELLOW}  📱 Test in browser DevTools Device Mode${NC}"
echo ""
echo "  Test Viewports:"
echo "  • Mobile:  375px x 667px  (iPhone SE)"
echo "  • Tablet:  768px x 1024px (iPad)"
echo "  • Desktop: 1920px x 1080px (Full HD)"
echo ""
echo "  Checklist for each viewport:"
echo "  ☐ Content fits without horizontal scroll"
echo "  ☐ Text is readable"
echo "  ☐ Buttons are tappable (min 44px height)"
echo "  ☐ Layout doesn't break"
echo ""
echo -n "  Confirm responsive design works (y/n): "
read RESPONSIVE_CONFIRM

if [ "$RESPONSIVE_CONFIRM" = "y" ] || [ "$RESPONSIVE_CONFIRM" = "Y" ]; then
  echo -e "  ${GREEN}✅ Responsive design validated${NC}"
else
  echo -e "  ${RED}❌ Responsive issues found${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    TEST SUMMARY                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Summary
echo "  Service Health:"
echo "    Frontend:      $([[ "$FRONTEND_STATUS" -eq 200 ]] && echo -e "${GREEN}✅${NC}" || echo -e "${RED}❌${NC}") ($FRONTEND_STATUS)"
echo "    Backend:       $([[ "$BACKEND_STATUS" -eq 200 ]] && echo -e "${GREEN}✅${NC}" || echo -e "${YELLOW}⚠️${NC}") ($BACKEND_STATUS)"
echo "    Database:      $([[ "$SUPABASE_STATUS" -eq 200 ]] && echo -e "${GREEN}✅${NC}" || echo -e "${RED}❌${NC}") ($SUPABASE_STATUS)"
echo ""
echo "  Manual Tests:"
echo "    Real-time:     Requires SQL execution"
echo "    Visual Design: $([[ "$VISUAL_CONFIRM" == "y" ]] && echo -e "${GREEN}✅${NC}" || echo -e "${RED}❌${NC}")"
echo "    Performance:   $([[ "$PERF_CONFIRM" == "y" ]] && echo -e "${GREEN}✅${NC}" || echo -e "${YELLOW}⚠️${NC}")"
echo "    Responsive:    $([[ "$RESPONSIVE_CONFIRM" == "y" ]] && echo -e "${GREEN}✅${NC}" || echo -e "${RED}❌${NC}")"
echo ""
echo "  Missing Components:"
echo "    ❌ Quiz Page (/app/quiz/page.tsx) - Not implemented"
echo "    ❌ End-to-end quiz flow - Blocked by missing quiz page"
echo ""
echo "  Next Actions:"
echo "    1. Create quiz page UI with monospace question blocks"
echo "    2. Connect START_QUIZ() button to quiz flow"
echo "    3. Test complete workflow: Dashboard → Quiz → Result"
echo "    4. Run Lighthouse audit for performance score"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "For detailed testing guide, see: E2E_TESTING_GUIDE.md"
echo ""
