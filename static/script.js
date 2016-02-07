/**
* World PLaylist © 2016
**/

var apiUrl = "http://localhost:8000/api/";
var youtubeLink = "https://www.youtube.com/watch?v=";
var seekToSeconds = 0;
var player;

/*
* -------------------------------------------
* music submission
* -------------------------------------------
*/
function submitMusic() {
  var link = $("#music-link-add").val();
  if (goodLink(link)) {
    var linkId = link.replace(youtubeLink, "").trim()
    getMusicInfos(linkId, function(data) {
      message = data.message
      status = data.status
      $("#music-link-add").val("");
      if (status === "ok") {
        swal("Thanks!", message, "success");
      } else {
        swal("Oops...", message, "error");
      }

    });
  } else {
    $("#music-link-add").val("");
    swal("Oops...", "The link seems not good", "error");
  }
}

function goodLink(link) {
  if (stringStartsWith(link, youtubeLink)) {
      return true
  } else {
    return false
  }
}

function stringStartsWith(string, prefix) {
    return string.slice(0, prefix.length) == prefix
}

function getMusicInfos(id, callback) {
  $.ajax({
    url: apiUrl + "musicinfo/" + id,
    type: "GET",
    success: function(data) {
       callback(data)
    }
  });
}

/*
*
* Playlist show
*
*/
function showPlaylist() {
  $.ajax({
    url: apiUrl + "showmusics",
    type: "GET",
    success: function(data){
       var d = data.data
       var html = "<ul>"
       for(var i=0; i<d.length; i++) {
         html += "<li>" + d[i].title + "</li>"
       }
       html += "</ul>"
       swal({
         title: "Next songs",
         text: html,
         imageUrl: "music.png",
         html: true
        });
    }
  });
}

/*
*
* Mute / Unmute
*
*/
function muteMode() {
  var mute = $("#muteit").prop("checked");
  if(mute) {
    player.mute()
  } else {
    player.unMute()
  }
}


/*
* -------------------------------------------
* playlist
* -------------------------------------------
*/
function seekToSecondsGet(callback) {
  $.ajax({
    url: apiUrl + "seektoseconds",
    type: "GET",
    success: function(data){
       callback(data)
    }
  });
}

function appendToPlaylist(boxId, title) {
  html = "<div class='music-info'>" +
            title +
        "</div>" +
        "<div id='" + boxId + "'></div>"
  return html
}

function onYouTubePlayerAPIReady() {
  $("#playlist-box").css("pointer-events", "auto");
  $.ajax({
    url: apiUrl + "musics",
    type: "GET",
    success: function(data) {
      var d = data.data
      var title = d.title
      var boxId = "player"
      var videoId = d.videoId
      $("#playlist-box").html(
        appendToPlaylist(boxId, title)
      );
      seekToSecondsGet(function(data) {
        seekToSeconds = data.data
        player = new YT.Player(boxId, {
            height: "90%",
            width: "100%",
            videoId: videoId,
            playerVars: {
              controls: 0,
              fs: 0,
              iv_load_policy: 3,
              rel: 0,
              showinfo: 0,
              modestbranding: 1,
              autohide: 1,
              cc_load_policy: 1,
              start: seekToSeconds
            },
            events: {
                "onReady": onPlayerReady,
                "onStateChange": onPlayerStateChange,
                "onError": onPlayerError
            }
        });// end of player
      }); //end seek
    } // end of sucess
  }); // end get data
}

function nextSong(player) {
  $("#playlist-box").css("pointer-events", "auto");
  $.ajax({
    url: apiUrl + "musics",
    type: "GET",
    success: function(data) {
      var d = data.data
      var title = d.title
      var videoId = d.videoId
      $(".music-info").html(title)
      seekToSecondsGet(function(data) {
        seekToSeconds = data.data
        player.loadVideoById(videoId, seekToSeconds)
        player.playVideo()
        $("#playlist-box").css("pointer-events", "none");
      }); //end seek
    } // end of sucess
  }); // end get data
}

function onPlayerReady(event) {
  event.target.playVideo();
  $("#playlist-box").css("pointer-events", "none");
}

function onPlayerStateChange(event) {
    if(event.data === 0) {
      setTimeout(function(){
          nextSong(player)
        }, 1000);
    }
 }

 function onPlayerError(e) {
   console.log(e)
 }
