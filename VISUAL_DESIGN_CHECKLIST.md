# Visual Design Checklist
## Black & White Only - Zero Color Leaks

---

## 🎨 Allowed Colors

```css
/* ONLY these colors are permitted */
#000000  /* Pure black - backgrounds */
#FFFFFF  /* Pure white - text, borders */
#808080  /* Medium gray - muted text */

/* Opacity variants allowed */
rgba(255, 255, 255, 0.03)  /* Hover backgrounds */
rgba(255, 255, 255, 0.1)   /* Subtle highlights */
rgba(255, 255, 255, 0.5)   /* Dimmed text */
rgba(0, 0, 0, 0.8)         /* Overlay backgrounds */
```

---

## ❌ Forbidden Colors

```css
/* NEVER use these */
#FF0000  /* Red */
#00FF00  /* Green */
#0000FF  /* Blue */
#FFFF00  /* Yellow */
#FF00FF  /* Magenta */
#00FFFF  /* Cyan */

/* No branded colors */
#1DA1F2  /* Twitter blue */
#25D366  /* WhatsApp green */
#FF5722  /* Material orange */

/* No gradients with colors */
linear-gradient(...)  /* Only B/W gradients allowed */
```

---

## 📝 Component Audit Checklist

### ✅ Dashboard (`/app/page.tsx`)
- [ ] Background: `#000000`
- [ ] Header text: `#FFFFFF`
- [ ] XP progress bar: White fill on black
- [ ] Topic cards: White border, white text
- [ ] Recommended card: White text, gray labels
- [ ] Toast notifications: White border, white text
- [ ] All hover states: `rgba(255,255,255,0.03)` background

### ✅ Leaderboard (`/app/leaderboard/page.tsx`)
- [ ] ASCII banner: `#FFFFFF`
- [ ] Table headers: `#FFFFFF`
- [ ] Table rows: White text, gray alternating
- [ ] "You" highlight: White border, no color
- [ ] Rank numbers: `#FFFFFF`
- [ ] Connection status: "🟢 LIVE" uses emoji (acceptable)

### ⚠️ Quiz Result (`/app/quiz/result/page.tsx`)
- [ ] Score display: White text
- [ ] XP gained: White text
- [ ] Performance feedback: Gray text
- [ ] Coach feedback: White/gray text
- [ ] "Next" button: White border, white text
- [ ] **Check for green success colors!**

### ❌ Quiz Page (NOT IMPLEMENTED)
- [ ] Questions: White monospace blocks
- [ ] Options: White radio buttons
- [ ] Selected state: White border only (no color fill)
- [ ] Submit button: White border, black background
- [ ] Progress: "Question X/5" in white

---

## 🔍 Inspection Methods

### Method 1: Browser DevTools (Recommended)

```javascript
// Run in browser console
// 1. Check computed styles
document.querySelectorAll('*').forEach(el => {
  const bg = window.getComputedStyle(el).backgroundColor;
  const color = window.getComputedStyle(el).color;
  const border = window.getComputedStyle(el).borderColor;
  
  // Alert on non-B/W colors
  if (bg && !bg.match(/rgba?\(0,\s*0,\s*0|rgba?\(255,\s*255,\s*255/)) {
    console.warn('Color leak (bg):', el, bg);
  }
  if (color && !color.match(/rgba?\(0,\s*0,\s*0|rgba?\(255,\s*255,\s*255|rgba?\(128,\s*128,\s*128/)) {
    console.warn('Color leak (text):', el, color);
  }
});

// 2. Check for gradients
document.querySelectorAll('*').forEach(el => {
  const bg = window.getComputedStyle(el).backgroundImage;
  if (bg && bg.includes('gradient') && !bg.match(/rgb\(0,\s*0,\s*0\)|rgb\(255,\s*255,\s*255\)/)) {
    console.warn('Gradient leak:', el, bg);
  }
});
```

### Method 2: Visual Inspection

1. **Desaturate Browser Window**
   - Chrome: DevTools → Rendering → Emulate vision deficiencies → Achromatopsia
   - This makes it easier to spot color leaks

2. **Screenshot Comparison**
   - Take screenshot
   - Open in image editor
   - Desaturate to grayscale
   - Any remaining color = leak

3. **Accessibility Check**
   - High contrast mode should not reveal hidden colors
   - All content should remain visible in B/W

---

## 🛠️ Common Color Leak Sources

### Tailwind CSS Classes to Avoid:

```css
/* ❌ NEVER use these */
.bg-blue-500
.text-red-600
.border-green-400
.hover:bg-indigo-700

/* ✅ Only use these */
.bg-black
.bg-white
.text-white
.text-gray-500
.border-white
.hover:bg-white/5
```

### Framer Motion Animations:

```jsx
// ❌ Wrong - colored animation
<motion.div
  animate={{ backgroundColor: '#FF0000' }}  // RED!
/>

// ✅ Correct - B/W animation
<motion.div
  animate={{ backgroundColor: 'rgba(255,255,255,0.1)' }}  // White
/>
```

### Emojis (Use with Caution):

```
✅ Allowed (monochrome or acceptable):
⚡ Lightning (no color)
🎯 Target (minimal color)
🔌 Plug (minimal color)
📊 Chart (minimal color)

❌ Avoid (colorful):
🔴 Red circle
🟢 Green circle
🎨 Palette
🌈 Rainbow
```

