var _language = $("html").attr("lang");
var noteupParags;
var noteupCounts;

/* The initialization function, where everything gets set */
function init() {
	languageManagement();
}

function removeLanguageChoice() {
	eraseCookie('canliiLanguage');
}

function languageManagement() {
	var rootPath = "/";
	var language = readCookie('canliiLanguage');

	if (language != null) {
		setCookie('canliiLanguage', language, 30);

		if (location.pathname == rootPath) {
			window.location.replace(rootPath + language + "/");
		}
	}
}

function checkChoice(language) {
	var theChoice = getObj('rememberLanguage');

	if (theChoice.checked) {
		setCookie('canliiLanguage', language, 30);
	}
}

//This function simply gets the element which has the id "objName"
//Made to work with the most popular browsers.
function getObj(objName) {
	var element;
	if (document.getElementById) {
		element = document.getElementById(objName);//Mozilla et IE
	} else if (document.all) {
		element = document.all[objName]; //IE
	} else if (document.layers) {
		element = document.layers[objName];
	}

	return element;
}

function show(obj, visibility) {
	var theDiv = getObj(obj);

	if (visibility == 'visible') {
		theDiv.style.visibility = visibility;
	} else {
		theDiv.style.display = visibility;
	}
}

function hide(obj, visibility) {
	var theDiv = getObj(obj);

	if (visibility == 'hidden') {
		theDiv.style.visibility = visibility;
	} else {
		theDiv.style.display = 'none';
	}
}

function changeDoctrinePeriodicalSort(element) {
	if (element.className === "link") {
		var elementToEnable;
		if (element.id === "titlePeriodicalSort") {
			elementToEnable = document.getElementById("publisherPeriodicalSort");
			document.getElementById("titleSortedPublications").style.display = "inline";
			document.getElementById("publisherSortedPublications").style.display = "none";
		} else {
			elementToEnable = document.getElementById("titlePeriodicalSort");
			document.getElementById("titleSortedPublications").style.display = "none";
			document.getElementById("publisherSortedPublications").style.display = "inline";
		}
		
		elementToEnable.className = "link";
		element.className = "";
	}
}

function changeFormAction(obj) {
	// This function is made to be called from the SUBMIT button of a FORM
	// Furthermore, this function is made for FORMs which have a SELECT object as its first form element
	// So we first need the Form object of the submit button
	var theForm = obj.form;

	// Then we need the first element, which is the SELECT object
	var selectOption = obj.elements[0];

	// Then, the index of the OPTION selected
	var optionIndex = selectOption.selectedIndex;

	// Finaly, the ACTION attribute of the FORM is set to the value of the selected object
	obj.action=selectOption.options[optionIndex].value;

	return true;
}

function toggleDensity(event) {
	event.preventDefault();
	
	var closestLi = $(event.currentTarget).closest("li");
	
	if (closestLi.hasClass("compact")) {
		closestLi.removeClass("compact");
		closestLi.addClass("full");
	} else {
		closestLi.removeClass("full");
		closestLi.addClass("compact");
	}
}

function expandDensity(event) {
	event.preventDefault();
	
	$("li.result").removeClass("compact");
	$("li.result").removeClass("full");
	
	$(event.currentTarget).closest("div").prev().find("span.compactWrapper").addClass("d-none");
	$(event.currentTarget).closest("div").prev().find("span.expandWrapper").removeClass("d-none");
}

function compactDensity(event) {
	event.preventDefault();
	
	$("li.result").addClass("compact");
	$("li.result").removeClass("full");
	
	$(event.currentTarget).closest("div").prev().find("span.expandWrapper").addClass("d-none");
	$(event.currentTarget).closest("div").prev().find("span.compactWrapper").removeClass("d-none");
}

function truncateString(str, num) {
	if (str.length > num) {
		return str.slice(0, num) + "...";
	} else {
		return str;
	}
}

/* For the comments to validate the feedback form */
function validateFeedback(form) {
	var theForm = form;
	var language = theForm['language'].value;
	var message = theForm['message'].value;

	if (message.replace(/\s/g, '') == '' || message.replace(/\s/g, '') == 'null') {
		if (language == 'en') {
			alert("Please enter a message before submitting your request.");
		} else {
			alert("S'il-vous-plaît, veuillez entrer un message avant de soumettre votre requête.");
		}
		return false;
	}

	theForm.submit();
	return true;
}

