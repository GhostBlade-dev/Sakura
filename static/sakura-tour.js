// Shepherd.js CDN loader
(function(){
  if (!window.Shepherd) {
    var shepherdCss = document.createElement('link');
    shepherdCss.rel = 'stylesheet';
    shepherdCss.href = 'https://cdn.jsdelivr.net/npm/shepherd.js@11.1.0/dist/css/shepherd.css';
    document.head.appendChild(shepherdCss);
    var shepherdScript = document.createElement('script');
    shepherdScript.src = 'https://cdn.jsdelivr.net/npm/shepherd.js@11.1.0/dist/js/shepherd.min.js';
    shepherdScript.onload = function() {
      window.dispatchEvent(new Event('shepherd:ready'));
    };
    document.head.appendChild(shepherdScript);
  } else {
    window.dispatchEvent(new Event('shepherd:ready'));
  }
})();

window.addEventListener('shepherd:ready', function() {
  if (localStorage.getItem('sakura_tour_seen')) return;

    // Add gentle chime audio element
    if (!document.getElementById('sakura-chime-audio')) {
      var audio = document.createElement('audio');
      audio.id = 'sakura-chime-audio';
  // Chime audio setup
  audio.src = '/static/chime.mp3.mp3';
      audio.preload = 'auto';
      document.body.appendChild(audio);
    }

    // Confetti burst function (simple sparkles)
    function sakuraConfetti() {
      for (let i = 0; i < 24; i++) {
        let sparkle = document.createElement('div');
        sparkle.className = 'sakura-confetti';
        sparkle.style.left = (50 + Math.random() * 40 - 20) + '%';
        sparkle.style.top = (48 + Math.random() * 8 - 4) + '%';
        sparkle.style.background = `radial-gradient(circle, #fff0fa 60%, #e07a9a 100%)`;
        sparkle.style.animationDelay = (Math.random() * 0.5) + 's';
        document.body.appendChild(sparkle);
        setTimeout(() => sparkle.remove(), 1800);
      }
    }

    // Inject magical, cozy Sakura tour styles
    if (!document.getElementById('sakura-tour-style')) {
      var style = document.createElement('style');
      style.id = 'sakura-tour-style';
      style.innerHTML = `
        @import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Fredoka:wght@500&family=Quicksand:wght@500&family=Comfortaa:wght@700&family=Indie+Flower&display=swap');
        .shepherd-element.sakura-tour {
          background: linear-gradient(135deg, #f8bbd0 60%, #e1bee7 100%) !important;
          border-radius: 32px !important;
          box-shadow: 0 4px 24px 0 #f8bbd088, 0 0 0 6px #e1bee722 !important;
          border: none !important;
          font-family: 'Comfortaa', 'Indie Flower', 'Pacifico', 'Fredoka', 'Quicksand', 'Comic Sans MS', 'Segoe UI', cursive, sans-serif !important;
          color: #7c3daf !important;
          padding: 18px 40px !important;
          animation: sakura-tour-pop 0.7s cubic-bezier(.4,2,.6,1);
          position: relative;
          z-index: 10001;
        }
        /* Chat bubble tail, matching recordBtn style */
        .shepherd-element.sakura-tour::before {
          content: '';
          position: absolute;
          left: 54px;
          bottom: -22px;
          width: 32px;
          height: 32px;
          background: linear-gradient(135deg, #f8bbd0 60%, #e1bee7 100%);
          border-bottom-left-radius: 32px 32px;
          box-shadow: 0 4px 12px #e1bee744;
          transform: rotate(10deg);
          z-index: 2;
        }
        .shepherd-element.sakura-tour .shepherd-title {
          font-family: 'Pacifico', 'Indie Flower', 'Comfortaa', 'Fredoka', 'Quicksand', 'Comic Sans MS', 'Segoe UI', cursive, sans-serif !important;
          color: #e07a9a !important;
          font-size: 1.5em !important;
          margin-bottom: 10px !important;
          letter-spacing: 0.01em;
          text-shadow: 0 1px 0 #fff6fa, 0 0 8px #ffe6fa88;
        }
        .shepherd-element.sakura-tour .shepherd-text {
          font-size: 1.13em !important;
          color: #a14e7a !important;
          margin-bottom: 14px !important;
          font-family: 'Comfortaa', 'Quicksand', 'Fredoka', 'Comic Sans MS', 'Segoe UI', cursive, sans-serif !important;
        }
        /* Animated magical outline */
        .shepherd-element.sakura-tour::after {
          content: '';
          position: absolute;
          top: -2px; left: -2px; right: -2px; bottom: -2px;
          border-radius: 36px 36px 24px 60px/36px 36px 36px 60px;
          pointer-events: none;
          z-index: 0;
          border: 2px solid transparent;
          background: linear-gradient(120deg, #f8bbd0 40%, #e0f7fa 60%, #fff0fa 100%) border-box;
          box-shadow: 0 0 12px 2px #f8bbd088;
          animation: sakura-outline-glow 2.2s linear infinite;
        }
        .shepherd-element.sakura-tour .sakura-tour-sparkle {
          position: absolute;
          pointer-events: none;
          z-index: 1;
          font-size: 1.7em;
          opacity: 0.7;
          animation: sakura-tour-sparkle 1.7s infinite alternate;
        }
        /* Add a white, semi-transparent background to the content for readability */
        .shepherd-element.sakura-tour .shepherd-content {
          background: rgba(255,255,255,0.92);
          border-radius: 28px;
          padding: 8px 12px 8px 12px;
          position: relative;
          z-index: 2;
        }
        @keyframes sakura-outline-glow {
          0% { box-shadow: 0 0 12px 2px #f8bbd088; }
          50% { box-shadow: 0 0 20px 6px #e07a9a44; }
          100% { box-shadow: 0 0 12px 2px #f8bbd088; }
        }
        /* Sparkle effect */
        .shepherd-element.sakura-tour .sakura-tour-sparkle {
          position: absolute;
          pointer-events: none;
          z-index: 10003;
          font-size: 1.7em;
          opacity: 0.7;
          animation: sakura-tour-sparkle 1.7s infinite alternate;
        }
        .shepherd-element.sakura-tour .sakura-tour-sparkle.s1 { top: 10px; left: 24px; animation-delay: 0s; }
        .shepherd-element.sakura-tour .sakura-tour-sparkle.s2 { top: 18px; right: 32px; animation-delay: 0.7s; }
        .shepherd-element.sakura-tour .sakura-tour-sparkle.s3 { bottom: 18px; left: 32px; animation-delay: 1.1s; }
        .shepherd-element.sakura-tour .sakura-tour-sparkle.s4 { bottom: 10px; right: 24px; animation-delay: 0.3s; }
        @keyframes sakura-tour-sparkle {
          0% { opacity: 0.5; transform: scale(1) rotate(0deg); }
          50% { opacity: 1; transform: scale(1.2) rotate(10deg); }
          100% { opacity: 0.5; transform: scale(1) rotate(0deg); }
        }
        /* ...existing code... */
        .shepherd-element.sakura-tour .shepherd-footer {
          display: flex;
          justify-content: flex-end;
          gap: 12px;
        }
        .shepherd-element.sakura-tour .shepherd-button {
          background: linear-gradient(90deg, #fff0fa 0%, #e0f7fa 100%) !important;
          color: #a14e7a !important;
          border-radius: 16px !important;
          font-family: 'Fredoka', 'Quicksand', 'Comic Sans MS', 'Segoe UI', cursive, sans-serif !important;
          font-weight: 700;
          font-size: 1.08em;
          border: none !important;
          box-shadow: 0 2px 8px #e07a9a22;
          padding: 8px 22px !important;
          margin: 0 2px;
          cursor: pointer;
          transition: background 0.3s, transform 0.2s;
        }
        .shepherd-element.sakura-tour .shepherd-button:hover {
          background: linear-gradient(90deg, #e0f7fa 0%, #fff0fa 100%) !important;
          color: #e07a9a !important;
          transform: scale(1.07);
        }
        .shepherd-element.sakura-tour .shepherd-cancel-icon {
          color: #e07a9a !important;
          background: #fff0fa !important;
          border-radius: 50%;
          box-shadow: 0 2px 8px #e07a9a22;
        }
        .shepherd-element.sakura-tour::before {
          content: '✨';
          position: absolute;
          top: 12px; left: 18px;
          font-size: 1.5em;
          opacity: 0.7;
          pointer-events: none;
          animation: sakura-tour-sparkle 1.7s infinite alternate;
        }
        .sakura-confetti {
          position: fixed;
          width: 14px; height: 14px;
          border-radius: 50%;
          pointer-events: none;
          z-index: 99999;
          opacity: 0.85;
          animation: sakura-confetti-fall 1.6s cubic-bezier(.4,2,.6,1) forwards;
        }
        @keyframes sakura-confetti-fall {
          0% { transform: scale(0.7) translateY(0) rotate(0deg); opacity: 0.9; }
          60% { transform: scale(1.1) translateY(-18px) rotate(20deg); opacity: 1; }
          100% { transform: scale(0.8) translateY(60px) rotate(60deg); opacity: 0; }
        }
        @keyframes sakura-tour-pop {
          0% { transform: scale(0.92); opacity: 0; }
          60% { transform: scale(1.08); opacity: 1; }
          100% { transform: scale(1); opacity: 1; }
        }
        @keyframes sakura-tour-sparkle {
          0% { opacity: 0.5; }
          50% { opacity: 1; }
          100% { opacity: 0.5; }
        }
      `;
      document.head.appendChild(style);
    }

    var tour = new Shepherd.Tour({
      defaultStepOptions: {
        classes: 'sakura-tour',
        scrollTo: true,
        cancelIcon: { enabled: true },
        canClickTarget: false
      }
    });

    // Only play chime after user interaction (click/tap)
    let sakuraChimeAllowed = false;
    function allowSakuraChime() { sakuraChimeAllowed = true; window.removeEventListener('pointerdown', allowSakuraChime); }
    window.addEventListener('pointerdown', allowSakuraChime);
    tour.on('show', function() {
      // Add sparkles to the popup
      setTimeout(function() {
        var popup = document.querySelector('.shepherd-element.sakura-tour');
        if (popup && !popup.querySelector('.sakura-tour-sparkle')) {
          const sparkles = [
            {cls: 's1', char: '✨'},
            {cls: 's2', char: '❄️'},
            {cls: 's3', char: '🌸'},
            {cls: 's4', char: '💫'}
          ];
          sparkles.forEach(s => {
            let el = document.createElement('span');
            el.className = 'sakura-tour-sparkle ' + s.cls;
            el.textContent = s.char;
            popup.appendChild(el);
          });
        }
      }, 10);
      var audio = document.getElementById('sakura-chime-audio');
      if (audio && sakuraChimeAllowed) {
        audio.currentTime = 0;
        audio.volume = 0.22;
        audio.play().catch(()=>{});
      }
    });
    tour.addStep({
      title: '🌸 Welcome to Sakura! ✨',
      text: 'Sakura is your <b>magical, cozy</b> voice agent.<br>Let me show you around with a sprinkle of magic!',
      buttons: [
        { text: 'Next ✨', action: tour.next }
      ]
    });
    tour.addStep({
      title: '🔑 Add API Keys',
      text: 'Click this <b>key button</b> <span style="color:#e07a9a;">under Sakura\'s avatar</span> to add your API keys for <b>Gemini, AssemblyAI, Murf, WeatherAPI, and Tavily</b>.',
      attachTo: { element: '#showApiKeyDialog', on: 'bottom' },
      buttons: [
        { text: 'Next ✨', action: tour.next }
      ]
    });
    tour.addStep({
      title: '🎤 Talk to Sakura',
      text: 'Press the <b>Start Recording</b> button and ask Sakura anything!<br>She can answer with <span style="color:#e07a9a;">real-time weather, search, prices, news</span>, and more.',
      attachTo: { element: '#recordBtn', on: 'bottom' },
      buttons: [
        { text: 'Next ✨', action: tour.next }
      ]
    });
    tour.addStep({
      title: '🪄 Special Skills',
      text: 'Try asking about the <b>weather, news, or anything current</b>.<br>Sakura <b>always</b> uses <span style="color:#e07a9a;">real-time info</span> for you! ✨',
      attachTo: { element: '.chat-history', on: 'top' },
      buttons: [
        { text: 'Next ✨', action: tour.next }
      ]
    });
    tour.addStep({
      title: '💖 Powered by Murf',
      text: 'Click the <b>Powered by Murf</b> badge for more info about <span style="color:#e07a9a;">Murf AI voices</span>.<br><span style="font-size:1.1em;">Murf makes Sakura\'s magical voice possible!</span>',
      attachTo: { element: '#murf-badge, #murf-branding', on: 'top' },
      buttons: [
        { text: 'Finish 🌸', action: function() {
            tour.complete();
            localStorage.setItem('sakura_tour_seen','1');
            sakuraConfetti();
        } }
      ]
    });
    tour.start();
  });
