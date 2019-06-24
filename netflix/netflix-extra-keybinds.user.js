// ==UserScript==
// @name         netflix-extra-keybinds
// @version      1.0
// @description  netflix-extra-keybinds
// @author       siikamiika
// @match        https://www.netflix.com/watch/*
// @grant        none
// ==/UserScript==

let netflix = window.netflix;

class NetflixController {
    constructor() {
        // wait for init
        setTimeout(_ => {
            this.videoPlayer = netflix.appContext.state.playerApp.getAPI().videoPlayer;
            this.videoApi = this.videoPlayer.getVideoPlayerBySessionId(
                this.videoPlayer.getAllPlayerSessionIds());
            //alert(this.videoApi.getCurrentTime());
        }, 5000);
    }

    relativeSeek(millis) {
        let current = this.videoApi.getCurrentTime();
        this.videoApi.seek(current + millis);
    }

    pause() {
        this.videoApi.pause();
    }

    play() {
        this.videoApi.play();
    }
}

let netflixController = new NetflixController();

// key listeners
document.addEventListener('keydown', function(e) {
  if (e.key == 'z') {
      netflixController.relativeSeek(-2000);
  } else if (e.key == 'x') {
      netflixController.relativeSeek(2000);
  }
});

// other events
document.addEventListener('mouseout', function(e){
    netflixController.pause();
});
document.addEventListener('mouseover', function(e){
    netflixController.play();
});
