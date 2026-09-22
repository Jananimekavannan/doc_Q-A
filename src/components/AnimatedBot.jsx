import React from "react";

export default function AnimatedBot({ state = "idle", children }) {
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
    <div className={`robot-holding-wrapper ${state}`}>
      {/* 1. BOT TOP: Speech bubble + Head & Antenna */}
      <div className="bot-top-anchor">
        {/* Holographic Speech / Status Bubble */}
        <div className="bot-speech-bubble">
          <span className="bot-status-dot" />
          <span className="bot-status-text">{getStatusText()}</span>
        </div>

        {/* Robot Head */}
        <div className="bot-head-assembly">
          {/* Antenna */}
          <div className="bot-antenna">
            <div className="antenna-ball" />
            <div className="antenna-pulse" />
            <div className="antenna-rod" />
          </div>

          {/* Head & Face Visor */}
          <div className="bot-head">
            <div className="bot-ear left">
              <span className="ear-light" />
            </div>

            <div className="bot-face">
              <div className="visor-reflection" />
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
              <div className="bot-mouth">
                <span className="wave-bar b1" />
                <span className="wave-bar b2" />
                <span className="wave-bar b3" />
                <span className="wave-bar b4" />
                <span className="wave-bar b5" />
              </div>
            </div>

            <div className="bot-ear right">
              <span className="ear-light" />
            </div>
          </div>

          {/* Neck collar */}
          <div className="bot-neck">
            <span className="neck-joint" />
          </div>
        </div>
      </div>

      {/* 2. BOT SIDES: Arms & Hands gripping the card left & right */}
      <div className="bot-side-arm left-arm-grip">
        <div className="arm-shoulder" />
        <div className="arm-bicep" />
        <div className="arm-elbow" />
        <div className="arm-forearm" />
        <div className="grip-hand">
          <div className="hand-base" />
          <div className="grip-finger f1" />
          <div className="grip-finger f2" />
          <div className="grip-finger f3" />
          <div className="grip-thumb" />
          <span className="grip-glow" />
        </div>
      </div>

      <div className="bot-side-arm right-arm-grip">
        <div className="arm-shoulder" />
        <div className="arm-bicep" />
        <div className="arm-elbow" />
        <div className="arm-forearm" />
        <div className="grip-hand">
          <div className="hand-base" />
          <div className="grip-finger f1" />
          <div className="grip-finger f2" />
          <div className="grip-finger f3" />
          <div className="grip-thumb" />
          <span className="grip-glow" />
        </div>
      </div>

      {/* 3. CENTER BOX: The Q&A Content Card */}
      <div className="held-box-container">
        {children}
      </div>

      {/* 4. BOT BOTTOM: Legs & Hovering Thruster Boots */}
      <div className="bot-bottom-legs">
        {/* Left Leg */}
        <div className="bot-leg left-leg">
          <div className="leg-hip" />
          <div className="leg-thigh" />
          <div className="leg-knee" />
          <div className="leg-calf" />
          <div className="bot-foot">
            <div className="boot-chassis" />
            <div className="boot-sole" />
            <div className="thruster-plume" />
          </div>
        </div>

        {/* Center Pelvis Core */}
        <div className="bot-pelvis">
          <span className="pelvis-core" />
        </div>

        {/* Right Leg */}
        <div className="bot-leg right-leg">
          <div className="leg-hip" />
          <div className="leg-thigh" />
          <div className="leg-knee" />
          <div className="leg-calf" />
          <div className="bot-foot">
            <div className="boot-chassis" />
            <div className="boot-sole" />
            <div className="thruster-plume" />
          </div>
        </div>
      </div>
    </div>
  );
}
