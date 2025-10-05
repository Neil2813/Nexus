# NEXUS: NASA Space Biology Knowledge Engine - Frontend

**Mission Control Interface for NASA Space Biology Data Exploration**

A production-ready React 18 + TypeScript frontend with space-themed UI for exploring NASA's Open Science Data Repository (OSDR) through AI-powered analysis and interactive visualizations.

## 🚀 Features

- **Space-Themed Mission Control UI**: Dark mode interface with astronaut-inspired design
- **Real-time NASA Data**: Direct integration with NASA OSDR API through backend
- **AI-Powered Search**: Semantic search with natural language processing
- **Interactive Knowledge Graph**: 3D visualization of biological relationships
- **Publication Analyzer**: AI-powered research paper summarization
- **System Health Monitoring**: Real-time backend service status
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **No Mock Data**: All data comes from real NASA APIs

## 🛠️ Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** + **shadcn/ui** components
- **React Query** for server state management
- **React Router** for navigation
- **Cytoscape.js** for knowledge graph visualization
- **Framer Motion** for animations
- **Zustand** for client state management

## 📋 Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend server running on `http://localhost:8000`

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
# or
yarn install
# or
pnpm install
```

### 2. Environment Setup
The `.env` file is already configured with working defaults:
```env
VITE_API_BASE=http://localhost:8000/api
VITE_APP_NAME=NEXUS: NASA Space Biology Knowledge Engine
```

### 3. Start Development Server
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

The app will be available at http://localhost:3000

### 4. Start Backend
Make sure the backend is running:
```bash
cd ../backend
uvicorn app.main:app --reload
```

## 🖥️ Application Structure

### Pages
- **Dashboard (`/`)**: Mission Control overview with real NASA data
- **Laboratory (`/laboratory`)**: Interactive knowledge graph visualization
- **Neural Search (`/search`)**: AI-powered semantic search of NASA studies
- **Publication Analyzer (`/publication`)**: AI text analysis and summarization
- **Training Center (`/training`)**: System monitoring and health checks
- **Dataset Detail (`/dataset/:id`)**: Detailed view of individual studies

### Key Components
- **Navbar**: Mission control navigation with space theme
- **MissionCard**: Study/dataset display cards
- **GraphViewport**: Interactive knowledge graph using Cytoscape
- **Loader**: Space-themed loading animations
- **UI Components**: shadcn/ui components with space theme customization

### Services
- **nasaApi**: Centralized API client for backend communication
- **useNasaData**: React Query hooks for data fetching

## 🎨 Design System

### Color Palette
- **Space**: Deep space background (`#0f0f1e`)
- **Astronaut White**: Primary text (`#fafbfc`)
- **Neural**: Cyan accent (`#00d1d1`)
- **Mission**: Blue accent (`#1e40af`)
- **ML Purple**: AI/ML features (`#7c3aed`)
- **Solar**: Warning/accent (`#facc15`)

### Typography
- **Headers**: Orbitron (space-themed)
- **Body**: Roboto (readable)
- **Tech**: Exo 2 (technical elements)
- **Code**: Roboto Mono (monospace)

### Animations
- **Neural Pulse**: AI processing indicators
- **Orbital Float**: Floating elements
- **Star Field**: Animated background stars
- **Launch Transition**: Page transitions

## 📡 API Integration

### Backend Endpoints Used
- `GET /api/datasets` - NASA space biology datasets
- `POST /api/search` - AI-powered study search
- `GET /api/graph` - Knowledge graph data
- `GET /api/organisms` - Available organisms
- `GET /api/missions` - Space missions
- `POST /api/summarize` - AI text summarization
- `POST /api/insights` - AI-generated insights
- `GET /api/health` - System health status

### Error Handling
- Graceful fallbacks for API failures
- Loading states with space-themed animations
- User-friendly error messages
- Offline detection and messaging

## 🔧 Development

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run type-check   # TypeScript type checking
npm run lint         # ESLint code linting
npm run format       # Prettier code formatting
```

### Code Style
- TypeScript for type safety
- ESLint + Prettier for code formatting
- Functional components with hooks
- Custom hooks for data fetching
- Tailwind CSS for styling

## 🧪 Features Walkthrough

### 1. Dashboard
- Real-time NASA dataset count
- AI insights display
- Quick launch pods to other sections
- System status indicators

### 2. Knowledge Graph Laboratory
- Interactive 3D graph visualization
- Node filtering by type (study, organism, mission)
- Real-time data from NASA knowledge graph
- Clickable nodes for detailed information

### 3. Neural Search
- Natural language search interface
- AI-powered intent parsing
- Filter by organisms and missions
- Real-time search suggestions
- Detailed result cards

### 4. Publication Analyzer
- Paste any research text for AI analysis
- Multiple AI provider support (Gemini, OpenAI)
- Graceful fallback to local processing
- Formatted summary display

### 5. Training Center
- System health monitoring
- AI insights management
- Real-time status indicators
- Backend service diagnostics

## 🚀 Production Build

```bash
npm run build
npm run preview
```

Optimized build includes:
- Code splitting
- Tree shaking
- Asset optimization
- TypeScript type checking
- CSS purging

## 🌟 Performance Features

- **React Query**: Intelligent caching and background refetching
- **Code Splitting**: Lazy loading for optimal performance
- **Image Optimization**: Optimized assets and icons
- **Bundle Analysis**: Webpack bundle analyzer integration
- **Service Worker Ready**: PWA capabilities

## 🔍 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure backend is running on port 8000
   - Check network connectivity
   - Verify CORS settings in backend

2. **Knowledge Graph Not Loading**
   - Check backend graph endpoint
   - Ensure Cytoscape dependencies installed
   - Check browser console for errors

3. **Build Errors**
   ```bash
   npm run type-check  # Check TypeScript errors
   npm run lint        # Check linting errors
   ```

4. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check component className usage
   - Verify color definitions in config

### Environment Variables
If the backend URL changes, update `.env`:
```env
VITE_API_BASE=http://your-backend-url/api
```

## 🤝 Contributing

1. Follow the existing code style
2. Add TypeScript types for new components
3. Test with the real backend API
4. Ensure responsive design
5. Maintain the space theme consistency

## 📚 Additional Resources

- [React Query Documentation](https://tanstack.com/query/latest)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [Cytoscape.js Documentation](https://js.cytoscape.org/)
- [NASA OSDR API Documentation](https://osdr.nasa.gov/bio/repo/)

---

**Mission Status: Ready for Launch! 🚀**

This frontend provides a complete space-themed interface for exploring NASA's space biology data with AI-powered insights and interactive visualizations.