function getLanguage() {
	var pathname = window.location.pathname;

	if (pathname.indexOf("/fr/") != -1) {
		return "fr";
	} else {
		return "en";
	}
}

function submitNoteup(lang, originUrl, nquery) {
	var specificSectionSelected = $("#specificNoteup").prop("checked");
	var section = $("#sectionInput").val();
	var sectionPart = "";
	var reSectionSubsection = /^([\.\w]+)\s?\(\s?([\.\w]+)\s?\)$/;
	if (specificSectionSelected && section != null && section !== '') {
		var matches = reSectionSubsection.exec(section);
		if(matches != null && matches[1] != null && matches[1] !== '' && matches[2] != null && matches[2] !== ''){
			sectionPart = "&section1=" + matches[1] + "-" + matches[2];
		}else {
			sectionPart = "&section1=" + section;
		}
	}
	
	window.location.assign("/" + lang + "/#search/origin1=" + originUrl + sectionPart + "&nquery1=" + encodeURIComponent(nquery) + "&linkedNoteup=");
}

function copyStringToClipboard(textToCopy) {
	var el = document.createElement('textarea');
	el.value = textToCopy;
	// Set non-editable to avoid focus and move outside of view
	el.setAttribute('readonly', '');
	el.style.position = 'fixed';
	el.style.bottom = 0;
	el.style.left = 0;
	document.body.appendChild(el);
	el.select();
	document.execCommand('copy');
	document.body.removeChild(el);
}

function getCopiedSourceMsg(lang) {
    if (lang === "en") {
        return "Citation copied to your clipboard";
    } else {
        return "Référence copié dans le presse-papiers";
    }
}

function getCopiedLinkMsg(lang) {
    if (lang === "en") {
        return "Link copied to your clipboard";
    } else {
        return "Lien copié dans le presse-papiers";
    }
}

/*** NAVIGATION ITEMS FILTERING ***/

function generateListRows(containerSelector, countSelector, displayedResults, generateRowFunction) {
	var frag = document.createDocumentFragment();
	for (var i = 0; i < displayedResults.length; i++) {
    	if (i < maxDisplay) {
      		var item = displayedResults[i],
          	row = generateRowFunction(item);
      		frag.appendChild(row);
    	} else {
    		break;
    	}
  	}
  	
  	var containerElement = document.querySelector(containerSelector);
  	containerElement.innerHTML = "";
	containerElement.appendChild(frag);
	generateCountMessage(countSelector, displayedResults);
}

function filterListRows(containerSelector, countSelector, allResults, displayedResults, textMatchFunction) {
	displayedResults = allResults.filter(textMatchFunction);
	generateListRows(containerSelector, countSelector, displayedResults, generateRow);
	
	// determine if we need to display the show more link
	if (displayedResults.length <= maxDisplay) {
		$("span.showMoreResults").hide();
	} else {
		$("span.showMoreResults").show();
	}
}

function generateCountMessage(countSelector, displayedResults) {
	var msg = "";
    var matches = displayedResults.length;
    
    var showingMsg = (getLanguage() == "fr") ? "Affichage de " : "Showing ";
    var ofMsg = (getLanguage() == "fr") ? " sur " : " of ";
    switch (true) {
		case (matches === 0):
	    	msg = (getLanguage() == "fr") ? "Aucun résultats" : "No results";
	      	break;
	    case (matches === 1):
	    	msg = showingMsg + (getLanguage() == "fr") ? "1 résultat" : "1 result";
	      	break;
	    case (matches <= maxDisplay):
	    	msg = showingMsg + displayedResults.length + ((getLanguage() == "fr") ? " résultats" : " results");
	      	break;
	    default:
	    	msg = showingMsg + maxDisplay + ofMsg + matches + ((getLanguage() == "fr") ? " résultats" : " results");
	}
	
	document.querySelector(countSelector).textContent = msg;
}

