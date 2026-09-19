"""
FuturSet Design Lab & Concept Lab Metadata
Defines comprehensive design intelligence, inspiration sources, animation specifications,
and visual tokens for all 28 Product Previews and 20 Standalone Concept Websites.
"""
from typing import List, Dict, Any

PREVIEWS_DATA: List[Dict[str, Any]] = [
    {
        "id": "01",
        "name": "Master Luminous",
        "badge": "Flagship / Recommended",
        "description": "Dark sophisticated interface, luminous violet/cyan borders, refined glass surfaces, crisp typography, and fluid micro-interactions.",
        "inspired_by": ["Linear (Hierarchy)", "Raycast (Shortcuts)", "Stripe (Depth)", "FuturSet (Original)"],
        "motion": "Staggered fade-up, glass specular sheen sweep, tactile pill compression, beacon pulse",
        "accent": "#635bff",
        "style_class": "theme-01-master",
        "animations": [
            {"name": "Staggered Entrance", "source": "Prismic CSS Guide", "usage": "Job Cards & Dossiers", "tech": "CSS keyframes fadeUp + var(--card-index)"},
            {"name": "Glass Specular Sweep", "source": "CodePen Glassmorphism", "usage": "Card Hover Sheen", "tech": "CSS ::after + linear-gradient + transform"},
            {"name": "Sonar Radar Ripple", "source": "Motion.dev", "usage": "Live Status Badges", "tech": "CSS keyframes sonar + opacity"},
            {"name": "Scroll Progress Bar", "source": "CSS scroll-driven animations", "usage": "Top Viewport Indicator", "tech": "animation-timeline: scroll() + JS fallback"}
        ]
    },
    {
        "id": "02",
        "name": "Linear Precision",
        "badge": "Minimal Dark Product",
        "description": "Ultra-dense, razor-sharp 1px border grid, monospace accents, instant keyboard navigation, and zero visual fluff.",
        "inspired_by": ["Linear.app (2026 Refresh)", "Raycast", "GitKraken"],
        "motion": "Instant 80ms transitions, snappy hover states, zero overshoot",
        "accent": "#5e6ad2",
        "style_class": "theme-02-linear",
        "animations": [
            {"name": "Subtle Border Illuminate", "source": "Linear.app", "usage": "Card & Row Borders", "tech": "transition: border-color 0.1s ease"},
            {"name": "Quick Monospace Shift", "source": "Linear", "usage": "Table Rows & Badges", "tech": "font-feature-settings: 'tnum'"}
        ]
    },
    {
        "id": "03",
        "name": "Stripe Dynamic",
        "badge": "Dynamic Mesh SaaS",
        "description": "Multi-angle gradient mesh aura (#635bff & #00d4ff), layered floating cards, rich luminous depth, and liquid hover buttons.",
        "inspired_by": ["Stripe.com/in", "Vercel", "Tailwind UI"],
        "motion": "Liquid fill button transitions, floating ambient mesh wave, smooth gradient shifts",
        "accent": "#00d4ff",
        "style_class": "theme-03-stripe",
        "animations": [
            {"name": "Liquid Button Fill", "source": "Prismic Button Catalog", "usage": "Primary CTA Buttons", "tech": "CSS ::before scale/translate on hover"},
            {"name": "Ambient Gradient Breathing", "source": "Stripe Radar", "usage": "Background Canvas", "tech": "CSS background-position cycle"}
        ]
    },
    {
        "id": "04",
        "name": "Raycast Command Center",
        "badge": "Keyboard-First Luxury",
        "description": "Dark obsidian glass, floating command HUD, prominent keyboard shortcut badges, and spotlight cursor tracking.",
        "inspired_by": ["Raycast.com", "macOS Sonoma", "Alfred"],
        "motion": "Spotlight radial cursor hover, quick command-palette reveal, tactile press",
        "accent": "#ff6363",
        "style_class": "theme-04-raycast",
        "animations": [
            {"name": "Radial Spotlight Hover", "source": "Raycast UI", "usage": "Interactive Cards", "tech": "radial-gradient(circle at var(--mouse-x), ...)"},
            {"name": "Command Key Pulse", "source": "Raycast Shortcuts", "usage": "Kbd Badges", "tech": "box-shadow keyframes"}
        ]
    },
    {
        "id": "05",
        "name": "Extreme Minimal",
        "badge": "Monochrome Clarity",
        "description": "Pure black and white foundation, high-contrast headline typography, maximum whitespace, and distraction-free data tables.",
        "inspired_by": ["Dieter Rams", "Braun Design", "The Verge Minimal"],
        "motion": "Subtle 120ms opacity fades, underline expansions, zero decorative shadows",
        "accent": "#ffffff",
        "style_class": "theme-05-minimal",
        "animations": [
            {"name": "Underline Sweep", "source": "Hover.css", "usage": "Navigation Links", "tech": "transform: scaleX(1)"},
            {"name": "Minimalist Fade", "source": "Vanilla CSS", "usage": "Modal & Filter Transitions", "tech": "opacity 0.15s ease"}
        ]
    },
    {
        "id": "06",
        "name": "Spatial Premium",
        "badge": "Multi-Layered Depth",
        "description": "Deep z-index layers, soft atmospheric shadows, subtle 2.5D card elevation on hover, and spatial floating docks.",
        "inspired_by": ["Apple visionOS", "Framer Spatial", "Craft.do"],
        "motion": "Soft floating ambient levitation, layered card parallax, diffuse drop shadows",
        "accent": "#38bdf8",
        "style_class": "theme-06-spatial",
        "animations": [
            {"name": "Floating Card Hover", "source": "CSS 3D Transforms", "usage": "Job Cards & Pipeline Stages", "tech": "transform: translateY(-6px) translateZ(10px)"},
            {"name": "Diffuse Ambient Glow", "source": "Spatial UI", "usage": "Card Shadows", "tech": "box-shadow: 0 20px 40px -15px rgba(0,0,0,0.7)"}
        ]
    },
    {
        "id": "07",
        "name": "Creative Framer",
        "badge": "Fluid Asymmetry",
        "description": "Asymmetrical layout balance, expressive typography pairings, fluid spring bezier curves, and organic card rhythms.",
        "inspired_by": ["Framer.com", "Halo Lab", "SiteInspire"],
        "motion": "Spring physics curves (cubic-bezier(0.34, 1.56, 0.64, 1)), dynamic elastic buttons",
        "accent": "#ec4899",
        "style_class": "theme-07-framer",
        "animations": [
            {"name": "Spring Elastic Hover", "source": "Motion.dev Spring", "usage": "Action Buttons & Chips", "tech": "cubic-bezier(0.34, 1.56, 0.64, 1)"},
            {"name": "Asymmetrical Reveal", "source": "Framer Motion", "usage": "Section Headers", "tech": "staggered translate & rotate"}
        ]
    },
    {
        "id": "08",
        "name": "Playful Premium",
        "badge": "Vibrant Personality",
        "description": "Rounded pill surfaces, cheerful neon accents (emerald, amber, cyan), friendly bouncy micro-interactions, and high usability.",
        "inspired_by": ["Duolingo Max", "Linear Mobile", "Loom"],
        "motion": "Bouncy pill hover, jelly-button press effect, cheerful celebration icons",
        "accent": "#10b981",
        "style_class": "theme-08-playful",
        "animations": [
            {"name": "Jelly Button Press", "source": "CodePen Playful", "usage": "Apply & Filter Buttons", "tech": "keyframes jellyBounce"},
            {"name": "Badge Pop", "source": "Prismic Micro-Interactions", "usage": "Urgency & Vacancy Badges", "tech": "transform: scale(1.08)"}
        ]
    },
    {
        "id": "09",
        "name": "AI Editorial",
        "badge": "Sophisticated Gazette",
        "description": "High-end serif headlines, refined warm-slate surfaces, dense editorial hierarchy, and intelligent content summaries.",
        "inspired_by": ["Substack", "Perplexity Pro", "The Atlantic"],
        "motion": "Smooth text opacity fades, subtle ink-like underline accents, elegant transitions",
        "accent": "#e2e8f0",
        "style_class": "theme-09-editorial",
        "animations": [
            {"name": "Editorial Text Reveal", "source": "CSS Typography", "usage": "Article Titles & Summaries", "tech": "keyframes textFadeIn"},
            {"name": "Ink Underline Expansion", "source": "Prismic Editorial", "usage": "Links & Citations", "tech": "transition: width 0.3s ease"}
        ]
    },
    {
        "id": "10",
        "name": "Awwwards Editorial",
        "badge": "Cinematic Visuals",
        "description": "Dramatic full-width compositions, cinematic letterspacing, high-contrast dark mood, and award-winning showcase styling.",
        "inspired_by": ["Awwwards Site of the Day", "The Variable", "Locomotive"],
        "motion": "Cinematic slide-ins, dramatic curtain reveals, smooth inertia scroll effects",
        "accent": "#f59e0b",
        "style_class": "theme-10-awwwards",
        "animations": [
            {"name": "Curtain Clip Reveal", "source": "Awwwards Trends", "usage": "Banner & Pipeline", "tech": "clip-path: inset(0 0 0 0)"},
            {"name": "Cinematic Letterspacing Shift", "source": "Awwwards Typography", "usage": "Headings", "tech": "transition: letter-spacing 0.4s"}
        ]
    },
    {
        "id": "11",
        "name": "Cyber AI",
        "badge": "Futuristic Telemetry",
        "description": "Cyberpunk terminal grid, luminous cyan and matrix green glowing borders, live telemetry pulses, and scanline overlays.",
        "inspired_by": ["Adaptive Security", "Cyberpunk 2077 HUD", "Vercel Geist"],
        "motion": "Pulsing neon borders, radar sweeps, rapid digital number tick",
        "accent": "#00ffcc",
        "style_class": "theme-11-cyber",
        "animations": [
            {"name": "Scanline Overlay", "source": "CodePen Cyber", "usage": "Background Texture", "tech": "repeating-linear-gradient scanline"},
            {"name": "Neon Border Pulse", "source": "Prismic Neon", "usage": "Scanner & Gazette Cards", "tech": "box-shadow: 0 0 15px cyan"}
        ]
    },
    {
        "id": "12",
        "name": "Glass System",
        "badge": "Pure Glassmorphism",
        "description": "Layered frosted glass cards, 24px backdrop blur, delicate specular border reflections, and icy crystalline aesthetics.",
        "inspired_by": ["macOS Big Sur", "Windows 11 Mica", "Dribbble Glass"],
        "motion": "Luminous specular shimmer sweep, smooth blur depth transitions",
        "accent": "#a5b4fc",
        "style_class": "theme-12-glass",
        "animations": [
            {"name": "Specular Edge Shimmer", "source": "Glassmorphism Guide", "usage": "All Panels & Modals", "tech": "backdrop-filter: blur(24px) + border reflection"},
            {"name": "Ice Sheen Hover", "source": "CodePen Glass", "usage": "Buttons & Chips", "tech": "linear-gradient(135deg, rgba(255,255,255,0.2), transparent)"}
        ]
    },
    {
        "id": "13",
        "name": "Aurora Fluid",
        "badge": "Atmospheric Glow",
        "description": "Breathing multi-stop northern-lights gradient aura (violet, teal, sapphire), organic rounded containers, and soft diffused glow.",
        "inspired_by": ["Stripe Climate", "Tailwind Aurora", "Framer Aurora"],
        "motion": "Slow-breathing gradient cycle (12s infinite loop), floating atmospheric orbs",
        "accent": "#818cf8",
        "style_class": "theme-13-aurora",
        "animations": [
            {"name": "Aurora Mesh Wave", "source": "CSS Mesh Gradients", "usage": "Full Canvas Background", "tech": "keyframes auroraBreathing 12s ease-in-out infinite"},
            {"name": "Soft Diffuse Hover", "source": "Prismic Ambient", "usage": "Job Cards & Badges", "tech": "filter: drop-shadow(0 0 12px rgba(99,91,255,0.4))"}
        ]
    },
    {
        "id": "14",
        "name": "Bento OS",
        "badge": "Modular Grid System",
        "description": "Apple-style modular bento grid, distinct widget cards, high card hierarchy, rounded 24px corners, and integrated OS pill badges.",
        "inspired_by": ["Apple Newsroom", "Bento.me", "Linear 2026"],
        "motion": "Card scale spring on hover, smooth widget reordering, snap alignment",
        "accent": "#3b82f6",
        "style_class": "theme-14-bento",
        "animations": [
            {"name": "Bento Tile Scale", "source": "Bento.me Design", "usage": "Dashboard Widgets & Tools", "tech": "transform: scale(1.02) + border-glow"},
            {"name": "Widget Pill Badge Pulse", "source": "Apple Bento", "usage": "Status Counters", "tech": "keyframes pulse"}
        ]
    },
    {
        "id": "15",
        "name": "Swiss Precision",
        "badge": "International Typographic",
        "description": "Strict 12-column grid lines, neutral high-contrast Helvetica/Inter typography, zero unnecessary decoration, and pure data legibility.",
        "inspired_by": ["Josef Müller-Brockmann", "Swiss Design Awards", "Monotype"],
        "motion": "Fast 90ms linear transitions, crisp state changes, absolute precision",
        "accent": "#e11d48",
        "style_class": "theme-15-swiss",
        "animations": [
            {"name": "Grid Line Highlight", "source": "Swiss Style", "usage": "Table Rows & Borders", "tech": "outline: 1px solid currentColor"},
            {"name": "Instant Type Invert", "source": "Swiss Poster", "usage": "Button Invert", "tech": "background: #fff; color: #000;"}
        ]
    },
    {
        "id": "16",
        "name": "Soft SaaS",
        "badge": "Friendly Light Mode",
        "description": "Clean light-mode interface, warm alabaster surfaces, soft pastel status chips, gentle diffuse shadows, and welcoming rounded corners.",
        "inspired_by": ["Notion", "Linear Light", "Intercom"],
        "motion": "Gentle 150ms ease-out transitions, soft shadow elevations",
        "accent": "#4f46e5",
        "style_class": "theme-16-softsaas",
        "animations": [
            {"name": "Soft Shadow Elevation", "source": "Tailwind Soft Shadows", "usage": "Job Cards on Hover", "tech": "box-shadow: 0 12px 24px -4px rgba(0,0,0,0.08)"},
            {"name": "Pastel Chip Fade", "source": "Notion UI", "usage": "Filter Chips", "tech": "transition: background 0.15s"}
        ]
    },
    {
        "id": "17",
        "name": "Developer Terminal",
        "badge": "CLI & Monospace",
        "description": "Authentic monospace code aesthetics (JetBrains Mono), CLI command prompts, green status LEDs, and dark slate terminal blocks.",
        "inspired_by": ["Warp Terminal", "GitHub CLI", "Raycast Developer"],
        "motion": "Blinking cursor, typewriter text header, scanline sweeps, instant command response",
        "accent": "#22c55e",
        "style_class": "theme-17-terminal",
        "animations": [
            {"name": "Blinking CLI Cursor", "source": "CodePen Terminal", "usage": "Search & Headers", "tech": "keyframes blink 1s infinite"},
            {"name": "LED Status Blip", "source": "Terminal UI", "usage": "Live Telemetry", "tech": "keyframes ledPulse 2s ease infinite"}
        ]
    },
    {
        "id": "18",
        "name": "Fintech Command Center",
        "badge": "Dense Market Data",
        "description": "High-density data tables, live telemetry tickers, green/red delta badges, multi-column financial layouts, and compact calculator widgets.",
        "inspired_by": ["Wealthsimple", "Bloomberg Terminal", "Robinhood Gold"],
        "motion": "Smooth numerical value transitions, ticker scroll, crisp tabular micro-interactions",
        "accent": "#14b8a6",
        "style_class": "theme-18-fintech",
        "animations": [
            {"name": "Data Ticker Scroll", "source": "Fintech UI", "usage": "Top Gazette Ticker", "tech": "keyframes marquee 25s linear infinite"},
            {"name": "Tabular Delta Highlight", "source": "Wealthsimple", "usage": "Vacancies & Salary", "tech": "transition: color 0.2s, background 0.2s"}
        ]
    },
    {
        "id": "19",
        "name": "3D Spatial",
        "badge": "GPU Transforms",
        "description": "Interactive 3D card tilt following cursor position, perspective transforms (perspective: 1000px), layered depth elevation, and metallic edge highlights.",
        "inspired_by": ["Atropos.js", "Stripe Press 3D", "Apple Keynote"],
        "motion": "Cursor-tracking 3D rotateX/rotateY, depth parallax for internal card badges",
        "accent": "#8b5cf6",
        "style_class": "theme-19-3dspatial",
        "animations": [
            {"name": "Cursor 3D Card Tilt", "source": "CodePen 3D Tilt", "usage": "Job Cards & Article Cards", "tech": "transform: perspective(1000px) rotateX(var(--rx)) rotateY(var(--ry))"},
            {"name": "Z-Axis Floating Chip", "source": "3D Spatial UI", "usage": "Card Badges", "tech": "transform: translateZ(20px)"}
        ]
    },
    {
        "id": "20",
        "name": "Liquid Morph",
        "badge": "Organic Fluidity",
        "description": "Smooth organic border-radius transitions, liquid button fills, fluid splash hover effects, and playful morphing containers.",
        "inspired_by": ["Liquid Death", "Codrops Organic", "Stripe Atlas"],
        "motion": "Morphing border-radius keyframes, liquid button sweeps",
        "accent": "#f43f5e",
        "style_class": "theme-20-liquid",
        "animations": [
            {"name": "Border-Radius Morph", "source": "Prismic Organic CSS", "usage": "Featured Badges & Icons", "tech": "keyframes morphBlob 8s ease-in-out infinite"},
            {"name": "Liquid Fill Button", "source": "Prismic Button Catalog", "usage": "Primary Actions", "tech": "liquid wave SVG or clip-path hover"}
        ]
    },
    {
        "id": "21",
        "name": "Kinetic Typography",
        "badge": "Dynamic Motion Type",
        "description": "Large kinetic headings, dynamic word stagger animations, variable font weight shifts on hover, and text-led visual hierarchy.",
        "inspired_by": ["Awwwards Type", "Nike Kinetic", "Pentagram"],
        "motion": "Staggered letter reveals, font-variation-settings weight transitions on hover (300 to 900)",
        "accent": "#e0e7ff",
        "style_class": "theme-21-kinetic",
        "animations": [
            {"name": "Variable Weight Shift", "source": "Variable Fonts API", "usage": "Hero Titles & Card Headers", "tech": "transition: font-weight 0.3s cubic-bezier(0.16, 1, 0.3, 1)"},
            {"name": "Kinetic Word Slide", "source": "Prismic Typography", "usage": "Banner Headlines", "tech": "keyframes wordSlideUp"}
        ]
    },
    {
        "id": "22",
        "name": "Holographic Future",
        "badge": "Iridescent Prism",
        "description": "Iridescent rainbow holographic gradient foil, shimmering metallic borders, subtle prismatic reflections, and futuristic glass surfaces.",
        "inspired_by": ["Pokemon Holographic", "Apple Pay Card", "Cyberpunk Foil"],
        "motion": "Prismatic angle shift on hover, iridescent foil shimmer across cards",
        "accent": "#d946ef",
        "style_class": "theme-22-holographic",
        "animations": [
            {"name": "Holographic Foil Shimmer", "source": "CodePen Hologram", "usage": "Card Backgrounds & Dossiers", "tech": "background: linear-gradient(115deg, transparent, rgba(255,255,255,0.4), transparent)"},
            {"name": "Prismatic Border Glow", "source": "CSS Iridescent", "usage": "Card Borders", "tech": "border-image: linear-gradient(...) 1"}
        ]
    },
    {
        "id": "23",
        "name": "Editorial Magazine",
        "badge": "Printed Press Elegance",
        "description": "Classic newsprint typography (Playfair Display / Merriweather), elegant column dividers, sophisticated drop caps, and thoughtful whitespace.",
        "inspired_by": ["The New York Times", "Kinfolk Magazine", "Wired"],
        "motion": "Subtle ink-spread reveals, elegant column divider animations, quiet transitions",
        "accent": "#f1f5f9",
        "style_class": "theme-23-magazine",
        "animations": [
            {"name": "Ink-Spread Reveal", "source": "Editorial Design", "usage": "Articles & Job Summaries", "tech": "keyframes inkSpread"},
            {"name": "Column Rule Fade", "source": "Magazine CSS", "usage": "Grid Dividers", "tech": "border-color transition"}
        ]
    },
    {
        "id": "24",
        "name": "Modern Brutalism",
        "badge": "Neo-Brutalist Bold",
        "description": "High-contrast thick 2.5px solid borders, hard 4px offset drop shadows (#000), bold vibrant accent blocks (canary yellow, electric cyan), and bold sans typography.",
        "inspired_by": ["Gumroad", "Figma Neo-Brutalism", "Brutalist Websites"],
        "motion": "Tactile button press with hard shadow collapse (translate(2px, 2px) box-shadow: 0 0), snappy zero-blur state changes",
        "accent": "#facc15",
        "style_class": "theme-24-brutalism",
        "animations": [
            {"name": "Hard Shadow Pop", "source": "Neo-Brutalism Standard", "usage": "Buttons, Cards & Modals", "tech": "box-shadow: 4px 4px 0 #000; active: translate(2px,2px)"},
            {"name": "Stark Border Flash", "source": "Brutalist CSS", "usage": "Interactive Chips", "tech": "border: 2.5px solid #000"}
        ]
    },
    {
        "id": "25",
        "name": "Light Premium",
        "badge": "Luxury Ivory Minimal",
        "description": "Ultra-clean luxury white/ivory interface, slate-900 typography, refined 0.5px subtle hairline borders, and micro-shadows of supreme elegance.",
        "inspired_by": ["Celine", "Aesop", "Apple Light Mode"],
        "motion": "Subtle 200ms ease-out elevations, quiet cursor transitions, serene calm aesthetics",
        "accent": "#0f172a",
        "style_class": "theme-25-lightprem",
        "animations": [
            {"name": "Micro-Shadow Elevation", "source": "Luxury UI", "usage": "Cards & Panels", "tech": "box-shadow: 0 4px 20px -2px rgba(0,0,0,0.05)"},
            {"name": "Hairline Border Soften", "source": "Minimalist CSS", "usage": "All Dividers", "tech": "border-color: rgba(0,0,0,0.06)"}
        ]
    },
    {
        "id": "26",
        "name": "OLED Cinematic",
        "badge": "True Black #000000",
        "description": "True #000000 pitch-black canvas designed for OLED displays, ultra-high contrast white/gold accents, and dramatic focused spotlighting.",
        "inspired_by": ["Apple Pro Display", "Sony Bravia OLED", "Tesla UI"],
        "motion": "Vivid spotlight illumination on cursor hover, dramatic light cone reveals",
        "accent": "#fbbf24",
        "style_class": "theme-26-oled",
        "animations": [
            {"name": "OLED Spotlight Follower", "source": "OLED UI Design", "usage": "Hero & Cards", "tech": "radial-gradient(600px at var(--x) var(--y), rgba(255,255,255,0.08), transparent)"},
            {"name": "Vivid Gold Beacon", "source": "Cinematic CSS", "usage": "Urgent Notifications", "tech": "box-shadow: 0 0 20px #f59e0b"}
        ]
    },
    {
        "id": "27",
        "name": "Motion Storytelling",
        "badge": "Immersive Narrative",
        "description": "Full-screen scroll choreography, sticky progress storytelling indicators, smooth section morphing, and interactive narrative flow.",
        "inspired_by": ["Apple AirPods Pro site", "Lusion.co", "Stripe Sessions"],
        "motion": "Scroll-driven section transitions, sticky storytelling breadcrumbs, animated pipeline milestones",
        "accent": "#06b6d4",
        "style_class": "theme-27-storytelling",
        "animations": [
            {"name": "Sticky Milestone Reveal", "source": "ScrollStorytelling", "usage": "Article Pipeline & Tools", "tech": "position: sticky + scroll progress animation"},
            {"name": "Section Morphing", "source": "Motion.page", "usage": "Page Scroll", "tech": "keyframes morphSection"}
        ]
    },
    {
        "id": "28",
        "name": "Accessibility Premium",
        "badge": "WCAG AAA Certified",
        "description": "High-contrast ratios exceeding 7:1, prominent 3px focus rings for keyboard navigation, clear dyslexic-friendly type options, and zero distracting motion.",
        "inspired_by": ["GOV.UK", "USWDS", "A11y Project"],
        "motion": "Respects prefers-reduced-motion: reduce by default; zero decorative looping; clear instant focus outlines",
        "accent": "#38bdf8",
        "style_class": "theme-28-a11y",
        "animations": [
            {"name": "High-Contrast Focus Ring", "source": "WCAG AAA Guidelines", "usage": "All Interactive Controls", "tech": "outline: 3px solid #38bdf8; outline-offset: 2px;"},
            {"name": "Instant Clear Feedback", "source": "A11y Standards", "usage": "Buttons & Form Inputs", "tech": "transition: none"}
        ]
    }
]

