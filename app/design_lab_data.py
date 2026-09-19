"""
FuturSet Design Lab & Concept Lab Metadata
Defines comprehensive design intelligence, inspiration sources, animation specifications,
performance metrics, and visual tokens for all 50 Product Previews and 20 Standalone Concept Websites.
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
            {"name": "Staggered Entrance", "source": "Prismic CSS Guide", "url": "https://prismic.io/blog/css-animations", "usage": "Job Cards & Dossiers", "tech": "CSS keyframes fadeUp + var(--card-index)", "gpu": "Composite-only (transform & opacity)", "a11y": "Disabled via prefers-reduced-motion"},
            {"name": "Glass Specular Sweep", "source": "CodePen Glassmorphism", "url": "https://codepen.io/tag/glassmorphism", "usage": "Card Hover Sheen", "tech": "CSS ::after + linear-gradient + transform", "gpu": "0ms layout recalculation", "a11y": "Subtle visual feedback"},
            {"name": "Sonar Radar Ripple", "source": "Motion.dev", "url": "https://motion.dev", "usage": "Live Status Badges", "tech": "CSS keyframes sonar + opacity", "gpu": "Hardware-accelerated transform scale", "a11y": "WCAG AAA 7:1 contrast ratio"},
            {"name": "Scroll Progress Bar", "source": "CSS Scroll-Driven", "url": "https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll-driven_animations", "usage": "Top Viewport Indicator", "tech": "animation-timeline: scroll() + JS fallback", "gpu": "Off-main-thread compositor scroll", "a11y": "Hidden when reduced-motion active"}
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
            {"name": "Subtle Border Illuminate", "source": "Linear.app", "url": "https://linear.app", "usage": "Card & Row Borders", "tech": "transition: border-color 0.1s ease", "gpu": "Repaint-only, 0 layout shifts", "a11y": "High-contrast border outline"},
            {"name": "Quick Monospace Shift", "source": "Linear Changelog", "url": "https://linear.app/changelog", "usage": "Table Rows & Badges", "tech": "font-feature-settings: 'tnum'", "gpu": "Instant render", "a11y": "Tabular numerals for screen readers"}
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
            {"name": "Liquid Button Fill", "source": "Prismic Button Catalog", "url": "https://prismic.io/blog/css-animations", "usage": "Primary CTA Buttons", "tech": "CSS ::before scale/translate on hover", "gpu": "Composite-only transform scaleY", "a11y": "Touch targets > 44px"},
            {"name": "Ambient Gradient Breathing", "source": "Stripe Radar", "url": "https://stripe.com/radar", "usage": "Background Canvas", "tech": "CSS background-position cycle 12s", "gpu": "GPU layer caching", "a11y": "Paused on reduced-motion"}
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
            {"name": "Radial Spotlight Hover", "source": "Raycast UI", "url": "https://raycast.com", "usage": "Interactive Cards", "tech": "radial-gradient(circle at var(--mouse-x), ...)", "gpu": "CSS custom property binding", "a11y": "Fallbacks to static border"},
            {"name": "Command Key Pulse", "source": "Raycast Shortcuts", "url": "https://raycast.com/manual", "usage": "Kbd Badges", "tech": "box-shadow keyframes", "gpu": "Composite-only", "a11y": "High contrast key indicators"}
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
            {"name": "Underline Sweep", "source": "Hover.css", "url": "https://ianlunn.github.io/Hover/", "usage": "Navigation Links", "tech": "transform: scaleX(1)", "gpu": "0ms layout reflow", "a11y": "Visible text contrast > 12:1"},
            {"name": "Minimalist Fade", "source": "Vanilla CSS", "url": "https://developer.mozilla.org", "usage": "Modal & Filter Transitions", "tech": "opacity 0.15s ease", "gpu": "GPU alpha composite", "a11y": "Instant alternative on Esc"}
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
            {"name": "Floating Card Hover", "source": "CSS 3D Transforms", "url": "https://developer.mozilla.org/en-US/docs/Web/CSS/transform", "usage": "Job Cards & Pipeline Stages", "tech": "transform: translateY(-6px) translateZ(10px)", "gpu": "GPU 3D matrix composite", "a11y": "Smooth non-jarring elevation"},
            {"name": "Diffuse Ambient Glow", "source": "Spatial UI", "url": "https://developer.apple.com/design", "usage": "Card Shadows", "tech": "box-shadow: 0 20px 40px -15px rgba(0,0,0,0.7)", "gpu": "Cached box-shadow", "a11y": "High card separation"}
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
            {"name": "Spring Elastic Hover", "source": "Motion.dev Spring", "url": "https://motion.dev", "usage": "Action Buttons & Chips", "tech": "cubic-bezier(0.34, 1.56, 0.64, 1)", "gpu": "Sub-pixel transform precision", "a11y": "Non-distracting bounce"},
            {"name": "Asymmetrical Reveal", "source": "Framer Motion", "url": "https://www.framer.com/motion/", "usage": "Section Headers", "tech": "staggered translate & rotate", "gpu": "Composite-only", "a11y": "Screen-reader friendly"}
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
            {"name": "Jelly Button Press", "source": "CodePen Playful", "url": "https://codepen.io/tag/button-animation", "usage": "Apply & Filter Buttons", "tech": "keyframes jellyBounce", "gpu": "Composite transform scale", "a11y": "Distinct tactile active state"},
            {"name": "Badge Pop", "source": "Prismic Micro-Interactions", "url": "https://prismic.io", "usage": "Urgency & Vacancy Badges", "tech": "transform: scale(1.08)", "gpu": "GPU layer caching", "a11y": "Visual prominence"}
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
            {"name": "Editorial Text Reveal", "source": "CSS Typography", "url": "https://typewolf.com", "usage": "Article Titles & Summaries", "tech": "keyframes textFadeIn", "gpu": "Opacity-only transition", "a11y": "AAA contrast text"},
            {"name": "Ink Underline Expansion", "source": "Prismic Editorial", "url": "https://prismic.io", "usage": "Links & Citations", "tech": "transition: width 0.3s ease", "gpu": "Transform scaleX", "a11y": "Focus-visible compliant"}
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
            {"name": "Curtain Clip Reveal", "source": "Awwwards Trends", "url": "https://www.awwwards.com", "usage": "Banner & Pipeline", "tech": "clip-path: inset(0 0 0 0)", "gpu": "GPU polygon rasterization", "a11y": "Zero content blockage"},
            {"name": "Cinematic Letterspacing Shift", "source": "Awwwards Typography", "url": "https://www.awwwards.com/websites/", "usage": "Headings", "tech": "transition: letter-spacing 0.4s", "gpu": "Typography reflow contained", "a11y": "Preserves word break"}
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
            {"name": "Scanline Overlay", "source": "CodePen Cyber", "url": "https://codepen.io/tag/cyberpunk", "usage": "Background Texture", "tech": "repeating-linear-gradient scanline", "gpu": "Static pattern cache", "a11y": "Non-distracting opacity"},
            {"name": "Neon Border Pulse", "source": "Prismic Neon", "url": "https://prismic.io", "usage": "Scanner & Gazette Cards", "tech": "box-shadow: 0 0 15px cyan", "gpu": "Box-shadow composite", "a11y": "Color contrast > 8:1"}
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
            {"name": "Specular Edge Shimmer", "source": "Glassmorphism Guide", "url": "https://uxdesign.cc/glassmorphism-in-user-interfaces-1f39bb1308c9", "usage": "All Panels & Modals", "tech": "backdrop-filter: blur(24px) + border reflection", "gpu": "GPU blur pipeline", "a11y": "Text background legibility guard"},
            {"name": "Ice Sheen Hover", "source": "CodePen Glass", "url": "https://codepen.io", "usage": "Buttons & Chips", "tech": "linear-gradient(135deg, rgba(255,255,255,0.2), transparent)", "gpu": "0ms layout reflow", "a11y": "High-contrast state"}
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
            {"name": "Aurora Mesh Wave", "source": "CSS Mesh Gradients", "url": "https://cssgradient.io", "usage": "Full Canvas Background", "tech": "keyframes auroraBreathing 12s ease-in-out infinite", "gpu": "GPU background-position cycle", "a11y": "Paused on reduced-motion"},
            {"name": "Soft Diffuse Hover", "source": "Prismic Ambient", "url": "https://prismic.io", "usage": "Job Cards & Badges", "tech": "filter: drop-shadow(0 0 12px rgba(99,91,255,0.4))", "gpu": "Drop-shadow composite", "a11y": "Clear focus rings"}
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
            {"name": "Bento Tile Scale", "source": "Bento.me Design", "url": "https://bento.me", "usage": "Dashboard Widgets & Tools", "tech": "transform: scale(1.02) + border-glow", "gpu": "Transform scale composite", "a11y": "Keyboard focusable tiles"},
            {"name": "Widget Pill Badge Pulse", "source": "Apple Bento", "url": "https://apple.com", "usage": "Status Counters", "tech": "keyframes pulse", "gpu": "Opacity transition", "a11y": "Screen reader live region"}
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
            {"name": "Grid Line Highlight", "source": "Swiss Style", "url": "https://swissstyle.com", "usage": "Table Rows & Borders", "tech": "outline: 1px solid currentColor", "gpu": "Instant outline swap", "a11y": "Extreme contrast 14:1"},
            {"name": "Instant Type Invert", "source": "Swiss Poster", "url": "https://www.poster-gallery.com", "usage": "Button Invert", "tech": "background: #fff; color: #000;", "gpu": "0ms composite", "a11y": "AAA rating"}
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
            {"name": "Soft Shadow Elevation", "source": "Tailwind Soft Shadows", "url": "https://tailwindcss.com", "usage": "Job Cards on Hover", "tech": "box-shadow: 0 12px 24px -4px rgba(0,0,0,0.08)", "gpu": "Box-shadow composite", "a11y": "Card boundary visible"},
            {"name": "Pastel Chip Fade", "source": "Notion UI", "url": "https://notion.so", "usage": "Filter Chips", "tech": "transition: background 0.15s", "gpu": "0 layout shift", "a11y": "Color + icon differentiation"}
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
            {"name": "Blinking CLI Cursor", "source": "CodePen Terminal", "url": "https://codepen.io/tag/terminal", "usage": "Search & Headers", "tech": "keyframes blink 1s infinite", "gpu": "Opacity toggle", "a11y": "Accessible aria-label"},
            {"name": "LED Status Blip", "source": "Terminal UI", "url": "https://warp.dev", "usage": "Live Telemetry", "tech": "keyframes ledPulse 2s ease infinite", "gpu": "Box-shadow blink", "a11y": "Status text accompanied"}
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
            {"name": "Data Ticker Scroll", "source": "Fintech UI", "url": "https://wealthsimple.com", "usage": "Top Gazette Ticker", "tech": "keyframes marquee 25s linear infinite", "gpu": "Transform translateX composite", "a11y": "Can be paused by user"},
            {"name": "Tabular Delta Highlight", "source": "Wealthsimple", "url": "https://wealthsimple.com", "usage": "Vacancies & Salary", "tech": "transition: color 0.2s, background 0.2s", "gpu": "0ms reflow", "a11y": "Text arrows indicate trend"}
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
            {"name": "Cursor 3D Card Tilt", "source": "CodePen 3D Tilt", "url": "https://codepen.io/tag/3d-card", "usage": "Job Cards & Article Cards", "tech": "transform: perspective(1000px) rotateX(var(--rx)) rotateY(var(--ry))", "gpu": "Hardware GPU 3D matrix", "a11y": "Clamped tilt (< 8deg)"},
            {"name": "Z-Axis Floating Chip", "source": "3D Spatial UI", "url": "https://atroposjs.com", "usage": "Card Badges", "tech": "transform: translateZ(20px)", "gpu": "GPU z-buffer", "a11y": "Clear text readability"}
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
            {"name": "Border-Radius Morph", "source": "Prismic Organic CSS", "url": "https://prismic.io", "usage": "Featured Badges & Icons", "tech": "keyframes morphBlob 8s ease-in-out infinite", "gpu": "Border-radius interpolation", "a11y": "Fixed interior content box"},
            {"name": "Liquid Fill Button", "source": "Prismic Button Catalog", "url": "https://prismic.io", "usage": "Primary Actions", "tech": "liquid wave SVG or clip-path hover", "gpu": "Clip-path GPU raster", "a11y": "Clear button text contrast"}
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
            {"name": "Variable Weight Shift", "source": "Variable Fonts API", "url": "https://variablefonts.io", "usage": "Hero Titles & Card Headers", "tech": "transition: font-weight 0.3s cubic-bezier(0.16, 1, 0.3, 1)", "gpu": "Font weight composite", "a11y": "Continuous readability"},
            {"name": "Kinetic Word Slide", "source": "Prismic Typography", "url": "https://prismic.io", "usage": "Banner Headlines", "tech": "keyframes wordSlideUp", "gpu": "TranslateY composite", "a11y": "Screen readers read entire word"}
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
            {"name": "Holographic Foil Shimmer", "source": "CodePen Hologram", "url": "https://codepen.io/tag/holographic", "usage": "Card Backgrounds & Dossiers", "tech": "background: linear-gradient(115deg, transparent, rgba(255,255,255,0.4), transparent)", "gpu": "Background-position cycle", "a11y": "Non-flashing slow shimmer"},
            {"name": "Prismatic Border Glow", "source": "CSS Iridescent", "url": "https://cssdesignawards.com", "usage": "Card Borders", "tech": "border-image: linear-gradient(...) 1", "gpu": "Border composite", "a11y": "Clear edge definition"}
        ]
    },
    {
        "id": "23",
        "name": "Editorial Magazine",
        "badge": "Printed Press Elegance",
        "description": "Classic newsprint typography (Merriweather), elegant column dividers, sophisticated drop caps, and thoughtful whitespace.",
        "inspired_by": ["The New York Times", "Kinfolk Magazine", "Wired"],
        "motion": "Subtle ink-spread reveals, elegant column divider animations, quiet transitions",
        "accent": "#f1f5f9",
        "style_class": "theme-23-magazine",
        "animations": [
            {"name": "Ink-Spread Reveal", "source": "Editorial Design", "url": "https://land-book.com", "usage": "Articles & Job Summaries", "tech": "keyframes inkSpread", "gpu": "Opacity + transform composite", "a11y": "High legibility font"},
            {"name": "Column Rule Fade", "source": "Magazine CSS", "url": "https://siteinspire.com", "usage": "Grid Dividers", "tech": "border-color transition", "gpu": "0ms layout reflow", "a11y": "Semantic structure preserved"}
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
            {"name": "Hard Shadow Pop", "source": "Neo-Brutalism Standard", "url": "https://brutalistwebsites.com", "usage": "Buttons, Cards & Modals", "tech": "box-shadow: 4px 4px 0 #000; active: translate(2px,2px)", "gpu": "Instant physical feedback", "a11y": "Extremely distinct click states"},
            {"name": "Stark Border Flash", "source": "Brutalist CSS", "url": "https://gumroad.com", "usage": "Interactive Chips", "tech": "border: 2.5px solid #000", "gpu": "0 layout shift", "a11y": "High contrast black on yellow"}
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
            {"name": "Micro-Shadow Elevation", "source": "Luxury UI", "url": "https://land-book.com", "usage": "Cards & Panels", "tech": "box-shadow: 0 4px 20px -2px rgba(0,0,0,0.05)", "gpu": "Cached box-shadow", "a11y": "Subtle, non-distracting"},
            {"name": "Hairline Border Soften", "source": "Minimalist CSS", "url": "https://siteinspire.com", "usage": "All Dividers", "tech": "border-color: rgba(0,0,0,0.06)", "gpu": "0ms composite", "a11y": "Clear visual hierarchy"}
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
            {"name": "OLED Spotlight Follower", "source": "OLED UI Design", "url": "https://apple.com/pro-display-xdr/", "usage": "Hero & Cards", "tech": "radial-gradient(600px at var(--x) var(--y), rgba(255,255,255,0.08), transparent)", "gpu": "CSS custom property binding", "a11y": "Saves battery on OLED devices"},
            {"name": "Vivid Gold Beacon", "source": "Cinematic CSS", "url": "https://sony.com", "usage": "Urgent Notifications", "tech": "box-shadow: 0 0 20px #f59e0b", "gpu": "Composite box-shadow", "a11y": "Instant urgency awareness"}
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
            {"name": "Sticky Milestone Reveal", "source": "ScrollStorytelling", "url": "https://apple.com/airpods-pro/", "usage": "Article Pipeline & Tools", "tech": "position: sticky + scroll progress animation", "gpu": "Compositor scroll thread", "a11y": "Content readable without scrolling"},
            {"name": "Section Morphing", "source": "Motion.page", "url": "https://motion.page", "usage": "Page Scroll", "tech": "keyframes morphSection", "gpu": "Transform composite", "a11y": "Smooth pacing"}
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
            {"name": "High-Contrast Focus Ring", "source": "WCAG AAA Guidelines", "url": "https://www.w3.org/WAI/WCAG21/Understanding/focus-visible.html", "usage": "All Interactive Controls", "tech": "outline: 3px solid #38bdf8; outline-offset: 2px;", "gpu": "Instant native outline", "a11y": "WCAG 2.1 AAA 100% Compliant"},
            {"name": "Instant Clear Feedback", "source": "A11y Standards", "url": "https://a11yproject.com", "usage": "Buttons & Form Inputs", "tech": "transition: none", "gpu": "0ms rendering", "a11y": "Immediate screen reader reaction"}
        ]
    },
    {
        "id": "29",
        "name": "AI Operating System",
        "badge": "Cognitive Workspace",
        "description": "Modern AI workspace with contextual sidebars, intelligent query suggestions, and smart widget layout.",
        "inspired_by": ["Cognition Devin", "Perplexity Workspaces", "Raycast AI"],
        "motion": "Smooth drawer expansion, contextual pill morphing, subtle glowing AI halos",
        "accent": "#a855f7",
        "style_class": "theme-29-aios",
        "animations": [
            {"name": "Cognitive Halo Glow", "source": "AI UI Design", "url": "https://perplexity.ai", "usage": "AI Matcher & Pipeline", "tech": "box-shadow: 0 0 25px rgba(168,85,247,0.35)", "gpu": "Composite box-shadow", "a11y": "Color contrast > 7:1"},
            {"name": "Contextual Panel Morph", "source": "Cognition AI", "url": "https://cognition.ai", "usage": "Tool Panels", "tech": "transition: flex-grow 0.25s cubic-bezier(0.16, 1, 0.3, 1)", "gpu": "Transform composite", "a11y": "Accessible tab index"}
        ]
    },
    {
        "id": "30",
        "name": "Data Immersion",
        "badge": "Visual Analytics",
        "description": "Data visualization as the visual language. Strong telemetry charts, live metric tickers, and smooth data transitions.",
        "inspired_by": ["Palantir Foundry", "Tableau Next", "Observable"],
        "motion": "Smooth chart bar grow, value counters, live stream pulse indicators",
        "accent": "#0ea5e9",
        "style_class": "theme-30-data",
        "animations": [
            {"name": "Telemetry Bar Grow", "source": "Observable HQ", "url": "https://observablehq.com", "usage": "Vacancy Bars", "tech": "keyframes growWidth 0.6s ease-out", "gpu": "Transform scaleX", "a11y": "Accessible data table fallback"},
            {"name": "Data Pulse Beacon", "source": "Palantir Foundry", "url": "https://palantir.com", "usage": "Active Jobs", "tech": "keyframes dataPulse 2s infinite", "gpu": "Opacity pulse", "a11y": "Live region announcements"}
        ]
    },
    {
        "id": "31",
        "name": "Editorial Dark Luxury",
        "badge": "Obsidian & Gold",
        "description": "Luxury typography, deep black obsidian canvas, gold foil typography accents, hairline rules, and generous whitespace.",
        "inspired_by": ["Monocle", "Robb Report", "Rolex"],
        "motion": "Whisper-quiet opacity transitions, slow 300ms hover lifts, gold foil shimmer",
        "accent": "#d4af37",
        "style_class": "theme-31-darklux",
        "animations": [
            {"name": "Gold Foil Shimmer", "source": "Luxury Editorial", "url": "https://monocle.com", "usage": "Category Badges", "tech": "linear-gradient(90deg, #d4af37, #fef08a, #d4af37)", "gpu": "Background-position shift", "a11y": "Contrast > 9:1 against obsidian"},
            {"name": "Whisper Lift", "source": "Rolex Digital", "url": "https://rolex.com", "usage": "Recruitment Cards", "tech": "transform: translateY(-3px)", "gpu": "0ms reflow", "a11y": "Smooth calm elevation"}
        ]
    },
    {
        "id": "32",
        "name": "Futuristic Glass Dashboard",
        "badge": "Holographic HUD",
        "description": "Frosted HUD panels, cyan holographic projection lines, depth blur, and high-end dashboard presentation.",
        "inspired_by": ["Iron Man Jarvis HUD", "FUI Design", "Minority Report UI"],
        "motion": "Holographic scanline sweep, HUD bracket alignment, luminous neon border flares",
        "accent": "#00e5ff",
        "style_class": "theme-32-hud",
        "animations": [
            {"name": "HUD Bracket Sweep", "source": "FUI Design Catalog", "url": "https://www.hudsandguis.com", "usage": "Job Cards & Pipeline", "tech": "keyframes hudSweep 4s linear infinite", "gpu": "Composite clip-path", "a11y": "Decorative only, text unaffected"},
            {"name": "Holographic Flare", "source": "Iron Man HUD", "url": "https://territorystudio.com", "usage": "Buttons & Badges", "tech": "box-shadow: 0 0 15px #00e5ff", "gpu": "Composite glow", "a11y": "High contrast cyan"}
        ]
    },
    {
        "id": "33",
        "name": "Calm Productivity",
        "badge": "Low-Noise Sanctuary",
        "description": "Low-noise, high clarity, soothing warm-slate palette, quiet motion, and productivity-first UX.",
        "inspired_by": ["Basecamp", "Readwise Reader", "Bear Notes"],
        "motion": "Soft 180ms ease transitions, gentle underline reveals, zero distracting effects",
        "accent": "#94a3b8",
        "style_class": "theme-33-calm",
        "animations": [
            {"name": "Zen Fade In", "source": "Readwise Reader", "url": "https://readwise.io/read", "usage": "Cards & Lists", "tech": "opacity 0.2s ease-out", "gpu": "Alpha composite", "a11y": "Zero motion triggers"},
            {"name": "Gentle Underline", "source": "Basecamp", "url": "https://basecamp.com", "usage": "Links", "tech": "border-bottom: 1.5px solid", "gpu": "0ms layout cost", "a11y": "Clear link affordance"}
        ]
    },
    {
        "id": "34",
        "name": "Creative Technology",
        "badge": "Interactive Canvas",
        "description": "Creative-code aesthetic, interactive surfaces, particle gravity, and high-quality creative motion.",
        "inspired_by": ["Resn", "Active Theory", "Hello Monday"],
        "motion": "Cursor particle repulsion, dynamic card skew on fast scroll, fluid ripple clicks",
        "accent": "#ff0055",
        "style_class": "theme-34-creative",
        "animations": [
            {"name": "Particle Repulsion", "source": "Active Theory", "url": "https://activetheory.net", "usage": "Background Canvas", "tech": "Canvas 2D particle vector math", "gpu": "Off-thread requestAnimationFrame", "a11y": "Background only, accessible DOM"},
            {"name": "Fluid Click Ripple", "source": "Resn Studio", "url": "https://resn.co.nz", "usage": "Buttons & Cards", "tech": "radial-gradient scale on mousedown", "gpu": "Composite transform", "a11y": "Clear touch acknowledgement"}
        ]
    },
    {
        "id": "35",
        "name": "Monochrome System",
        "badge": "Dot-Matrix Geometry",
        "description": "Almost entirely monochrome. Typography, dot-matrix grids, geometry, and crisp interaction form the identity.",
        "inspired_by": ["Teenage Engineering", "Nothing OS", "Braun"],
        "motion": "Snappy 60ms state swaps, dot-matrix blink, geometric box flips",
        "accent": "#d1d5db",
        "style_class": "theme-35-monochrome",
        "animations": [
            {"name": "Dot Matrix Blink", "source": "Nothing OS", "url": "https://nothing.tech", "usage": "Badges & Tickers", "tech": "opacity 0.08s step-end", "gpu": "Instant render", "a11y": "Extreme contrast 18:1"},
            {"name": "Geometric Invert", "source": "Teenage Engineering", "url": "https://teenage.engineering", "usage": "Hover Buttons", "tech": "background: #fff; color: #000;", "gpu": "0 layout cost", "a11y": "Highest accessibility score"}
        ]
    },
    {
        "id": "36",
        "name": "Neon Data",
        "badge": "Tokyo Synthwave",
        "description": "Dark data environment with electric violet, lime green, and hot pink information accents on deep navy.",
        "inspired_by": ["Blade Runner 2049", "Tokyo Night", "Vaporwave Tech"],
        "motion": "Pulsing neon lines, chromatic aberration hover, fast synthwave grid drift",
        "accent": "#a3e635",
        "style_class": "theme-36-neondata",
        "animations": [
            {"name": "Neon Lime Pulse", "source": "Synthwave CSS", "url": "https://codepen.io/tag/synthwave", "usage": "Urgent Vacancies", "tech": "box-shadow: 0 0 12px #a3e635", "gpu": "Composite glow", "a11y": "High contrast on dark slate"},
            {"name": "Synthwave Grid Drift", "source": "Tokyo Night Theme", "url": "https://github.com/enkia/tokyo-night-vscode-theme", "usage": "Canvas Grid", "tech": "background-position: 0 100%", "gpu": "GPU background drift", "a11y": "Subtle opacity (15%)"}
        ]
    },
    {
        "id": "37",
        "name": "Premium Enterprise",
        "badge": "Corporate Trust",
        "description": "Trust, clarity, dense business information hierarchy, and professional corporate UX.",
        "inspired_by": ["Salesforce Lightning", "Snowflake", "Workday"],
        "motion": "Structured 140ms ease-in-out transitions, metric badge updates, calm table pagination",
        "accent": "#2563eb",
        "style_class": "theme-37-enterprise",
        "animations": [
            {"name": "Metric Badge Update", "source": "Salesforce Lightning", "url": "https://lightningdesignsystem.com", "usage": "Stats & Totals", "tech": "keyframes badgeFlash 0.4s", "gpu": "Background composite", "a11y": "Announced to screen readers"},
            {"name": "Corporate Border Reveal", "source": "Snowflake UI", "url": "https://snowflake.com", "usage": "Data Tables", "tech": "border-color: #2563eb", "gpu": "0ms layout shift", "a11y": "Clear visual delimiters"}
        ]
    },
    {
        "id": "38",
        "name": "Product Studio",
        "badge": "Canvas-Centric",
        "description": "Minimal product interface, creative presentation, floating tool palettes, and premium motion.",
        "inspired_by": ["Figma", "Framer Studio", "Spline"],
        "motion": "Floating dock hover, canvas zoom simulation, tool palette snap",
        "accent": "#0ea5e9",
        "style_class": "theme-38-studio",
        "animations": [
            {"name": "Palette Snap", "source": "Figma Design System", "url": "https://figma.com", "usage": "Floating Compare Dock", "tech": "transform: translateY(0) scale(1)", "gpu": "Sub-pixel transform", "a11y": "Accessible keyboard controls"},
            {"name": "Canvas Hover Glow", "source": "Framer Studio", "url": "https://framer.com", "usage": "Interactive Cards", "tech": "box-shadow: 0 10px 30px rgba(14,165,233,0.25)", "gpu": "Composite shadow", "a11y": "Focus-visible ring"}
        ]
    },
    {
        "id": "39",
        "name": "Immersive WebGL",
        "badge": "GPU Acceleration",
        "description": "WebGL-inspired visual language with fluid particle physics, smooth inertial transforms, and high performance.",
        "inspired_by": ["Three.js Journey", "Lusion.co", "Bruno Simon"],
        "motion": "Inertial drag simulation, spring-damping card tilt, GPU mesh refraction",
        "accent": "#00f0ff",
        "style_class": "theme-39-webgl",
        "animations": [
            {"name": "Inertial Card Tilt", "source": "Bruno Simon Portfolio", "url": "https://bruno-simon.com", "usage": "Job Cards", "tech": "transform: perspective(800px) rotateX(var(--rx)) rotateY(var(--ry))", "gpu": "Hardware GPU 3D acceleration", "a11y": "Damped motion < 6deg"},
            {"name": "Refractive Canvas Aura", "source": "Lusion Studio", "url": "https://lusion.co", "usage": "Background Canvas", "tech": "Canvas 2D chromatic refraction", "gpu": "WebGL/Canvas composite", "a11y": "Respects reduced-motion"}
        ]
    },
    {
        "id": "40",
        "name": "Future Master",
        "badge": "2026 Synthesis",
        "description": "Completely original design based on the strongest new ideas from 2026 internet design research. Adaptive kinetic cards, fluid pills, and responsive aura.",
        "inspired_by": ["2026 Design Trends", "Awwwards Site of the Year", "Future Web Standards"],
        "motion": "Adaptive kinetic card hover, dynamic light-cone projection, fluid spring pill transitions",
        "accent": "#7c3aed",
        "style_class": "theme-40-future",
        "animations": [
            {"name": "Dynamic Light-Cone Projection", "source": "Future Web Standards", "url": "https://w3c.github.io/csswg-drafts/", "usage": "Hero & Dossiers", "tech": "conic-gradient + radial-gradient mask", "gpu": "Compositor-only raster", "a11y": "Contrast > 10:1"},
            {"name": "Fluid Spring Pill", "source": "2026 Interaction Design", "url": "https://motion.dev", "usage": "Filter Chips & Actions", "tech": "cubic-bezier(0.16, 1, 0.3, 1)", "gpu": "0ms layout reflow", "a11y": "WCAG AAA compliant"}
        ]
    },
    {
        "id": "41",
        "name": "Neomorphic Clay",
        "badge": "Soft Spatial",
        "description": "Tactile extruded soft-surface UI with dual inner/outer shadows, pill switches, and physical soft-plastic depth.",
        "inspired_by": ["Dribbble Claymorphism", "Skeuomorphism 2.0", "Apple Watch UI"],
        "motion": "Tactile button depression on mousedown, soft shadow collapse, smooth clay transitions",
        "accent": "#818cf8",
        "style_class": "theme-41-clay",
        "animations": [
            {"name": "Tactile Clay Depression", "source": "Claymorphism CSS", "url": "https://uxdesign.cc/claymorphism-in-user-interfaces-e668b550d322", "usage": "Interactive Buttons & Cards", "tech": "box-shadow: inset 4px 4px 8px rgba(0,0,0,0.5), inset -4px -4px 8px rgba(255,255,255,0.05)", "gpu": "Composite box-shadow", "a11y": "Clear pressed state for touch"},
            {"name": "Soft Shadow Morph", "source": "Neumorphism IO", "url": "https://neumorphism.io", "usage": "Card Hover", "tech": "transition: box-shadow 0.2s ease", "gpu": "Cached shadow composite", "a11y": "Boundary line ensures readability"}
        ]
    },
    {
        "id": "42",
        "name": "Bento OS v2",
        "badge": "Window Dock OS",
        "description": "Floating desktop dock with windowed tool widgets, draggable pods, and modular operating-system ergonomics.",
        "inspired_by": ["macOS Sequoia", "Raycast Floating Dock", "Bento.me"],
        "motion": "Dock icon magnification on hover, smooth window popout, snap-to-grid reordering",
        "accent": "#38bdf8",
        "style_class": "theme-42-dockos",
        "animations": [
            {"name": "Dock Magnification", "source": "macOS Dock CSS", "url": "https://apple.com/macos", "usage": "Bottom Navigation & Tools", "tech": "transform: scale(1.15) translateY(-4px)", "gpu": "Transform composite", "a11y": "Keyboard accessible dock"},
            {"name": "Window Popout Spring", "source": "Raycast Floating Panel", "url": "https://raycast.com", "usage": "Modals & Dossiers", "tech": "cubic-bezier(0.34, 1.56, 0.64, 1)", "gpu": "GPU layer caching", "a11y": "Focus trapped inside window"}
        ]
    },
    {
        "id": "43",
        "name": "High-Frequency Telemetry",
        "badge": "Neural Data Graph",
        "description": "Real-time streaming status blips, live flashing delta indicators, connected node clusters, and ticker feeds.",
        "inspired_by": ["NASDAQ TradeStation", "Etherscan", "Bloomberg Professional"],
        "motion": "Rapid delta flash (green/red), ticker marquee, neural node pulse wave",
        "accent": "#10b981",
        "style_class": "theme-43-telemetry",
        "animations": [
            {"name": "Delta Flash Blip", "source": "Wall Street Telemetry", "url": "https://bloomberg.com", "usage": "Vacancies & Pay Matrix", "tech": "keyframes deltaFlash 0.8s ease-out", "gpu": "Color composite", "a11y": "Includes up/down symbols"},
            {"name": "Neural Wave Pulse", "source": "Etherscan Telemetry", "url": "https://etherscan.io", "usage": "Live Scanner Feed", "tech": "keyframes wavePulse 3s infinite", "gpu": "Opacity pulse", "a11y": "Live stream status visible"}
        ]
    },
    {
        "id": "44",
        "name": "Papercraft & Tactile Origami",
        "badge": "Tactile Material",
        "description": "Layered fold-out paper panels, realistic fiber texture, tactile crease shadows, and origami-inspired card reveals.",
        "inspired_by": ["Material Design 3", "Papercraft Web", "Origami Studio"],
        "motion": "Paper fold-out 3D rotation, subtle corner curl on hover, physical page flip transitions",
        "accent": "#f59e0b",
        "style_class": "theme-44-papercraft",
        "animations": [
            {"name": "Paper Corner Curl", "source": "CodePen Paper", "url": "https://codepen.io/tag/paper", "usage": "Job Cards & Dossiers", "tech": "transform: rotate(-1deg) translateY(-4px)", "gpu": "GPU 2D transform", "a11y": "No layout distortion"},
            {"name": "Origami Panel Unfold", "source": "Origami Studio", "url": "https://origami.design", "usage": "Pipeline Stages", "tech": "transform: perspective(600px) rotateX(0)", "gpu": "Composite 3D", "a11y": "Screen readers see unfolded content"}
        ]
    },
    {
        "id": "45",
        "name": "Retro Cyberpunk 2099",
        "badge": "Chiptune & CRT",
        "description": "Neon scanlines, CRT screen curvature distortion, high-fidelity chiptune aesthetic, and hot magenta/cyan wires.",
        "inspired_by": ["Cyberpunk 2077", "90s Geocities Reimagined", "Vaporwave"],
        "motion": "CRT scanline warp, glitch text on hover, neon wire trace animation",
        "accent": "#ff007f",
        "style_class": "theme-45-retrocyber",
        "animations": [
            {"name": "CRT Scanline Warp", "source": "Retro CRT CSS", "url": "https://codepen.io/tag/crt", "usage": "Scanner & Telemetry", "tech": "repeating-linear-gradient + subtle vignette", "gpu": "GPU background blend", "a11y": "Contrast > 9:1"},
            {"name": "Neon Wire Trace", "source": "Cyberpunk UI", "url": "https://cyberpunk.net", "usage": "Section Borders", "tech": "stroke-dashoffset animation", "gpu": "SVG hardware acceleration", "a11y": "Purely decorative"}
        ]
    },
    {
        "id": "46",
        "name": "Nordic Minimal",
        "badge": "Warm Organic",
        "description": "Soft birch, stone, and linen tones, warm muted typography, serene generous whitespace, and calm Scandinavian aesthetics.",
        "inspired_by": ["Scandinavian Design", "Muuto", "Artek"],
        "motion": "Serene 220ms ease transitions, quiet hover states, gentle natural rhythm",
        "accent": "#78716c",
        "style_class": "theme-46-nordic",
        "animations": [
            {"name": "Nordic Soft Fade", "source": "Scandinavian Minimal", "url": "https://muuto.com", "usage": "All Cards & Panels", "tech": "transition: all 0.22s ease", "gpu": "Composite transition", "a11y": "Calm, zero motion sickness"},
            {"name": "Stone Border Tone", "source": "Artek Design", "url": "https://artek.fi", "usage": "Dividers", "tech": "border-color: #d6d3d1", "gpu": "0ms reflow", "a11y": "Clear structural lines"}
        ]
    },
    {
        "id": "47",
        "name": "Biophilic Glass",
        "badge": "Botanical Tech",
        "description": "Translucent botanical emerald and sage frosted glass with organic breathing glow, leafy accents, and natural balance.",
        "inspired_by": ["Biophilic Architecture", "Eden Project", "Apple Environmental"],
        "motion": "Organic breathing glow, leafy green pulse, smooth morning dew hover transitions",
        "accent": "#059669",
        "style_class": "theme-47-biophilic",
        "animations": [
            {"name": "Organic Breathing Glow", "source": "Biophilic UI", "url": "https://edenproject.com", "usage": "Pipeline & Cards", "tech": "keyframes biophilicGlow 6s ease-in-out infinite", "gpu": "Composite box-shadow", "a11y": "Slow non-flashing period"},
            {"name": "Sage Dew Hover", "source": "Nature Tech", "url": "https://apple.com/environment", "usage": "Action Buttons", "tech": "background: linear-gradient(135deg, #059669, #10b981)", "gpu": "0 layout cost", "a11y": "AAA contrast text"}
        ]
    },
    {
        "id": "48",
        "name": "Isometric Holographic 3D",
        "badge": "Orthographic Projection",
        "description": "2.5D isometric card projection with illuminated neon edges, depth elevation layers, and architectural spatial grids.",
        "inspired_by": ["Monument Valley", "SimCity 3D", "Figma 3D"],
        "motion": "Orthographic card lift on z-axis, illuminated isometric edge sweep, layer separation",
        "accent": "#6366f1",
        "style_class": "theme-48-isometric",
        "animations": [
            {"name": "Orthographic Z-Lift", "source": "Monument Valley UI", "url": "https://monumentvalleygame.com", "usage": "Job Cards & Tools", "tech": "transform: rotateX(15deg) rotateY(-10deg) translateZ(15px)", "gpu": "GPU 3D matrix transform", "a11y": "Text remains sharp and unskewed"},
            {"name": "Isometric Edge Glow", "source": "Isometric CSS", "url": "https://codepen.io/tag/isometric", "usage": "Card Borders", "tech": "box-shadow: -4px 4px 0 #4338ca", "gpu": "Composite shadow", "a11y": "Clear 3D depth perception"}
        ]
    },
    {
        "id": "49",
        "name": "Dark Luxury Monospace",
        "badge": "The Developer Atelier",
        "description": "Ultra-refined JetBrains Mono typography, 0.5px hairline gold borders, dark charcoal surfaces, and couture developer aesthetics.",
        "inspired_by": ["The Developer Atelier", "JetBrains Fleet", "Prada Black"],
        "motion": "Typewriter character reveal, hairline border illuminate, quiet luxury micro-interactions",
        "accent": "#eab308",
        "style_class": "theme-49-atelier",
        "animations": [
            {"name": "Hairline Gold Illuminate", "source": "Developer Atelier", "url": "https://jetbrains.com/fleet/", "usage": "Cards & Pipeline", "tech": "border-color: rgba(234, 179, 8, 0.6)", "gpu": "0ms composite", "a11y": "High contrast gold on charcoal"},
            {"name": "Typewriter Stagger", "source": "Monospace UI", "url": "https://typewolf.com", "usage": "Headers & Badges", "tech": "keyframes typeChar 0.05s steps(1)", "gpu": "Composite opacity", "a11y": "Screen reader intact"}
        ]
    },
    {
        "id": "50",
        "name": "Quantum Nebula",
        "badge": "Future Canvas Master",
        "description": "Multi-spectral cosmic nebula aura with dynamic cursor gravity, celestial particle stars, and ethereal responsive cards.",
        "inspired_by": ["NASA James Webb", "WebGL Cosmic Engine", "Awwwards Master of the Year"],
        "motion": "Cosmic nebula breathing, gravity cursor particle attraction, prismatic stellar card flares",
        "accent": "#8b5cf6",
        "style_class": "theme-50-quantum",
        "animations": [
            {"name": "Cosmic Nebula Breathing", "source": "NASA JWST Interactive", "url": "https://webbtelescope.org", "usage": "Full Canvas Background", "tech": "keyframes nebulaBreathe 16s ease-in-out infinite", "gpu": "Hardware GPU background raster", "a11y": "Paused on reduced-motion"},
            {"name": "Stellar Prismatic Flare", "source": "Awwwards Master", "url": "https://awwwards.com", "usage": "Primary CTA & Pipeline", "tech": "linear-gradient(135deg, #8b5cf6, #ec4899, #38bdf8)", "gpu": "Composite gradient transform", "a11y": "WCAG AAA 7:1 contrast"}
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
