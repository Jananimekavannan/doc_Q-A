import React from "react";

export default function AnimatedBot({ state = "idle" }) {
  // state: 'idle' | 'uploading' | 'thinking' | 'answered'

  const getStatusText = () => {
    switch (state) {
      case "uploading":
        return "Scanning document...";
      case "thinking":
        return "Reasoning & retrieving...";
      case "answered":
        return "Answer ready!";
      default:
        return "DocuMind AI Ready";
    }
  };

  const getEyeColor = () => {
    switch (state) {
      case "uploading":
        return "#34D399";
      case "thinking":
        return "#FBBF24";
      case "answered":
        return "#60A5FA";
      default:
        return "#38BDF8";
    }
  };

  const eyeColor = getEyeColor();

  return (
    <div className={`side-robot-wrapper ${state}`}>
      {/* Robot Speech Bubble */}
      <div className="bot-side-speech">
        <span className="speech-dot" style={{ background: eyeColor, boxShadow: `0 0 8px ${eyeColor}` }} />
        <span className="speech-text">{getStatusText()}</span>
      </div>

      {/* Vector Illustration of the Exact Robot from the Reference Image */}
      <svg
        className="robot-svg"
        viewBox="0 0 260 320"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Shading Gradients */}
          <linearGradient id="bodyWhite" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#F1F5F9" />
            <stop offset="60%" stopColor="#E2E8F0" />
            <stop offset="100%" stopColor="#CBD5E1" />
          </linearGradient>

          <linearGradient id="bodyDark" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#64748B" />
            <stop offset="100%" stopColor="#334155" />
          </linearGradient>

          <linearGradient id="screenBg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#0B132B" />
            <stop offset="100%" stopColor="#020617" />
          </linearGradient>

          <linearGradient id="redBadge" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#EF4444" />
            <stop offset="100%" stopColor="#B91C1C" />
          </linearGradient>

          {/* Glow Filters */}
          <filter id="cyanGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* ================= LEGS & FEET (Standing at bottom) ================= */}
        <g className="robot-legs-group">
          {/* Left Leg (Background Leg) */}
          <g className="left-leg">
            {/* Ribbed Leg Segments */}
            <path d="M125 210 Q118 225 115 240" stroke="#334155" strokeWidth="12" strokeLinecap="round" />
            <path d="M125 210 Q118 225 115 240" stroke="#64748B" strokeWidth="8" strokeLinecap="round" />
            <circle cx="120" cy="225" r="5" fill="#1E293B" />
            {/* Left Foot / Boot */}
            <path
              d="M102 240 C102 235 125 235 128 240 L132 262 C132 266 100 266 98 262 Z"
              fill="url(#bodyWhite)"
              stroke="#0F172A"
              strokeWidth="4"
              strokeLinejoin="round"
            />
            <path d="M100 258 L130 258" stroke="#0F172A" strokeWidth="3" />
          </g>

          {/* Right Leg (Foreground Standing Leg) */}
          <g className="right-leg">
            {/* Ribbed Leg Segments */}
            <path d="M165 210 Q170 230 178 250" stroke="#334155" strokeWidth="14" strokeLinecap="round" />
            <path d="M165 210 Q170 230 178 250" stroke="#94A3B8" strokeWidth="9" strokeLinecap="round" />
            <circle cx="172" cy="230" r="6" fill="#1E293B" stroke="#0F172A" strokeWidth="2" />
            {/* Right Chunky Boot */}
            <path
              d="M162 250 C162 244 195 242 202 250 L208 276 C208 282 158 282 156 276 Z"
              fill="url(#bodyWhite)"
              stroke="#0F172A"
              strokeWidth="4.5"
              strokeLinejoin="round"
            />
            {/* Boot Sole Detail */}
            <path d="M158 272 L206 272" stroke="#0F172A" strokeWidth="3.5" />
          </g>
        </g>

        {/* ================= TORSO & CHEST ================= */}
        <g className="robot-torso-group">
          {/* Main Torso Block */}
          <path
            d="M118 145 C118 140 182 140 182 145 L178 205 C178 212 122 212 122 205 Z"
            fill="url(#bodyWhite)"
            stroke="#0F172A"
            strokeWidth="4.5"
            strokeLinejoin="round"
          />

          {/* Torso Shadow / Inset */}
          <path
            d="M125 185 C125 185 150 195 175 185 L173 203 C173 207 127 207 127 203 Z"
            fill="#CBD5E1"
            stroke="#0F172A"
            strokeWidth="2.5"
          />

          {/* Chest Shield / Triangle Badge */}
          <path
            d="M140 156 L160 156 L150 172 Z"
            fill="url(#redBadge)"
            stroke="#0F172A"
            strokeWidth="3"
            strokeLinejoin="round"
          />
          {/* Badge Highlight */}
          <path d="M143 158 L157 158" stroke="rgba(255,255,255,0.6)" strokeWidth="2" />
        </g>

        {/* ================= LEFT ARM (Holding the board) ================= */}
        <g className="robot-holding-arm">
          {/* Shoulder Joint */}
          <circle cx="118" cy="150" r="10" fill="#334155" stroke="#0F172A" strokeWidth="3.5" />

          {/* Ribbed Segmented Arm stretching to the left board */}
          <path
            d="M116 150 C95 145 78 135 60 128"
            stroke="#334155"
            strokeWidth="14"
            strokeLinecap="round"
          />
          <path
            d="M116 150 C95 145 78 135 60 128"
            stroke="#94A3B8"
            strokeWidth="9"
            strokeLinecap="round"
          />

          {/* Elbow Joint */}
          <circle cx="85" cy="140" r="6" fill="#1E293B" stroke="#0F172A" strokeWidth="2" />

          {/* Gripping Hand (Holding onto the board frame) */}
          <g className="grip-hand-svg" transform="translate(42, 114)">
            <rect
              x="0"
              y="0"
              width="22"
              height="20"
              rx="6"
              fill="url(#bodyWhite)"
              stroke="#0F172A"
              strokeWidth="3.5"
            />
            {/* Clamp Fingers wrapping the edge */}
            <circle cx="2" cy="5" r="4" fill="#64748B" stroke="#0F172A" strokeWidth="2" />
            <circle cx="2" cy="10" r="4" fill="#64748B" stroke="#0F172A" strokeWidth="2" />
            <circle cx="2" cy="15" r="4" fill="#64748B" stroke="#0F172A" strokeWidth="2" />
            {/* Thumb */}
            <ellipse cx="14" cy="4" rx="4" ry="3" fill="#64748B" stroke="#0F172A" strokeWidth="2" />
          </g>
        </g>

        {/* ================= RIGHT ARM (Bent & Pointing at the board) ================= */}
        <g className="robot-pointing-arm">
          {/* Shoulder Joint */}
          <circle cx="182" cy="154" r="10" fill="#334155" stroke="#0F172A" strokeWidth="3.5" />

          {/* Upper Arm */}
          <path d="M182 154 L196 175" stroke="#334155" strokeWidth="14" strokeLinecap="round" />
          <path d="M182 154 L196 175" stroke="#94A3B8" strokeWidth="9" strokeLinecap="round" />

          {/* Elbow Joint */}
          <circle cx="196" cy="175" r="7" fill="#1E293B" stroke="#0F172A" strokeWidth="2.5" />

          {/* Forearm Bent inward pointing left */}
          <path d="M196 175 L168 186" stroke="#334155" strokeWidth="15" strokeLinecap="round" />
          <path d="M196 175 L168 186" stroke="#E2E8F0" strokeWidth="10" strokeLinecap="round" />

          {/* Pointing Hand with extended index finger */}
          <g className="pointing-hand-svg" transform="translate(138, 172)">
            {/* Hand Glove */}
            <circle cx="20" cy="14" r="10" fill="url(#bodyWhite)" stroke="#0F172A" strokeWidth="3" />
            {/* Extended Pointing Finger */}
            <path
              d="M18 10 L0 10 C-3 10 -3 16 0 16 L18 16"
              fill="#94A3B8"
              stroke="#0F172A"
              strokeWidth="3"
              strokeLinejoin="round"
            />
            {/* Curled other fingers */}
            <ellipse cx="20" cy="18" rx="5" ry="4" fill="#64748B" stroke="#0F172A" strokeWidth="2" />
          </g>
        </g>

        {/* ================= NECK RINGS ================= */}
        <g className="robot-neck-group">
          <ellipse cx="150" cy="138" rx="16" ry="6" fill="#334155" stroke="#0F172A" strokeWidth="3" />
          <ellipse cx="150" cy="134" rx="14" ry="5" fill="#64748B" stroke="#0F172A" strokeWidth="2.5" />
          <ellipse cx="150" cy="130" rx="12" ry="4" fill="#94A3B8" stroke="#0F172A" strokeWidth="2" />
        </g>

        {/* ================= ROBOT HEAD ================= */}
        <g className="robot-head-group">
          {/* Side Ears */}
          <rect x="94" y="55" width="12" height="32" rx="6" fill="#475569" stroke="#0F172A" strokeWidth="3.5" />
          <rect x="194" y="55" width="12" height="32" rx="6" fill="#475569" stroke="#0F172A" strokeWidth="3.5" />

          {/* Outer Head Chassis (White Rounded TV Monitor) */}
          <rect
            x="100"
            y="28"
            width="100"
            height="90"
            rx="26"
            fill="url(#bodyWhite)"
            stroke="#0F172A"
            strokeWidth="5"
            strokeLinejoin="round"
          />

          {/* Top Red/Cyan Scanner Cap */}
          <g className="head-top-badge">
            <path
              d="M125 28 C125 18 175 18 175 28 Z"
              fill="url(#bodyWhite)"
              stroke="#0F172A"
              strokeWidth="4"
              strokeLinejoin="round"
            />
            <rect
              x="133"
              y="20"
              width="34"
              height="8"
              rx="4"
              fill="url(#redBadge)"
              stroke="#0F172A"
              strokeWidth="2.5"
            />
          </g>

          {/* Inner Dark Blue/Black Visor Screen */}
          <rect
            x="110"
            y="38"
            width="80"
            height="70"
            rx="18"
            fill="url(#screenBg)"
            stroke="#0F172A"
            strokeWidth="4"
          />

          {/* Screen Visor Glass Highlight */}
          <path
            d="M116 44 C116 44 145 42 165 48 C150 56 122 56 116 44 Z"
            fill="rgba(255, 255, 255, 0.18)"
          />

          {/* Animated Cyan Glowing Eyes */}
          <g className="screen-eyes" filter="url(#cyanGlow)">
            {/* Left Eye */}
            <ellipse className="bot-eye left" cx="132" cy="66" rx="7" ry="9" fill={eyeColor} />
            {/* Right Eye */}
            <ellipse className="bot-eye right" cx="168" cy="66" rx="7" ry="9" fill={eyeColor} />
          </g>

          {/* Animated Glowing Smile Mouth */}
          <path
            className="bot-smile"
            d="M138 84 Q150 96 162 84 Z"
            fill={eyeColor}
            filter="url(#cyanGlow)"
          />
        </g>
      </svg>
    </div>
  );
}