CONCEPTS_DATA: List[Dict[str, Any]] = [
    {
        "id": "01",
        "slug": "quantum-canvas",
        "title": "Quantum Constellation Canvas",
        "category": "Canvas / WebGL",
        "tagline": "Interactive particle physics recruitment constellation",
        "description": "Every government sector and recruitment is represented as an interactive gravitational node. Users drag, zoom, and inspect real jobs connected by salary and eligibility orbits.",
        "accent": "#00f0ff"
    },
    {
        "id": "02",
        "slug": "spatial-sphere",
        "title": "3D Geospatial Gujarat Sphere",
        "category": "3D / Spatial",
        "tagline": "3D orbiting sphere of 33 Gujarat districts & Central boards",
        "description": "Spin the 3D district globe to reveal localized OJAS and GPSC vacancies across Ahmedabad, Surat, Gandhinagar, Rajkot, and Vadodara.",
        "accent": "#635bff"
    },
    {
        "id": "03",
        "slug": "cyberpunk-cockpit",
        "title": "Cyberpunk Avionics HUD",
        "category": "Futuristic UI",
        "tagline": "Tactical cockpit with real-time gazette telemetry streams",
        "description": "Full-screen sci-fi avionics heads-up display featuring oscilloscope gazette audio visualizers, holographic target locks on new jobs, and HUD telemetry.",
        "accent": "#00ff66"
    },
    {
        "id": "04",
        "slug": "terminal-monolith",
        "title": "Retro CRT Monolith",
        "category": "Monospace / Retro",
        "tagline": "100% green-phosphor CRT command-line recruitment terminal",
        "description": "Authentic 1980s mainframe interface with scanline curvature, phosphor glow, keyboard-driven commands (`job ls --state=gujarat`), and ASCII art charts.",
        "accent": "#33ff33"
    },
    {
        "id": "05",
        "slug": "brutalist-newspaper",
        "title": "The Gazette Broadsheet 1920",
        "category": "Editorial / Print",
        "tagline": "Vintage newsprint broadsheet with hot-metal typography",
        "description": "Classic multi-column newspaper layout with vintage typography, engraved government emblems, classifieds columns, and wax-seal confirmation badges.",
        "accent": "#1a1a1a"
    },
    {
        "id": "06",
        "slug": "luxury-atelier",
        "title": "Atelier Gazette Privée",
        "category": "Luxury / Haute Couture",
        "tagline": "High-fashion editorial lookbook for executive appointments",
        "description": "Silk and marble aesthetics with Didot serif typography, full-bleed imagery, and discreet luxury presentation for Class-1 GAS, GPS, and IAS careers.",
        "accent": "#c5a880"
    },
    {
        "id": "07",
        "slug": "liquid-physics",
        "title": "Liquid Bubble Dynamics",
        "category": "Physics / Generative",
        "tagline": "Interactive liquid simulation with floating job bubbles",
        "description": "Jobs float as hydrostatic fluid bubbles that merge, collide, and pop to reveal detailed syllabus breakdowns and vacancy breakdowns.",
        "accent": "#ff2d55"
    },
    {
        "id": "08",
        "slug": "infinite-zoom",
        "title": "Infinite Semantic Zoom",
        "category": "Zoomable Canvas",
        "tagline": "Seamless infinite zoom from macro sectors to micro exam questions",
        "description": "Pan and zoom effortlessly from All India overview into Gujarat State, into GPSC board, into Mamlatdar post, into the exact 15KB photo upload guide.",
        "accent": "#5856d6"
    },
    {
        "id": "09",
        "slug": "bento-desktop-os",
        "title": "FuturSet OS Desktop",
        "category": "Desktop / Window Manager",
        "tagline": "Complete web-based operating system with draggable tool windows",
        "description": "Windowed multi-tasking desktop featuring the 7th Pay Calculator window, Article Pipeline window, Live Radar scanner window, and system dock.",
        "accent": "#007aff"
    },
    {
        "id": "10",
        "slug": "neumorphic-clay",
        "title": "Neumorphic Tactile Clay",
        "category": "Neumorphism",
        "tagline": "Soft extruded clay cards with physical tactile shadows",
        "description": "Physical soft-plastic aesthetic with realistic dual-shadow depth, tactile toggle switches, and smooth inset pill buttons.",
        "accent": "#e0e5ec"
    },
    {
        "id": "11",
        "slug": "dark-hologram",
        "title": "Dark Hologram Laboratory",
        "category": "Hologram / Sci-Fi",
        "tagline": "Wireframe holographic grid with cyan laser projections",
        "description": "Floating 3D wireframe wireframes projecting official gazette notifications in mid-air with volumetric lighting and laser grid floors.",
        "accent": "#00f7ff"
    },
    {
        "id": "12",
        "slug": "swiss-poster",
        "title": "Zurich Typographic Poster",
        "category": "Swiss Style",
        "tagline": "Bold asymmetric Swiss poster layout with strict mathematical grids",
        "description": "Ultra-bold Akzidenz-Grotesk headlines, diagonal grid shifts, stark black/red/white contrasts, and supreme typographic clarity.",
        "accent": "#ff3b30"
    },
    {
        "id": "13",
        "slug": "audio-radar",
        "title": "Acoustic Telemetry Synthesizer",
        "category": "Audio / Visualizer",
        "tagline": "Visual acoustic frequency spectrum for live recruitment feeds",
        "description": "Frequency synthesizer visualizer translating incoming gazette streams into harmonic waveforms, audio pulses, and real-time spectrum graphs.",
        "accent": "#af52de"
    },
    {
        "id": "14",
        "slug": "spatial-carousel",
        "title": "360° Spatial Carousel",
        "category": "3D Carousel",
        "tagline": "Rotating 3D cylindrical carousel of recruitment cards",
        "description": "Swipe or drag to rotate a 360-degree 3D circular carousel of active government vacancies with depth blur and perspective scaling.",
        "accent": "#34c759"
    },
    {
        "id": "15",
        "slug": "cinematic-story",
        "title": "Aspirant Odyssey: Cinematic Scroll",
        "category": "Scrollytelling",
        "tagline": "Fullscreen story scroll following an aspirant from application to appointment",
        "description": "Cinematic visual chapters tracking the journey of a Gujarat student through OTR registration, prelims CBRT, physical test, mains, and appointment.",
        "accent": "#ff9500"
    },
    {
        "id": "16",
        "slug": "isometric-city",
        "title": "Gujarat Sachivalaya Isometric Map",
        "category": "Isometric / Map",
        "tagline": "Interactive 3D isometric city with government buildings",
        "description": "Explore an isometric 3D Gandhinagar capital complex where clicking the Police HQ opens LRD jobs, High Court opens assistant jobs, and Sachivalaya opens GPSC.",
        "accent": "#30b0c7"
    },
    {
        "id": "17",
        "slug": "pixel-arcade",
        "title": "8-Bit Rojgar Arcade",
        "category": "Retro Gaming",
        "tagline": "Chiptune 8-bit retro gaming interface for government careers",
        "description": "Pixel-art dashboard featuring 16-bit sprites, retro game dialog boxes, high-score vacancy leaderboards, and quest-based exam preparation tracks.",
        "accent": "#ffcc00"
    },
    {
        "id": "18",
        "slug": "glass-prism",
        "title": "Refractive Optical Prism",
        "category": "Optics / Glass",
        "tagline": "Multi-spectral light refraction through crystal glass prisms",
        "description": "Light refracts into chromatic spectrums through frosted crystal slabs, creating prismatic color flares on hover and cursor movement.",
        "accent": "#e056fd"
    },
    {
        "id": "19",
        "slug": "aurora-sky",
        "title": "Borealis Sky Observatorium",
        "category": "Atmospheric Sky",
        "tagline": "Celestial starry night sky with dynamic aurora borealis waves",
        "description": "Night-sky canvas where constellations represent central recruitment boards (SSC, UPSC, RRB) and northern lights ripple when new notifications drop.",
        "accent": "#70a1ff"
    },
    {
        "id": "20",
        "slug": "accessible-terminal",
        "title": "A11y High-Contrast Braille Console",
        "category": "Accessibility First",
        "tagline": "WCAG AAA 14:1 ultra-contrast high-velocity accessible console",
        "description": "Engineered for maximum accessibility with amber-on-black 14:1 contrast, screen-reader optimized landmarks, keyboard-only shortcuts, and zero layout shift.",
        "accent": "#ffbf00"
    }
]
