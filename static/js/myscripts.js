window.onload = function(){
	var loader = document.getElementById("loader");
	loader.style.opcaity=0;
	loader.style.display='none';

	var windowH= window.innerHeight;
	topValue = windowH - 100;
	var contentWrap = document.getElementsByClassName("content");
	contentWrap[0].style.top= topValue +'px';
	
	var page = window.location.toString();

	if((page.indexOf('register') !== -1)){
		var subButton2 = document.getElementById("subButton2");
		var uploadBtn = document.getElementById("fileBtnHide");
		subButton2.onclick = function () {
			uploadBtn.click();
		};

		var avatar = document.getElementById("fileBtnHide");
		avatar.onchange =function() {
			var file = avatar.files[0];
			if (file) {
				var fileSize = 0;
				fileSize = (Math.round(file.size * 100 / (1024 * 1024)) / 100).toString();
				alert(fileSize);
					
			
			}
		}


	};
	if((page.indexOf('editAccount') !== -1)){
		var subButton2 = document.getElementById("subButton2");
		var uploadBtn = document.getElementById("fileBtnHide");
		subButton2.onclick = function () {
			uploadBtn.click();
		};

		var avatar = document.getElementById("fileBtnHide");
		avatar.onchange =function() {
			var file = avatar.files[0];
			if (file) {
				var fileSize = 0;
				fileSize = (Math.round(file.size * 100 / (1024 * 1024)) / 100).toString();
				alert(fileSize);
					
			
			}
		}
	};



	var vid = document.getElementById("bgvid");
	var onOFF = document.getElementById("vidPauseVisable");

	onOFF.onclick = function () {
		if (vid.paused) {
			vid.play();
			onOFF.style.backgroundImage="url(static/images/pause.png)";
		} else {
				vid.pause();
				onOFF.style.backgroundImage="url(static/images/play.png)";
				}
	};

	var destiny = document.getElementsByClassName('content');
	var destinyY = destiny[0].offsetTop;
	
	if (navigator.userAgent.toLowerCase().indexOf('firefox') !== -1){
		scrollTo(document.documentElement, destinyY, 200);
	}else{
		scrollTo(document.body, destinyY, 200);
	}
};



function scrollTo(element, to, duration) {
	if (duration <= 0) return;
	var difference = to - element.scrollTop;
	var perTick = difference / duration * 2;
	setTimeout(function() {
		element.scrollTop = element.scrollTop + perTick;
		scrollTo(element, to, duration - 2);
	}, 10);
};