function normalizeString(toNormalize) {
	// IE11 does not support normalize
	if (String.prototype.normalize != undefined) {
		return toNormalize.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, "");
	}
	
	return toNormalize.toLowerCase();
}

/*** END NAVIGATION ITEMS FILTERING ***/


/*******************************************************************************
 * browser detection for tools page
 ******************************************************************************/
var BrowserDetect = {
init: function () {
this.browser = this.searchString(this.dataBrowser) || null;
this.version = this.searchVersion(navigator.userAgent)
	|| this.searchVersion(navigator.appVersion)
	|| null;
this.OS = this.searchString(this.dataOS) || null;
},
searchString: function (data) {
for (var i=0;i<data.length;i++)	{
	var dataString = data[i].string;
	var dataProp = data[i].prop;
	this.versionSearchString = data[i].versionSearch || data[i].identity;
	if (dataString) {
		if (dataString.indexOf(data[i].subString) != -1)
			return data[i].identity;
	}
	else if (dataProp)
		return data[i].identity;
}
},
searchVersion: function (dataString) {
var index = dataString.indexOf(this.versionSearchString);
if (index == -1) return;
return parseFloat(dataString.substring(index+this.versionSearchString.length+1));
},
dataBrowser: [
{
	string: navigator.userAgent,
	subString: "Chrome",
	identity: "Chrome"
},
{
	string: navigator.vendor,
	subString: "Apple",
	identity: "Safari",
	versionSearch: "Version"
},
{
	string: navigator.userAgent,
	subString: "Firefox",
	identity: "Firefox"
},
{
	string: navigator.userAgent,
	subString: "MSIE",
	identity: "Internet Explorer",
	versionSearch: "MSIE"
}
],
dataOS : [
{
	string: navigator.platform,
	subString: "Win",
	identity: "Windows"
},
{
	string: navigator.platform,
	subString: "Mac",
	identity: "Mac"
},
{
	   string: navigator.userAgent,
	   subString: "iPhone",
	   identity: "iPhone/iPod"
},
{
	string: navigator.platform,
	subString: "Linux",
	identity: "Linux"
}
]

};
BrowserDetect.init();
/* ********************************************
******************************************** */

/* ********************************************
reflex web service loading
******************************************** */
var interval;
var randomlyGeneratedHash;
var status;

function getRandomHash() {
	return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
}

function updateReflexStatus() {
	$.get("/reflex-ws-simple-interface/reflexStatus.do?hash=" + randomlyGeneratedHash, function(data) {
		if (interval != undefined && data == 'done') {
			clearInterval(interval);
			resetUI();
		}
	});
}

function updateUI() {
	document.getElementById('errorMessage').innerHTML = '';
	document.getElementById('lockPane').className = 'lockOn';

	randomlyGeneratedHash = getRandomHash();
	document.forms['documentToReflexForm'].generatedHash.value = randomlyGeneratedHash;
	interval = setInterval(updateReflexStatus, 500);
}

function resetUI() {
	document.getElementById('lockPane').className = 'lockOff';
}
/* ********************************************
******************************************** */

/*** JUDGMENTS ***/

function selectText(startElement, endElement) {
	var range;

	if (window.getSelection) { //all browsers and ie9+
		range = document.createRange();
		range.setStartBefore(startElement);
		range.setEndBefore(endElement);
		
		let newDiv = document.createElement("DIV");
		newDiv.id = "toremove";
		let bodyNode = document.getElementsByTagName("BODY")[0];
		bodyNode.appendChild(newDiv);
		
		let rangeCopyNodes = range.cloneContents(true).childNodes;
		for (let i = 0; i < rangeCopyNodes.length; i++) {
			let rangeCopyNode = rangeCopyNodes[i].cloneNode(true);
			if (rangeCopyNode.nodeType == 1) { // element node
				let nodeToRemove = rangeCopyNode.querySelector(".unselectable");
				if (nodeToRemove != undefined) {
					nodeToRemove.parentNode.removeChild(nodeToRemove); // ie support
				}
			}
			
			newDiv.appendChild(rangeCopyNode);
		}
		
		let newRange = document.createRange();
		newRange.setStartBefore(newDiv);
		newRange.setEndAfter(newDiv);
		
		var selection = window.getSelection();
		selection.removeAllRanges();
		selection.addRange(newRange);
		document.execCommand("copy");
		selection.removeAllRanges();
		
		newDiv.parentNode.removeChild(newDiv); // ie support
	}
}

