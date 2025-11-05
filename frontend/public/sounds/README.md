# Quiz Result Page - Sound Files

## Terminal Click Sound

To add the optional terminal click sound effect:

1. **Option 1: Use a free sound library**
   - Download from [Freesound.org](https://freesound.org/search/?q=keyboard+click)
   - Search for "terminal click" or "keyboard click"
   - Place the `.mp3` file in `/public/sounds/terminal-click.mp3`

2. **Option 2: Generate programmatically**
   ```javascript
   // Alternative: Use Web Audio API to generate click sound
   const audioContext = new AudioContext()
   const oscillator = audioContext.createOscillator()
   const gainNode = audioContext.createGain()
   
   oscillator.connect(gainNode)
   gainNode.connect(audioContext.destination)
   
   oscillator.frequency.value = 800
   gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
   gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1)
   
   oscillator.start(audioContext.currentTime)
   oscillator.stop(audioContext.currentTime + 0.1)
   ```

3. **Option 3: Use existing assets**
   - Copy any short click sound (< 100ms duration)
   - Convert to MP3 format
   - Ensure volume is normalized

## Sound Toggle

The quiz result page includes a sound toggle feature:
- Default: OFF (to avoid unexpected sounds)
- Users can enable via `[SOUND: ON/OFF]` button
- Plays on button clicks: RETRY_QUIZ() and NEXT_TOPIC()

## File Location

Place sound file at:
```
/Users/mohith/Projects/StudyQuest/frontend/public/sounds/terminal-click.mp3
```

Create directory if needed:
```bash
mkdir -p /Users/mohith/Projects/StudyQuest/frontend/public/sounds
```

## Sound Specs

- Format: MP3
- Duration: 50-100ms
- Volume: Normalized to -6dB
- Sample rate: 44.1kHz or 48kHz
- Bit rate: 128kbps minimum

## Fallback

If sound file doesn't exist, the app will:
- Silently fail (no error shown)
- Continue functioning normally
- Sound toggle still works (for future use)

This is handled in the `playClickSound()` function with `.catch()`.
