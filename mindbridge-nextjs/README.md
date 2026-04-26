# 🧠 MindBridge AI — Next.js Frontend

> **Claude-inspired sanctuary for mental health conversations.**

## Quick Start

### Prerequisites
- Node.js 18+
- Backend running on http://localhost:8000 (see `../backend/`)

### Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

Open http://localhost:3000

## Architecture

```
app/
├── components/
│   ├── Layout/
│   │   ├── Sidebar.jsx         # Claude-style left sidebar
│   │   └── ModeToggle.jsx      # 💬/🧠 segmented control
│   ├── Chat/
│   │   └── WelcomeScreen.jsx   # Personalized welcome
│   ├── Session/
│   │   └── SessionCard.jsx     # Session list items
│   ├── EmpathyChat.jsx         # Direct chat mode
│   ├── HybridAssess.jsx        # ML+Hybrid interview
│   ├── ManualAssess.jsx        # 13-field form (modal)
│   ├── HistoryTab.jsx          # Session history
│   ├── AnalyticsTab.jsx        # Stats dashboard
│   └── ControlPanel.jsx        # Settings
├── lib/
│   └── api.js                  # Backend API client
├── page.jsx                    # Main app shell
├── layout.jsx                  # Root layout
└── globals.css                 # Design system
```

## Design System

**Claude-Inspired Aesthetic:**
- **Canvas**: Parchment `#f5f4ed` — warm, non-clinical
- **Accents**: Terracotta `#c96442` — earthy, warm
- **Typography**: Playfair Display (serif) + DM Sans (sans)
- **Philosophy**: "We stay. We understand. We celebrate your survival."

## Key Features

| Feature | Description |
|---------|-------------|
| 💬 Direct Chat | Pure conversation, no analysis |
| 🧠 ML+Hybrid | Structured assessment + DTC prediction |
| 🎭 Mode Toggle | Animated 💬/🧠 segmented control |
| 📋 Session Sidebar | Claude-style conversation history |
| 👤 Personalization | First-time / returning / post-crisis welcomes |
| 🌓 Theme | Dark/light mode with warm palette |

## API Integration

All backend communication via `lib/api.js`:

```javascript
// Example: Send chat message
const response = await sendInterviewMessage({
  message: "I feel like drowning yaar",
  history: [],
  userName: "Priya"
});
// Returns: { reply, empathy_map, crisis_detected, prediction }
```

## Environment

Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Build for Production

```bash
npm run build
```

## Stack

- Next.js 15
- React 19
- Tailwind CSS
- FastAPI backend
- MongoDB + Redis (optional)
- Ollama LLM

---

📖 See root `../README.md` for full documentation.