function getHtmlContent(startElement, endElement) {
	var range;

	let htmlContent = "";
	if (window.getSelection) { //all browsers and ie9+
		range = document.createRange();
		range.setStartBefore(startElement);
		
		if (endElement.tagName == "FOOTER") {
			// we may miss some information at the end if there is more than one <p> in the last paragraph, but
			// otherwise the outerHTML returns a big chunk of the document that is invalid
			range.setEndAfter(startElement);
		} else {
			range.setEndBefore(endElement);
		}
		
		let rangeCopyNodes = range.cloneContents(true).childNodes;
		for (let i = 0; i < rangeCopyNodes.length; i++) {
			let rangeCopyNode = rangeCopyNodes[i];
			if (rangeCopyNode.nodeType == 1) { // element node
				let nodeToRemove = rangeCopyNode.querySelector(".unselectable");
				if (nodeToRemove != undefined) {
					nodeToRemove.parentNode.removeChild(nodeToRemove); // ie support
				}
				
				htmlContent += rangeCopyNode.outerHTML;
			} else if (rangeCopyNode.nodeType == 3) { // text node
				htmlContent += rangeCopyNode.textContent;
			}
		}
	}
	
	return htmlContent;
}

function copyWithoutViibesMarkers() {
	if (window.getSelection) { //all browsers and ie9+
		let selectionToCopy = window.getSelection();
		let rangeToCopy = selectionToCopy.getRangeAt(0);
		
		let newDiv = document.createElement("DIV");
		newDiv.id = "toremove";
		let bodyNode = document.getElementsByTagName("BODY")[0];
		bodyNode.appendChild(newDiv);
		
		let rangeCopyNodes = rangeToCopy.cloneContents().childNodes;
		for (let i = 0; i < rangeCopyNodes.length; i++) {
			let rangeCopyNode = rangeCopyNodes[i].cloneNode(true);
			if (rangeCopyNode.nodeType == 1) { // element node
				let nodeToRemove = rangeCopyNode.querySelector(".unselectable");
				if (nodeToRemove != undefined) {
					nodeToRemove.parentNode.removeChild(nodeToRemove); // ie support
				}
			}
			
			newDiv.appendChild(rangeCopyNode);
		}
		
		let newRange = document.createRange();
		newRange.setStartBefore(newDiv);
		newRange.setEndAfter(newDiv);
		
		selectionToCopy.removeAllRanges();
		selectionToCopy.addRange(newRange);
		
		window.setTimeout(function () {
			selectionToCopy.removeAllRanges();
			newDiv.parentNode.removeChild(newDiv); // ie support
	    }, 100);
	}
}

function recreateAllScrollMarkerTips(forLegislations) {
	if (noteupParags != undefined && noteupParags != null) {
		Tipped.remove('div.scroll-marker span');
		
		// recreate markers in chunks, so the interface is unaffected while loading big documents, like the code civil
		let chunkSize = 50;
		let timeout = 50;
		let itemIndex = 0;
		(function() {
			let remainingDataLength = (noteupParags.length - itemIndex);
		    let currentChunkSize = (remainingDataLength >= chunkSize) ? chunkSize : remainingDataLength;
		    
		    if(itemIndex < noteupParags.length) {
		    	while(currentChunkSize--) {
					let paragStartElement = document.querySelector("[data-viibes-parag='" + noteupParags[itemIndex] + "']");
					if (paragStartElement != null) {
						let paragEndElement = document.querySelector('[data-viibes-end="' + paragStartElement.dataset['viibesStart'] + '"]');
					    if (paragEndElement == null) {
					    	paragEndElement = $("footer.bootstrap")[0];
					    }
		
						let markerElement = document.querySelector("[data-scroll-parag='" + noteupParags[itemIndex] + "']");
						if (markerElement != null) {
							createScrollMarkerTip(_language, paragStartElement, markerElement, paragEndElement, noteupCounts[itemIndex], forLegislations);
						}
					}
					itemIndex++;
		      	}
		      	setTimeout(arguments.callee, timeout);
		    }
		})();
	}
}

