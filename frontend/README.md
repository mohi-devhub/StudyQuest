# StudyQuest Frontend - Monochrome Developer Dashboard

A terminal-inspired, monochrome developer dashboard built with Next.js 14, TypeScript, and Framer Motion.

## 🎨 Design Philosophy

- **Pure Black Background**: `#000000`
- **White Text**: `#FFFFFF`
- **Gray Accents**: `#CCCCCC`
- **Font**: JetBrains Mono (monospace)
- **Style**: Terminal/CLI aesthetic with smooth animations

## 🚀 Quick Start

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Backend Connection

Make sure your FastAPI backend is running on `http://localhost:8000` before starting the frontend.

```bash
# In a separate terminal, from the backend directory
cd ../backend
uvicorn main:app --reload
```

## 📁 Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Dashboard page
│   ├── quiz/
│   │   └── result/
│   │       └── page.tsx    # Quiz Result Page
│   └── globals.css         # Global styles & Tailwind
├── components/
│   ├── Header.tsx          # Dashboard header
│   ├── XPProgressBar.tsx   # XP progress visualization
│   ├── TopicCard.tsx       # Individual topic cards
│   ├── RecommendedCard.tsx # Featured recommendation
│   └── LoadingScreen.tsx   # Loading state
├── public/
│   └── sounds/
│       └── terminal-click.mp3  # Optional button click sound
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
└── next.config.js
```

## 🎯 Features

### Current Features

- **XP Progress Bar**: Animated horizontal progress bar showing level and XP
- **Topic Cards**: Display studied topics with scores and visual indicators
- **Recommended Topics**: AI-powered recommendations with priority levels
- **Stats Overview**: Total quizzes, average score, topics studied
- **AI Insights**: Motivational messages and learning advice
- **Quiz Result Page**: Terminal-style quiz summary with coach feedback
- **Loading States**: Smooth loading animations
- **Error Handling**: User-friendly error messages with retry
- **Sound Effects**: Optional terminal click sounds (configurable)

### Quiz Result Page Features

#### Terminal Output Style
- White banner header: `═══════════════ QUIZ SUMMARY ═══════════════`
- Indented CLI-style logs with tree symbols (├─, └─)
- ASCII divider lines using border elements
- Monochrome color scheme consistent with dashboard

#### Data Display
- **Quiz Metadata**: Topic, difficulty (with █░░░ visual), timestamp
- **Performance Metrics**: Score percentage, correct/total, accuracy bar
- **XP Reward**: XP gained with scale animation, next difficulty
- **Coach Feedback**: Motivation, insights, tips, next steps

#### Interactive Elements
- **RETRY_QUIZ()** button - Restart same topic/difficulty
- **NEXT_TOPIC()** button - Return to dashboard for new recommendations
- **Sound Toggle** - `[SOUND: ON/OFF]` for terminal click effects
- **Return Link** - `← RETURN_TO_DASHBOARD` underlined link

#### Animations (Framer Motion)
- Staggered fade-in for each section (0.1s delays)
- Horizontal scale animation for dividers
- Accuracy bar fill animation (1s duration)
- XP gain scale bounce effect
- Button hover/tap interactions

### Component Features

#### XP Progress Bar
- Shows current level and total XP
- Animated fill percentage
- XP remaining to next level

#### Topic Cards
- Average score display
- Last attempt timestamp
- Total attempts counter
- Visual score indicators (5-bar graph)
- Hover effects with underline

#### Recommended Card
- Priority badges (HIGH/MEDIUM/LOW)
- Category labels (weak_area/review/new)
- Current score and difficulty level
- Estimated XP gain
- Urgency message
- Interactive start quiz button

## 🛠️ Technology Stack

- **Framework**: Next.js 14.0.4
- **Language**: TypeScript 5.3.3
- **Styling**: Tailwind CSS 3.4.0
- **Animations**: Framer Motion 10.16.16
- **Font**: JetBrains Mono (Google Fonts)

## 🎨 Color Palette

```css
--terminal-black: #000000
--terminal-white: #FFFFFF
--terminal-gray: #CCCCCC
```

## ⚙️ Configuration

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Tailwind Custom Theme

The `tailwind.config.js` includes custom terminal colors:

```javascript
colors: {
  'terminal-black': '#000000',
  'terminal-white': '#FFFFFF',
  'terminal-gray': '#CCCCCC',
}
```

## 🔌 API Integration

The dashboard fetches data from these endpoints:

- `GET /progress/{user_id}` - User progress and topics
- `POST /study/recommendations` - AI-powered topic recommendations

### Mock Data

Currently using mock data for demonstration. To connect to real API:

1. Uncomment API calls in `app/page.tsx` (lines 66-75)
2. Implement authentication to get a real token
3. Replace `'your_token_here'` with actual auth token

## 🎭 Animations

All animations use Framer Motion with these patterns:

- **Fade In**: `opacity: 0 → 1`
- **Slide Up**: `y: 20 → 0`
- **Scale**: `scale: 0.95 → 1`
- **Stagger**: Delayed animations for lists

### Performance

- Initial animations on page load
- Smooth transitions (300ms - 1s)
- Hardware-accelerated transforms
- Optimized re-renders with React hooks

## 📱 Responsive Design

The dashboard is fully responsive:

- **Mobile**: Single column layout
- **Tablet**: 2-column grid for topics
- **Desktop**: 4-column stats grid, 2-column topics

Breakpoints follow Tailwind defaults:
- `md`: 768px
- `lg`: 1024px

## 🎨 Custom Styling

### Scrollbar

```css
/* Custom monochrome scrollbar */
::-webkit-scrollbar {
  width: 8px;
  background: black;
  border-left: 1px solid white;
}
```

### Selection

```css
/* Inverted selection colors */
::selection {
  background: white;
  color: black;
}
```

### Focus States

```css
/* White outline on focus */
*:focus {
  outline: 1px solid white;
  outline-offset: 2px;
}
```

## 🚧 Future Enhancements

- [ ] Authentication flow
- [ ] Quiz page with adaptive difficulty
- [ ] Progress tracking updates
- [ ] Topic filtering and search
- [ ] Dark/light mode toggle (keeping monochrome)
- [ ] Settings page
- [ ] User profile
- [ ] Achievement badges
- [ ] Leaderboard

## 📝 Development Notes

### Expected Lint Errors

Before `npm install`, you'll see TypeScript and CSS lint errors. These are normal:

- `Cannot find module 'react'` - Resolved after installing dependencies
- `Cannot find module 'next'` - Resolved after installing dependencies
- `Unknown at rule @tailwind` - Resolved after installing PostCSS

### Building for Production

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
npm run dev -- -p 3001
```

### Module Not Found Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Tailwind Styles Not Working

1. Check PostCSS config exists
2. Restart dev server
3. Clear Next.js cache: `rm -rf .next`

## 📄 License

Part of the StudyQuest project.

## 🤝 Contributing

This is a learning project. Feel free to fork and experiment!

---

**Built with ⚡ by developers, for developers**
