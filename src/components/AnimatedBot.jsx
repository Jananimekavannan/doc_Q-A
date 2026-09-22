import React from "react";

export default function AnimatedBot({ state = "idle" }) {
  // state: 'idle' | 'uploading' | 'thinking' | 'answered'

  const getStatusText = () => {
    switch (state) {
      case "uploading":
        return "Scanning & indexing document...";
      case "thinking":
        return "Analyzing context & reasoning...";
      case "answered":
        return "Answer retrieved from document!";
      default:
        return "Awaiting your document & questions";
    }
  };

  return (
    <div className={`bot-container ${state}`}>
      {/* Hologram Speech / Status Badge */}
      <div className="bot-speech-bubble">
        <span className="bot-status-dot" />
        <span className="bot-status-text">{getStatusText()}</span>
      </div>

      {/* Main Floating Robot Body */}
      <div className="bot-avatar">
        {/* Antenna */}
        <div className="bot-antenna">
          <div className="antenna-rod" />
          <div className="antenna-ball" />
          <div className="antenna-pulse" />
        </div>

        {/* Head chassis */}
        <div className="bot-head">
          {/* Left Ear Sensor */}
          <div className="bot-ear left">
            <span className="ear-light" />
          </div>

          {/* Face / LED Visor Screen */}
          <div className="bot-face">
            <div className="visor-reflection" />

            {/* Eyes */}
            <div className="bot-eyes">
              <div className="eye left">
                <span className="eye-pupil" />
                <span className="eye-shine" />
              </div>
              <div className="eye right">
                <span className="eye-pupil" />
                <span className="eye-shine" />
              </div>
            </div>

            {/* Digital Mouth / Sound Wave */}
            <div className="bot-mouth">
              <span className="wave-bar b1" />
              <span className="wave-bar b2" />
              <span className="wave-bar b3" />
              <span className="wave-bar b4" />
              <span className="wave-bar b5" />
            </div>
          </div>

          {/* Right Ear Sensor */}
          <div className="bot-ear right">
            <span className="ear-light" />
          </div>
        </div>

        {/* Neck / Collar */}
        <div className="bot-neck">
          <span className="neck-joint" />
        </div>

        {/* Body & Chest Core */}
        <div className="bot-torso">
          <div className="chest-plate">
            <div className="chest-core" />
          </div>
        </div>
      </div>

      {/* Robot Arms Holding the Card */}
      <div className="bot-arms-wrapper">
        {/* Left Arm & Gripping Hand */}
        <div className="bot-arm left-arm">
          <div className="shoulder-joint" />
          <div className="upper-arm" />
          <div className="elbow-joint" />
          <div className="forearm" />
          <div className="bot-hand left-hand">
            <div className="finger f-thumb" />
            <div className="finger f-index" />
            <div className="finger f-middle" />
            <div className="palm-glow" />
          </div>
        </div>

        {/* Right Arm & Gripping Hand */}
        <div className="bot-arm right-arm">
          <div className="shoulder-joint" />
          <div className="upper-arm" />
          <div className="elbow-joint" />
          <div className="forearm" />
          <div className="bot-hand right-hand">
            <div className="finger f-thumb" />
            <div className="finger f-index" />
            <div className="finger f-middle" />
            <div className="palm-glow" />
          </div>
        </div>
      </div>
    </div>
  );
}