function createScrollMarkerTip(lang, paragStart, markerElement, paragEnd, noteupCount, forLegislations) {
	Tipped.create(
			$(markerElement), 
			"<div class='bootstrap'><b>" + getParagraphMsg(lang, forLegislations) + " " + getParagDisplay(paragStart.dataset['viibesParag'], forLegislations) + ", " + getCitingDocumentsMsg(lang) + " (" + noteupCount + ")</b></div><br/><div class='documentcontent canliidocumentcontent markerTip'>" + truncate(getHtmlContent(paragStart, paragEnd), 1500) + "</div>", 
			{	maxWidth: 800,
				position: 'left',
				cache: false
			});
}

function getParagDisplay(paragNum, forLegislations) {
	let newParagNum = paragNum
	if (forLegislations != undefined && forLegislations == true) {
		let section = null;
		let subsection = null;
		if (paragNum.indexOf("-") >= 0) {
			let splittedSection = paragNum.split("-");
			section = splittedSection[0];
			subsection = splittedSection[1];
			
			newParagNum = section + "(" + subsection + ")";
		}
	}
	
	return newParagNum;
}

function kFormatter(num) {
	let absNum = Math.abs(num);
	if (absNum > 9999) {
		return sign(num)*((absNum/1000).toFixed(0)) + 'k';
	} else if (absNum > 999) {
		return sign(num)*((absNum/1000).toFixed(1)) + 'k';
	}
	
	return sign(num)*absNum;
}

function getParagraphMsg(lang, forLegislations) {
    if (lang === "en") {
		return (forLegislations != undefined && forLegislations == true) ? "Section" : "Paragraph";
    } else {
        return (forLegislations != undefined && forLegislations == true) ? "Article" : "Paragraphe";
    }
}

function getCitingDocumentsMsg(lang) {
    if (lang === "en") {
        return "Citing documents";
    } else {
        return "Documents citants";
    }
}

function setReflexRecordNoteupCountText(lang, citedByPrefix, singleDocument, multipleDocuments) {
	var base = "/" + lang + "/search/multiNoteUpCount.do";
	
	var i = 0;
	var queryString = "";
	$("a[data-link-noteup-count]").each(function() {
		var documentPath = $(this).attr("data-link-noteup-count");
		
		if (i == 0) {
			queryString = "?path=" + documentPath;
		} else {
			queryString += "&path=" + documentPath;
		}
		
		i++;
	});
	
	if (queryString !== "") {
		$.getJSON(base + queryString, function(data) {
			$.each(data, function(path, formattedCount) {
				var documentCount = "";
				var count = ("" + formattedCount).replace(/[\s,]/g, '');
				count = parseInt(count, 10);
				var noteupSearchLink = $("a[data-link-noteup-count='" + path + "']")
				var citedByElem = noteupSearchLink.prev(".cited-by-count");
				
				if (count == 1) {
	                citedByElem.text(citedByPrefix);
					documentCount += ' ' + formattedCount + ' ' + singleDocument;
					noteupSearchLink.text(documentCount);
	            } else if (count > 1) {
	            	citedByElem.text(citedByPrefix);
					documentCount += ' ' + formattedCount + ' ' + multipleDocuments;
					noteupSearchLink.text(documentCount);
	            }
			});
		});
	}
}

function getFormattedNowDate() {
	var now = new Date(); 
	return now.getFullYear() + "-" + (("0" + (now.getMonth() + 1)).slice(-2)) + "-" + (("0" + (now.getDate())).slice(-2));
}

function nextSiblingWithClass(node, siblingClass) {
	while (node = node.nextSibling) {
		let str = " " + node.className + " ";
	    let testClass = " " + siblingClass + " ";
	    let hasClass = (str.indexOf(testClass) != -1) ;
		
        if (hasClass) {
            return node;
        }
    }
    return null;
}

/*** SATAL ***/

function toggleWithIcon(element, targetSelector) {
	$(targetSelector).toggle();
	
	let togglerIcon = $(element).find("i");
	if (togglerIcon.hasClass("fa-angle-down")) {
		togglerIcon.removeClass("fa-angle-down");
		togglerIcon.addClass("fa-angle-up");
	} else {
		togglerIcon.removeClass("fa-angle-up");
		togglerIcon.addClass("fa-angle-down");
	}
}

