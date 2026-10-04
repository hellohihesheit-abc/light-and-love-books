(function () {
  var tracks = [
    { id: "ylqjtkqpFPo", title: "The Quiet City" },
    { id: "WU6sYq5PmCM", title: "Until Morning" },
    { id: "2_xsl3n82sA", title: "First Light" },
    { id: "qq3kQMw8SLA", title: "Loved First" },
    { id: "hDKeYg1TmV0", title: "Morning Prayer" },
    { id: "SOpLQeRru4c", title: "Mercy" },
    { id: "SaAawJn7ixU", title: "Closer to God" },
    { id: "IYvMjxQZD04", title: "The Quiet Hour" },
    { id: "w_VbS2qXSDc", title: "Abide" },
    { id: "9nPuc_zcDxI", title: "After the Rain" },
    { id: "ECDp8uiOkZs", title: "After Midnight" },
    { id: "lzqdOl6Zqyc", title: "Autumn Light" }
  ];
  var day = Math.floor(Date.now() / 86400000);
  var index = day % tracks.length;
  var frame = document.getElementById("music-frame");
  var label = document.getElementById("music-now");
  var nextBtn = document.getElementById("music-next");
  if (!frame) return;

  function show(i, autoplay) {
    index = (i + tracks.length) % tracks.length;
    var t = tracks[index];
    var src = "https://www.youtube-nocookie.com/embed/" + t.id +
      "?autoplay=" + (autoplay ? "1" : "0") + "&rel=0&playsinline=1";
    frame.innerHTML = '<iframe src="' + src + '" title="' + t.title +
      '" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
    if (label) label.textContent = t.title;
  }

  show(index, true);
  if (nextBtn) nextBtn.addEventListener("click", function () { show(index + 1, true); });
})();
