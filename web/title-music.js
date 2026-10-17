/* E1M1's score comes from tools/music.py, just like the in-game MIDI.
   A small chiptune synth keeps the landing page independent of the game engine. */
(function () {
  var context, buffer, source, wanted = true, stopped = false;
  var toggle = document.getElementById('music');
  var score = fetch('title-score.json').then(function (r) {
    if (!r.ok) throw new Error('Music unavailable');
    return r.json();
  }).catch(function () { toggle.hidden = true; return null; });

  function label() {
    var playing = !!source && context.state === 'running';
    toggle.textContent = playing ? toggle.dataset.off : toggle.dataset.on;
    toggle.setAttribute('aria-pressed', String(playing));
  }

  function render(data) {
    var rate = 22050;
    var result = context.createBuffer(1, Math.ceil(data.duration * rate), rate);
    var out = result.getChannelData(0);
    var seed = 19;
    function noise() { seed = (seed * 16807) % 2147483647; return seed / 1073741824 - 1; }
    data.notes.forEach(function (note) {
      var start = Math.round(note[0] * rate), duration = note[1], ch = note[2], pitch = note[3];
      var tail = ch === 9 ? .22 : .025;
      var length = Math.floor((duration + tail) * rate);
      var frequency = 440 * Math.pow(2, (pitch - 69) / 12);
      var gain = note[4] / 127 * (ch === 1 ? .15 : ch === 9 ? .12 : ch === 2 ? .065 : .045);
      for (var i = 0; i < length && start + i < out.length; i++) {
        var t = i / rate, value, env;
        if (ch === 9) {
          var kick = pitch === 36, snare = pitch === 38;
          env = Math.exp(-t * (kick ? 22 : snare ? 20 : 48));
          value = kick ? Math.sin(2 * Math.PI * (48 * t + 3 * (1 - Math.exp(-t * 30)))) :
            snare ? noise() * .75 + Math.sin(t * 1100) * .25 : noise();
        } else {
          var phase = 2 * Math.PI * frequency * t;
          env = Math.min(1, t / .004) * Math.min(1, Math.max(0, (duration + tail - t) / tail));
          value = ch === 1 ? Math.sin(phase) + .25 * Math.sin(phase * 2) :
            ch === 2 ? Math.tanh(3 * Math.sin(phase)) :
            Math.tanh(2.5 * (Math.sin(phase) + .4 * Math.sin(phase * 2))) * Math.exp(-t * 2);
        }
        out[start + i] += gain * env * value;
      }
    });
    for (var i = 0; i < out.length; i++) out[i] = Math.tanh(out[i] * .8);
    return result;
  }

  function play() {
    if (!wanted || stopped) return;
    var Audio = window.AudioContext || window.webkitAudioContext;
    if (!Audio) { toggle.hidden = true; return; }
    if (!context) { context = new Audio(); context.onstatechange = label; }
    // Called synchronously from the click handler, before the score's promise.
    context.resume().catch(function () {});
    score.then(function (data) {
      if (!data || stopped || !wanted || source) return;
      if (!buffer) buffer = render(data);
      source = context.createBufferSource();
      source.buffer = buffer;
      source.loop = true;
      source.connect(context.destination);
      source.start();
      label();
    }).catch(function () { toggle.hidden = true; });
  }

  toggle.addEventListener('click', function () {
    if (source && context.state === 'running') {
      wanted = false; source.stop(); source.disconnect(); source = null; label();
    } else { wanted = true; play(); }
  });
  window.titleMusic = {
    play: play,
    stop: function () {
      stopped = true;
      if (source) { source.stop(); source.disconnect(); source = null; }
      if (context) context.close().catch(function () {});
      toggle.hidden = true;
    }
  };
  play();
})();