function showHide(target) {
	var item = document.getElementById(target);
	if (item.style.display == "") {
		item.style.display = "none";
	} else {
		item.style.display = "";
	}
}

function validateTrackChanges(msg) {
	var versions = document.getElementsByName("path");
	var count = 0;

	for (var i = 0; i < versions.length; i++) {
		if (versions[i].checked) {
			count++;
		}
	}

	if (count != 2) {
		alert(msg);
		return false;
	}
	return true;
}

//Following functions are for the table of contents of legislations pages

function toggleToc() {
	if (document.getElementById('TOC').style.display == 'none') {
		document.getElementById('TOC').style.display = '';
		document.getElementById('tocButton').innerHTML = hideTableOfContent;
	} else {
		document.getElementById('TOC').style.display = 'none';
		document.getElementById('tocButton').innerHTML = showTableOfContent;
	}
	
	// align the 'Expand All' text when opening the table of content for the first time
	if($('#tableExpandButton').length) {
		document.getElementById('tableExpandButtonDiv').innerHTML = '<span class=\"tocToggle\"><a onClick="openToc();" id="tableExpandButton"><img src="/images/Plus.JPG" class="lexedo-no-modify" alt="+"></a></span> '
			+ expandTableOfContentNode;
	}
}

function toggle(tocId, toggleId) {
	if (document.getElementById(tocId).style.display == 'none') {
		document.getElementById(tocId).style.display = '';
		document.getElementById(toggleId).innerHTML = '<img src=\"/images/Minus.JPG\" class=\"lexedo-no-modify\" alt="-">';
	} else {
		document.getElementById(tocId).style.display = 'none';
		document.getElementById(toggleId).innerHTML = '<img src=\"/images/Plus.JPG\" class=\"lexedo-no-modify\" alt="+">';
	}
}

var currentValueToggle;

function inerExecOpenToc() {

	if (currentValueToggle == 'tableExpandButton_plus') {
		var displayValue = '';
		var toggleLinkValue = '<img src=\"/images/Minus.JPG\" class="lexedo-no-modify" alt="-">';
		document.getElementById('tableExpandButtonDiv').innerHTML = '<span class=\"tocToggle\"><a onClick="openToc();" id="tableExpandButton"><img src="/images/Minus.JPG" class="lexedo-no-modify" alt="-"></a></span> '
				+ collapseTableOfContentNode;

		document.getElementById('tableExpandButtonDiv').className = "tableExpandButton_minus";
	} else {
		var displayValue = 'none';
		var toggleLinkValue = '<img src=\"/images/Plus.JPG\" class="lexedo-no-modify" alt="+">';
		document.getElementById('tableExpandButtonDiv').innerHTML = '<span class=\"tocToggle\"><a onClick="openToc();" id="tableExpandButton"><img src="/images/Plus.JPG" class="lexedo-no-modify" alt="+"></a></span> '
				+ expandTableOfContentNode;

		document.getElementById('tableExpandButtonDiv').className = "tableExpandButton_plus";
	}

	node = document.getElementById('TOC');

	var reTable = new RegExp('\\binnerTocTable\\b');
	var reToggle = new RegExp('\\btocToggleLink\\b');
	var els = node.getElementsByTagName("*");

	for ( var i = 0, j = els.length; i < j; i++) {
		if (reTable.test(els[i].className)) {
			els[i].style.display = displayValue;
		}
		if (reToggle.test(els[i].className)) {
			els[i].innerHTML = toggleLinkValue;
		}
	}

	document.body.className = '';
}

function openToc() {
	currentValueToggle = document.getElementById('tableExpandButtonDiv').className;

	document.body.className = 'busy';

	document.getElementById('tableExpandButtonDiv').innerHTML = '<span class=\"tocToggle\"><a><img src="/images/Plus.JPG" class="lexedo-no-modify" alt="+"></a></span> '
			+ waitForTableOfContent;

	function doTheWorkOpenToc() {
		inerExecOpenToc();
	}
	setTimeout(doTheWorkOpenToc, 0);
}


