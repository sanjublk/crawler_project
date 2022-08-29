function fetchLyrics(e) {
  e.preventDefault();
//   e.target.removeEventListener("click", fetchLyrics);
//   e.target.addEventListener("click", () => e.preventDefault());
  let url = $(e.target).attr("href").replace("song", "lyrics");
  $.ajax({
    url: url,
    success: (data) => changeLyrics(data, e.target),
  });
}

function changeLyrics(data, target) {
  $(".songName").fadeOut("fast", function () {
    $(".songName").text(data.name).fadeIn();
  });
  $("#lyrics").fadeOut("fast", function () {
    $("#lyrics").html(data.lyrics.replaceAll("\n", "<br>")).fadeIn();
  });
  let parent = $(target).parent();
  $(parent).html(data.name);
  $("#current").html(
    `<a class="songList" href="/lyrics/${$("#current").attr("songId")}">${$(
      "#current"
    ).text()}</a>`
  );
  $("#current a").click((e) => {
    fetchLyrics(e);
  });
  $("#current").removeAttr("id");
  $(parent).attr({ songId: data.id, id: "current" });
  $(target).attr("disabled", false);
  changeButtons(data.next, data.previous);
}


function changeButtons(next, prev) {
  if (prev != null) {
    $("#previousSong").attr("href", `/song/${prev}`);
    $("#previousSong").parent().css("display", "block");
  } else {
    $("#previousSong").parent().css("display", "none");
  }

  if (next != null) {
    $("#nextSong").attr("href", `/song/${next}`);
    $("#nextSong").parent().css("display", "block");
  } else {
    $("#nextSong").parent().css("display", "none");
  }
}


function nextPrev(e, v) {
  console.log("meh");
  e.preventDefault();
  goToTop();
  let currentSongId = $("#current").attr("songId");
  let url = `/lyrics/${parseInt(currentSongId) + v}`;
  $.ajax({
    url: url,
    success: (data) => {
      $(".songName").text(data.name);
      $("#lyrics").html(data.lyrics.replaceAll("\n", "<br>"));

      $("#current").html(
        `<a class="songList" href="/lyrics/${$("#current").attr("songId")}">${$(
          "#current"
        ).text()}</a>`
      );
      $("#current a").click((e) => {
        fetchLyrics(e);
      });
      $("#current").removeAttr("id");
      Array.from($(".sidebar li")).forEach((element) => {
        if ($(element).attr("songId") == data.id) {
          $(element).html(data.name);
          $(element).attr({ songId: data.id, id: "current" });
        }
        changeButtons(data.next, data.previous);
      });
    },
  });
}


function goToTop() {
  window.scrollTo(0, 0);
}


function main() {
  let nextSong = (e) => nextPrev(e, 1);
  let previousSong = (e) => nextPrev(e, -1);
  let elements = document.getElementsByClassName("songList");
  Array.from(elements).forEach((element) =>
    element.addEventListener("click", fetchLyrics)
  );
  document
    .getElementById("previousSong")
    .addEventListener("click", previousSong);
  document.getElementById("nextSong").addEventListener("click", nextSong);
}

$(main);