---

## 📐 Font Consistency

### Primary Font:

```css
font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
```

### Verification:

```javascript
// Run in console
document.querySelectorAll('*').forEach(el => {
  const font = window.getComputedStyle(el).fontFamily;
  if (font && !font.includes('JetBrains Mono') && !font.includes('monospace')) {
    console.warn('Non-monospace font:', el, font);
  }
});
```

### Acceptable Fallbacks:

1. `JetBrains Mono` (preferred)
2. `Fira Code` (acceptable)
3. `SF Mono` (macOS fallback)
4. `Consolas` (Windows fallback)
5. `Courier New` (universal fallback)
6. `monospace` (system fallback)

---

## 🎭 Hover & Active States

### Acceptable Patterns:

```css
/* ✅ Correct - subtle white overlay */
.hover\:bg-white\/5:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

/* ✅ Correct - border emphasis */
.hover\:border-2:hover {
  border-width: 2px;
  border-color: #FFFFFF;
}

/* ✅ Correct - invert */
.hover\:bg-white:hover {
  background-color: #FFFFFF;
  color: #000000;
}

/* ❌ Wrong - colored state */
.hover\:bg-blue-500:hover {
  background-color: #3B82F6;  /* BLUE! */
}
```

---

## 🧪 Automated Testing

### Color Leak Detector Script:

```bash
#!/bin/bash
# Save as: check_colors.sh

echo "Scanning CSS files for color violations..."

# Check for hex colors outside B/W palette
grep -rn --include="*.css" --include="*.tsx" --include="*.jsx" \
  -E '#[0-9A-Fa-f]{6}' . | \
  grep -v '#000000' | \
  grep -v '#FFFFFF' | \
  grep -v '#808080' | \
  grep -v '#fff' | \
  grep -v '#000'

echo "Scanning for RGB colors outside B/W..."
grep -rn --include="*.css" --include="*.tsx" --include="*.jsx" \
  -E 'rgb\([0-9]+,\s*[0-9]+,\s*[0-9]+\)' . | \
  grep -v 'rgb(0, 0, 0)' | \
  grep -v 'rgb(255, 255, 255)' | \
  grep -v 'rgb(128, 128, 128)'

echo "Checking Tailwind color classes..."
grep -rn --include="*.tsx" --include="*.jsx" \
  -E 'bg-(red|blue|green|yellow|purple|pink|indigo|teal|cyan|orange|lime|emerald|violet|fuchsia|rose|sky|amber)' .

echo "Done! Any results above are potential color leaks."
```

---

## ✅ Final Validation Steps

### Before Deployment:

1. **Run Color Detector Script**
   ```bash
   chmod +x check_colors.sh
   ./check_colors.sh
   ```

2. **Browser Console Check**
   - Open DevTools → Console
   - Paste color leak detection script (from Method 1)
   - Fix any warnings

3. **Visual Inspection**
   - Load all pages
   - Enable DevTools → Rendering → Achromatopsia
   - Verify no colors visible

4. **Screenshot Test**
   - Capture dashboard, leaderboard, quiz, result
   - Convert to grayscale in image editor
   - No color should remain

5. **Lighthouse Accessibility**
   - Run audit
   - Check contrast ratios (should be 21:1 for B/W)

---

## 📊 Test Results Template

```
Date: November 5, 2025
Tested by: [Name]

Color Leak Audit:
-----------------
✅ Dashboard: No leaks detected
✅ Leaderboard: No leaks detected  
✅ Quiz Result: No leaks detected
❌ Quiz Page: Not implemented

Font Consistency:
-----------------
✅ All headers: JetBrains Mono
✅ All body text: JetBrains Mono
✅ All buttons: JetBrains Mono
✅ No serif/sans-serif leaks

Hover States:
-------------
✅ Buttons: White overlay only
✅ Cards: White border emphasis
✅ Links: No color changes

Issues Found:
-------------
1. [None]

Signed off: __________ Date: __________
```

---

## 🚨 Common Violations & Fixes

### Issue 1: Colored Success/Error States

```tsx
// ❌ Wrong
<div className="bg-green-500">Success!</div>
<div className="text-red-600">Error!</div>

// ✅ Correct
<div className="border border-white">✓ Success</div>
<div className="border border-white">✗ Error</div>
```

### Issue 2: Chart Libraries

```javascript
// ❌ Wrong - colored charts
const chartColors = ['#FF0000', '#00FF00', '#0000FF'];

// ✅ Correct - B/W gradients
const chartColors = [
  'rgba(255, 255, 255, 1.0)',
  'rgba(255, 255, 255, 0.7)',
  'rgba(255, 255, 255, 0.4)',
  'rgba(255, 255, 255, 0.1)'
];
```

### Issue 3: External Libraries

```tsx
// ❌ Danger - libraries may inject colors
import { Button } from 'material-ui';  // Often colored

// ✅ Safe - custom components
import { Button } from '@/components/Button';  // You control styling
```

---

## 📚 Resources

- **Tailwind Config:** `frontend/tailwind.config.ts`
- **Global Styles:** `frontend/app/globals.css`
- **Color Variables:** Search for `terminal-` in codebase

---

*Last Updated: November 5, 2025*
*Status: ENFORCED - Zero tolerance for color leaks*