/*** END SATAL ***/

function isIeOrEdge() {
	return /edge|msie\s|trident\//i.test(window.navigator.userAgent);
}

function isIe() {
	return /msie\s|trident\//i.test(window.navigator.userAgent);
}

function isSmartphone() {
	var isSmartphone = false;
	if (window.matchMedia && window.matchMedia("(max-width: 767px)").matches) {
		isSmartphone = true;
	}
	
	return isSmartphone;
}

function isDesktop() {
	let isDesktop = true;
	if (window.matchMedia && window.matchMedia("(max-width: 1199.98px)").matches) {
		isDesktop = false;
	}
	
	return isDesktop;
}

function isTouchDevice() {
	return 'ontouchstart' in document.documentElement;
}

function fixSmartphoneDisplay() {
	if (isSmartphone()) {
		// fixes some QC judgments display (ie: QCDAG)
		$("div#originalDocument table, div#originalDocument tr, div#originalDocument td, div#originalDocument p").each(function () {
			$(this).removeAttr("width");
	        $(this).css("width", "auto");
	        
	        var cssMarginLeft = $(this).css("margin-left");
	        if (cssMarginLeft != undefined && cssMarginLeft !== "0px") {
	        	$(this).css("margin-left", "0px");
	        }
	        
	        var textIndent = $(this).css("text-indent");
	        if (textIndent != undefined && textIndent !== "0") {
	        	$(this).css("textIndent", "0");
	        }
	    });
		
		// fixes CA legislations display
		$("div#originalDocument div.canliidocumentcontent div").each(function () {
			$(this).css("width", "auto");
		});
		
		// prevent images with greater width than the viewport on small devices
		$("div#originalDocument div.canliidocumentcontent img").css("max-width", $(window).width() - 20);
		
		// fixes BC statutes display
		$("span.holder, span.secnumholder, span.rulenoholder").css("position", "static");
	}
}

function offsetAnchor(offset) {
    if (location.hash.length !== 0) {
        window.scrollTo(window.pageXOffset, window.pageYOffset - offset);
    }
}

/*** REFLEX2 MULTIPLE LINK ***/
function tipMultipleReflex2Link() {
	$(this).click(function(e) {
		e.stopPropagation();
	});
	
	var linkCount = $(this).attr("link-count");
	
	if (linkCount > 12) {
		$(this).attr("class", "reflex2-tooManyLinks");
	} else if (linkCount > 1) {
		var content = "<div><b><p>" + getTipTitleString(lang, linkCount) + "</b></p></div><ul>";
		for (var i = 1; i <= linkCount; i++) {
			var title = $(this).attr("title" + i);
			var link = $(this).attr("link" + i);
			
			if (link.indexOf("#sec") != -1 || link.indexOf("#art") != -1) {
				link+= "_smooth";
			}
			
			content += "<li><a class='multipleLawsLink' href='" + link + "'>" + title + "</a></li>";
		}
		content += "</ul>"
		
		this.addEventListener("click", function(e) {
			Tipped.create(this, "<div class='bootstrap'>" + content + "</div>", { 
				cache: false,
		    	showOn: false, 
		    	hideOn: 'click-outside',
		    	afterHide : function(content, element) {
			    	// remove the tipped after it's hidden, so the styles are reset if the user decides to switch theme
			    	Tipped.remove(element);
				} 
			});
		    Tipped.show(this);
		});
	}
}

function getTipTitleString(lang, linkCount) {
	if (lang == 'en') {
		return 'CanLII found ' + linkCount + ' possible links for this citation:';
	} else {
		return 'CanLII a trouvé ' + linkCount + ' liens possibles pour cette référence :';
	}
}
/*** END REFLEX2 MULTIPLE LINK ***/

