function setCookie(cookieName, value, duration) {
	var expiration = "";
	
	if (duration) {
		var endTime = new Date();
		endTime.setTime(endTime.getTime()+(duration*24*3600*1000));
		expiration = "; expires=" + endTime.toGMTString();
	}

	document.cookie = cookieName + "=" + value + expiration + "; path=/";
}

function eraseCookie(cookieName) {
	setCookie(cookieName, '', -1);
}

function readCookie(cookieName) {
	var nameLookup = cookieName + "=";
	var cookies = document.cookie.split(";");

	for (var i=0; i < cookies.length; i++) {
		cookie = cookies[i];
		while (cookie.charAt(0)==' ') cookie = cookie.substring(1, cookie.length);
		if (cookie.indexOf(nameLookup) == 0) {
			return cookie.substring(nameLookup.length, cookie.length);
		}
	}

	return null;
}

