
document.onreadystatechange = function (){
	var windowH= window.innerHeight;
	topValue = windowH - 100;
	var contentWrap = document.getElementsByClassName("content");
	contentWrap[0].style.top= topValue +'px';
	
	var page = window.location.toString();

	if((page.indexOf('register') > -1)){
		var subButton2 = document.getElementById("subButton2");
		subButton2.onclick = function () {
			var uploadBtn = document.getElementById("fileBtnHide");
			uploadBtn.click();
		};
	};

	if((page.indexOf('editAccount') > -1)){
		var subButton2 = document.getElementById("subButton2");
		subButton2.onclick = function () {
			var uploadBtn = document.getElementById("fileBtnHide");
			uploadBtn.click();
		};
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
	//alert('destiny:'+destiny+'//destinyY:'+destinyY);
	
	//ok for chrome, safari but not firefox
	scrollTo(document.body, destinyY, 200);

};

function scrollTo(element, to, duration) {
	if (duration <= 0) return;
	var difference = to - element.scrollY;
	var perTick = difference / duration * 2;
	setTimeout(function() {
		//ok safari,chome
		//element.scrollTop = element.scrollTop + perTick;
		element.scrollY = element.scrollY + perTick;
		alert(element.scrollY);
		scrollTo(element, to, duration - 2);
	}, 10);
};