function addDarkStylesheet() {
	let head = document.getElementsByTagName('HEAD')[0];
    let link = document.createElement('link');

    link.id = "darkStylesheet";
    link.rel = "stylesheet";
    link.type = "text/css";
    link.href = "/css/dark.css";
    head.appendChild(link);

	// also manage the stylesheet for the parent document, if inside an iframe
	let parentDarkStyleSheet = parent.document.getElementById("darkStylesheet");
	if (parentDarkStyleSheet == null) {
		let parentHead = parent.document.getElementsByTagName('HEAD')[0];
		let outsideLink = parent.document.createElement('link');

	    outsideLink.id = "darkStylesheet";
	    outsideLink.rel = "stylesheet";
	    outsideLink.type = "text/css";
	    outsideLink.href = "/css/dark.css";
	    parentHead.appendChild(outsideLink);
	}
}

function removeDarkStylesheet() {
	let element = document.getElementById("darkStylesheet");
	if (element != null) {
		element.parentNode.removeChild(element);
	}
	
	// also manage the stylesheet for the parent document, if inside an iframe
	let parentDarkStyleSheet = parent.document.getElementById("darkStylesheet");
	if (parentDarkStyleSheet != null) {
		parentDarkStyleSheet.parentNode.removeChild(parentDarkStyleSheet);
	}
}

function isDarkMode() {
	let canliiDark = readCookie("canliiTheme");
	if (canliiDark != null && canliiDark == 'dark') {
		return true;
	}
	return false;
}

function getUnsupportedBrowserString() {
	if (_language == 'fr') {
		return "Navigateur non supporté";
	} else {
		return "Unsupported browser";
	}
}

function updateQueryString(uri, key, value) {
    // Use window URL if no query string is provided
    if ( ! uri ) { uri = window.location.href; }

    // Create a dummy element to parse the URI with
    var a = document.createElement( 'a' ), 

        // match the key, optional square brackets, an equals sign or end of string, the optional value
        reg_ex = new RegExp( key + '((?:\\[[^\\]]*\\])?)(=|$)(.*)' ),

        // Setup some additional variables
        qs,
        qs_len,
        key_found = false;

    // Use the JS API to parse the URI 
    a.href = uri;

    // If the URI doesn't have a query string, add it and return
    if ( ! a.search ) {

        a.search = '?' + key + '=' + value;

        return a.href;
    }

    // Split the query string by ampersands
    qs = a.search.replace( /^\?/, '' ).split( /&(?:amp;)?/ );
    qs_len = qs.length; 

    // Loop through each query string part
    while ( qs_len > 0 ) {

        qs_len--;

        // Remove empty elements to prevent double ampersands
        if ( ! qs[qs_len] ) { qs.splice(qs_len, 1); continue; }

        // Check if the current part matches our key
        if ( reg_ex.test( qs[qs_len] ) ) {

            // Replace the current value
            qs[qs_len] = qs[qs_len].replace( reg_ex, key + '$1' ) + '=' + value;

            key_found = true;
        }
    }   

    // If we haven't replaced any occurrences above, add the new parameter and value
    if ( ! key_found ) { qs.push( key + '=' + value ); }

    // Set the new query string
    a.search = '?' + qs.join( '&' );

    return a.href;
}

function completeIframeLoad(iframe) {
	if (isDoctrinePath(iframe.contentWindow.location.href)) {
		iframe.style.height = '90vh';
	} else {
		iframe.style.height = '100vh';
		iframe.style.height = (iframe.contentWindow.document.documentElement.scrollHeight + 100) + 'px';
	}
	
	$("#searchDocumentFrame", parent.document).removeClass("loading");
	$("#frameSpinner", parent.document).css("opacity", "0");
}

function isDoctrinePath(path) {
	if (path.indexOf("commentary/doc") !== -1 || path.indexOf("doctrine/doc") !== -1) {
		return true;
	} else {
		return false;
	}
}

function addFootnotesTooltips() {
	Tipped.remove("a[name^='_ftnref']");
	
	$("a[name^='_ftnref']").each(function (e) {
		let ftnId = this.href.slice(this.href.lastIndexOf('_') + 1);
		Tipped.create(this, "<div class='bootstrap ftntip'>" + $("#" + ftnId).html() + "</div>");
	});
}

$(window).scroll(function() {
	var scrollTopValue = $(this).scrollTop();
	
	// back to top button
	if (scrollTopValue > 250) {
		$('button#backToTop').fadeIn(200);
	} else {
		$('button#backToTop').fadeOut(200);
	}
});

window.onload = init;