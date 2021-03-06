window.onload = function(){
	//Hide loader
	var loader = document.getElementById("loader");
	loader.style.opcaity=0;
	loader.style.display='none';
	//Set content container height and position
	adaptContentPage();
	//Prepare forms if on editAccount or register page
	var page = window.location.toString();
	if((page.indexOf('register') !== -1) || (page.indexOf('editAccount') !== -1)) {
		prepareForms();
	}
	//use clcik instead of hover for ipad
	if(navigator.platform.indexOf('iPad') !== -1) {
		if((page.indexOf('friends') !== -1) || (page.indexOf('users') !== -1)) {
			alternativeHover();
		}
	}
	//Prepare BgVideo
	var vid = document.getElementById("bgvid");
	var onOFF = document.getElementById("vidPauseVisable");
	var message = document.getElementById("message");
	onOFF.onclick = function () {
		if (vid.paused) {
			vid.play();
			onOFF.style.backgroundImage="url(static/images/pause.svg)";
			message.style.opacity=0.5;
		}else{
				vid.pause();
				onOFF.style.backgroundImage="url(static/images/play.svg)";
				message.style.opacity=0;
		}
	};
	//Scroll to content start
	var destiny = document.getElementsByClassName('content');
	var destinyY = destiny[0].offsetTop;
	if (navigator.userAgent.toLowerCase().indexOf('firefox') !== -1){
		//firefox
		scrollTo(document.documentElement, destinyY, 200);
	}else{
		//rest of navigators
		scrollTo(document.body, destinyY, 200);
	}
};

window.onresize = adaptContentPage;

function adaptContentPage() {
	var windowH= window.innerHeight;
	var topValue = windowH - 100;
	var contentWrap = document.getElementsByClassName("content");
	contentWrap[0].style.top= topValue +'px';
}

function alternativeHover() {
	var userDivs = document.getElementsByClassName('contentUser');
	[].forEach.call(userDivs, function(e){
		e.onclick = function() {
			var target = e.getElementsByClassName('contentButtonWrap');
			e.style.backgroundSize='450px auto';
			e.style.outline='3px solid green';
			target[0].style.left=0;
	    };
	});
};

function prepareForms() {
	//Enable click of hidden file upload button
	var subButton2 = document.getElementById("subButton2");
	var uploadBtn = document.getElementById("fileBtnHide");
	subButton2.onclick = function () {
		uploadBtn.click();
	};
	//Limit file upload size to 1Mb to allow submission
	var avatar = document.getElementById("fileBtnHide");
	avatar.onchange =function() {
		var flash = document.getElementById('flashes');
		var submitBtn = document.getElementsByClassName('subButton');
		var file = avatar.files[0];
		if (file) {
			var fileSize = 0;
			fileSize = (Math.round(file.size * 100 / (1024 * 1024)) / 100).toString();
			if (fileSize >= 1.1 ){
				submitBtn[0].style.display='none';
				flash.innerHTML = '"Select an image under 1 MB"';
			}else{
				submitBtn[0].style.display='block';
				flash.innerHTML = '"Image loaded"';
			}
		}
	};
}

function scrollTo(element, to, duration) {
	if (duration <= 0) return;
	var difference = to - element.scrollTop;
	var perTick = difference / duration * 2;
	setTimeout(function() {
		element.scrollTop = element.scrollTop + perTick;
		scrollTo(element, to, duration - 2);
	}, 10);
};