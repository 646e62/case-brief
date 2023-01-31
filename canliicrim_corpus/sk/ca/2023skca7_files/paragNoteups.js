function createParagTools(urlToCall, concatId, origin, translationUrl, lang, citationText, tinyUrl, forLegislations) {
	// sometimes the tips shows dark even when there is no dark theme, so here we make sure the correct theme is set
	if (isDarkMode()) {
		Tipped.setDefaultSkin('dark');
	} else {
		Tipped.setDefaultSkin('light');
	}
	
	$("div.viibes-marker-toolbox").on("click", function (e) {
		let dropdownMenu = $(this).find("div.dropdown-menu");
		let parag = $(this).next("[data-viibes-parag]");
		let paragNum = parag.data("viibesParag");
		
		let dropdownItem = dropdownMenu.find("a.dropdown-item.copy-text");
		if (dropdownItem == null || dropdownItem.length == 0) {
			// add menu dynamically so the big legislations are less bulky (less bytes)
			$.get("/noteups/paragNoteups/menu?lang=" + lang + "&concatId=" + concatId + "&parag=" + paragNum + "&origin=" + origin + "&translationUrl=" + translationUrl + "&forLegislations=" + forLegislations, function(data) {
				dropdownMenu.html(data);
				
				dropdownMenu.find("a.copy-text").on("click", function (e) {
			    	// this prevents the dropdown from closing on click
			    	e.stopPropagation();
				    
					let paragWrapper = $(this).closest("div.paragWrapper")[0];
					let beginElem = paragWrapper.querySelector("[data-viibes-start]");
					let endElem = document.querySelector('[data-viibes-end="' + beginElem.dataset['viibesStart'] + '"]');
				    if (endElem == null) {
					    // clicked on the last paragraph, select until the end of document
					    endElem = $("footer.bootstrap")[0];
				    }
				    
				    selectText(paragWrapper, endElem);
					Tipped.create($(this), "<div class='bootstrap'>" + getCopiedMsg(lang) + "</div>", { cache: false, showOn: false, afterHide : function(content, element) {
						// remove the tipped after it's hidden, so the styles are reset if the user decides to switch theme
						Tipped.remove(element);
					} });
					Tipped.show(this);
			    });

				dropdownMenu.find("a.copy-source").on("click", function (e) {
					// this prevents the dropdown from closing on click
			    	e.stopPropagation();
			
					let paragNumber = $(this).closest("div.viibes-marker-toolbox")[0].dataset["withParag"];
					let paragUrl = tinyUrl + "#par" + paragNumber;
					let sourcePart = citationText + ", " + getAtMsg(lang) + " para " + paragNumber + ", <" + paragUrl + ">, " + getRetrievedOnMsg(lang) + getFormattedNowDate();
					
					if (forLegislations != undefined && forLegislations == true) {
						let section = paragNumber;
						let subsection = null;
						paragUrl = tinyUrl + "#" + getSectionParam(lang) + section;
						if (section.indexOf("-") >= 0) {
							let splittedSection = section.split("-");
							section = splittedSection[0];
							subsection = splittedSection[1];
							
							paragUrl = tinyUrl + "#" + getSectionParam(lang) + section + getSubsectionParam(lang) + subsection;
						}
						
						sourcePart = citationText + ", " + getSectionReferenceMsg(lang) + " " + section + (subsection == null ? "" : "(" + subsection + ")") + ", <" + paragUrl + ">, " + getRetrievedOnMsg(lang) + getFormattedNowDate();
					}
				    
				    copyStringToClipboard(sourcePart);
					Tipped.create($(this), "<div class='bootstrap'>" + getCopiedSourceMsg(lang) + "</div>", { cache: false, showOn: false, afterHide : function(content, element) {
						// remove the tipped after it's hidden, so the styles are reset if the user decides to switch theme
						Tipped.remove(element);
					} });
					Tipped.show(this);
				});
				
				dropdownMenu.find("a.copy-link").on("click", function (e) {
					// this prevents the dropdown from closing on click
			    	e.stopPropagation();
				    
					let paragNumber = $(this).closest("div.viibes-marker-toolbox")[0].dataset["withParag"];
					let paragUrl = tinyUrl + "#par" + paragNumber;
					if (forLegislations != undefined && forLegislations == true) {
						let section = paragNumber;
						let subsection = null;
						paragUrl = tinyUrl + "#" + getSectionParam(lang) + section;
						if (section.indexOf("-") >= 0) {
							let splittedSection = section.split("-");
							section = splittedSection[0];
							subsection = splittedSection[1];
							
							paragUrl = tinyUrl + "#" + getSectionParam(lang) + section + getSubsectionParam(lang) + subsection;
						}
					}
				    
				    copyStringToClipboard(paragUrl);
					Tipped.create($(this), "<div class='bootstrap'>" + getCopiedLinkMsg(lang) + "</div>", { cache: false, showOn: false, afterHide : function(content, element) {
						// remove the tipped after it's hidden, so the styles are reset if the user decides to switch theme
						Tipped.remove(element);
					} });
					Tipped.show(this);
				});
			})
		    .fail(function(jqXHR) {
			    console.error(jqXHR);
		    })
		    .always(function() {
			    // nothing to do
		    });
		}
	});
	
	// in IE, all childs must have the 'unselectable' attribute set to 'on' for it to be unselectable
    if (isIe()) {
		let unselectables = document.querySelectorAll(".unselectable");
		for (let i=0; i<unselectables.length; i++) {
			makeUnselectable(unselectables[i]);
		}
    }
	
	$("#markerLoadingAlert").fadeIn(200);
	
    $.get(urlToCall, function(data) {
	    noteupParags = Object.keys(data);
	    noteupCounts = noteupParags.map(function(e) {
		      return data[e];
	    });
	    let maxCount = Math.max.apply(Math, noteupCounts);
	    
	    // unable to load these legislations with the heatmap in Chrome/Edge on macOS
	    let excludedConcatIds = ['l5549', 'l12792'];
	    
		let addHeatmap = noteupParags.length != 0 && (noteupParags.length < 2000) && !excludedConcatIds.includes(concatId) && !isIe();
		//let addHeatmap = noteupParags.length != 0 && !isIe();
		
		if ((forLegislations && !isIe() && addHeatmap) || !forLegislations) {
			// all read and writes must be separated, so the browser does not reflow for every element in the loop
			let markersToAdd = [];
			let paragElements = document.querySelectorAll("[data-viibes-parag]");
			let paragElementsMap = new Map();
			for (let i=0; i<paragElements.length; i++) {
				paragElementsMap[paragElements[i].dataset.viibesParag] = paragElements[i];
			}
			
			let paragEndElements = document.querySelectorAll('[data-viibes-end]');
			let paragEndElementsMap = new Map();
			for (let i=0; i<paragEndElements.length; i++) {
				paragEndElementsMap[paragEndElements[i].dataset.viibesEnd] = paragEndElements[i];
			}
			
			for (let i=0; i<noteupParags.length; i++) {
				// in some cases (Youth Protection Act), the parags can contain a new line, which breaks the javascript
				const parag = noteupParags[i].replace(/\n/g, "\\n"); 
				
				let paragElement = paragElementsMap[parag];
				
				if (paragElement != null) {
					const viibesId = paragElement.dataset['viibesStart'];
					let end = paragEndElementsMap[viibesId];
					
					let markerToAdd = buildParagraphMarker(addHeatmap, maxCount, paragElement, end);
					if (markerToAdd != null) {
						markersToAdd.push(markerToAdd);
					}
				}
				
			}
			
			insertParagraphMarkers(markersToAdd);
			
			let scrollMarker = document.querySelector(".scroll-marker");
			let scrollMarkersToAdd = buildScrollMarkers(scrollMarker, markersToAdd, paragEndElementsMap);
			insertScrollMarkers(lang, forLegislations, scrollMarkersToAdd);
		}
	    
	    window.addEventListener('resize', _.debounce(calculateParagMarkers, 300));
	    window.addEventListener('resize', _.debounce(calculateScrollMarkers, 300));

	    if (isIe()) {
		    window.addEventListener('copy', function (e) {
			    // prevent the selection of unselectable elements in IE 
			    // (in IE, if the selection starts outside, unselectable elements are still selectable)
			    copyWithoutViibesMarkers();
		    });
	    }
    })
    .fail(function(jqXHR) {
	    console.error(jqXHR);
    })
    .always(function() {
	    $("#markerLoadingAlert").fadeOut(500);
    });
}

function buildParagraphMarker(addHeatmap, maxCount, start, end) {
	let citedCount = 0;
	let citedCountDisplay = 0;
	let viibesCountElement = start.parentElement.querySelector("[data-noteup-count]");
	if (viibesCountElement != null) {
		citedCount = viibesCountElement.dataset["noteupCount"];
		citedCountDisplay = viibesCountElement.dataset["noteupCountDisplay"];
		
		if (citedCountDisplay == undefined || citedCountDisplay == null) {
			citedCountDisplay = kFormatter(viibesCountElement.dataset["noteupCount"]);
			if (isIe()) {
				// we have to use jQuery so it works in IE11
				$(viibesCountElement).attr("data-noteup-count-display", citedCountDisplay);
			} else {
				viibesCountElement.dataset["noteupCountDisplay"] = kFormatter(viibesCountElement.dataset["noteupCount"]);
			}
		}
	}
	
	let markerToAdd = null;
	if (addHeatmap && citedCount != null && citedCount != 0) {
		// add a colored marker to cited paragraphs
		markerToAdd = {};
		markerToAdd['className'] = 'viibes-marker';
		markerToAdd['bgColor'] = getRgbaBlueValue(citedCount, maxCount);
		markerToAdd['start'] = start;
		markerToAdd['height'] = computeParagMarkerHeight(start, end);
		markerToAdd['citedCountDisplay'] = citedCountDisplay;
	}
	
	return markerToAdd;
}

function insertParagraphMarkers(markersToAdd) {
	for (let i=0; i<markersToAdd.length; i++) {
		let marker = document.createElement('span');
		marker.className = markersToAdd[i]['className'];
		marker.style.height = markersToAdd[i]['height'];
		marker.style.backgroundColor = markersToAdd[i]['bgColor'];
		
		if (isIe()) {
			makeUnselectable(marker);
		}

		markersToAdd[i]['start'].appendChild(marker);
		markersToAdd[i]['marker'] = marker;
	}
}

function buildScrollMarkers(scrollMarker, markersToAdd, paragEndElementsMap) {
	let scrollMarkersToAdd = [];
	
	// read scroll markers data
	for (let i=0; i<markersToAdd.length; i++) {
		let scrollMarkerToAdd = {};
		let start = markersToAdd[i]['start'];
		let marker = markersToAdd[i]['marker'];
		
		let end = paragEndElementsMap[start.dataset['viibesStart']];
	    if (end == null) {
	    	end = $("footer.bootstrap")[0];
	    }

		let spanTop = start.parentElement.offsetTop;
		let offsetParent = start.parentElement.offsetParent;
		if (offsetParent != null && offsetParent.tagName !== "BODY") {
			spanTop += offsetParent.offsetTop;
		}
		
		let scrollMarkerChildHeightAndPos = computeScrollMarkerHeightAndPos(spanTop, marker);
		scrollMarkerToAdd['scrollMarkerChildTop'] = scrollMarkerChildHeightAndPos['top'];
		scrollMarkerToAdd['scrollMarkerChildHeight'] = scrollMarkerChildHeightAndPos['height'];
		scrollMarkerToAdd['start'] = start;
		scrollMarkerToAdd['end'] = end;
		scrollMarkerToAdd['spanTop'] = spanTop;
		scrollMarkerToAdd['marker'] = marker;
		scrollMarkerToAdd['bgColor'] = markersToAdd[i]['bgColor'];
		scrollMarkerToAdd['citedCountDisplay'] = markersToAdd[i]['citedCountDisplay'];
		scrollMarkerToAdd['scrollMarker'] = scrollMarker;
		
		scrollMarkersToAdd.push(scrollMarkerToAdd);
	}
	
	return scrollMarkersToAdd;
}

function insertScrollMarkers(lang, forLegislations, scrollMarkersToAdd) {
	for (let i=0; i<scrollMarkersToAdd.length; i++) {
		let scrollMarkerChild = document.createElement("span");
		scrollMarkerChild.style.top = scrollMarkersToAdd[i]['scrollMarkerChildTop'];
		scrollMarkerChild.style.height = scrollMarkersToAdd[i]['scrollMarkerChildHeight'];
		scrollMarkerChild.dataset['scrollParag'] = scrollMarkersToAdd[i]['start'].dataset['viibesParag'];
		scrollMarkerChild.style.backgroundColor = scrollMarkersToAdd[i]['bgColor'];
		scrollMarkersToAdd[i]['scrollMarker'].appendChild(scrollMarkerChild);
		
		// scroll and highlight paragraph on click
		scrollMarkerChild.addEventListener("click", function(e) {
			const marker = scrollMarkersToAdd[i]['marker'];
	    	const desiredOffset = scrollMarkersToAdd[i]['spanTop'] - 100;
			const onScroll = function () {
				if (Math.floor(window.pageYOffset) === desiredOffset || isScrolledToBottom()) {
					let viibesMarkerLeft = marker.offsetLeft;
					let paraLeft = -10;
					let paraRight = viibesMarkerLeft - 3;
					let postScrollHl = document.createElement("div");
					postScrollHl.style.left = (paraLeft - viibesMarkerLeft) + "px";
					postScrollHl.style.width = (paraRight - paraLeft) + "px";
					postScrollHl.className = "scrollHighlight";
					marker.innerHTML = '';
					marker.appendChild(postScrollHl);
					window.removeEventListener('scroll', onScroll)
					window.setTimeout(function() { postScrollHl.style.zIndex = -1; }, 2000);
				}
			};
			window.addEventListener('scroll', onScroll)
	
			if (Math.floor(window.pageYOffset) === desiredOffset) {
				onScroll();
			} else {
	    		window.scrollTo({
	    			top: desiredOffset,
	    			left: 0,
	    			behavior: 'smooth'
	    		});
	    	}
	
	    	Tipped.hideAll();
	    });

		// add heatmap marker tip
	    if (!isTouchDevice()) {
			createScrollMarkerTip(lang, scrollMarkersToAdd[i]['start'], scrollMarkerChild, scrollMarkersToAdd[i]['end'], scrollMarkersToAdd[i]['citedCountDisplay'], forLegislations);
	    }
	}
}

function isScrolledToBottom() {
	let scrollTop = (document.documentElement && document.documentElement.scrollTop) || document.body.scrollTop;

	// Grodriguez's fix for scrollHeight:
	// accounting for cases where html/body are set to height:100%
	let scrollHeight = (document.documentElement && document.documentElement.scrollHeight) || document.body.scrollHeight;
	
	// >= is needed because if the horizontal scrollbar is visible then window.innerHeight includes
	// it and in that case the left side of the equation is somewhat greater.
	return (scrollTop + window.innerHeight) >= scrollHeight;
}

function getRetrievedOnMsg(lang) {
    if (lang === "en") {
        return "retrieved on ";
    } else {
        return "consulté le ";
    }
}

function getCopiedMsg(lang) {
    if (lang === "en") {
        return "Text copied to your clipboard";
    } else {
        return "Texte copié dans le presse-papiers";
    }
}

function getDocumentsMsg(citedCount) {
    if (citedCount == 1) {
        return "document";
    } else {
        return "documents";
    }
}

function getSectionParam(lang) {
    if (lang === "en") {
        return "sec";
    } else {
        return "art";
    }
}

function getSectionReferenceMsg(lang) {
    if (lang === "en") {
        return "s";
    } else {
        return "art";
    }
}

function getSubsectionParam(lang) {
    if (lang === "en") {
        return "subsec";
    } else {
        return "par";
    }
}

function getAtMsg(lang) {
    if (lang === "en") {
        return "at";
    } else {
        return "au";
    }
}

function getRgbaBlueValue(citedCount, maxCount) {
	let opacityValue = getBaseLog(citedCount, maxCount);
	if (maxCount > 0 && isNaN(opacityValue)) {
		opacityValue = 1;
	} else if (opacityValue < 0.2) {
    	// minimum opacity is 0.1
		opacityValue = 0.2;
    }
	
	return "rgba(2,122,187," + opacityValue + ")"; // canlii blue
//    return "rgba(0,86,179," + opacityValue + ")"; // canlii hover blue
}

function getOpacity(citedCount, maxCount) {
	let opacityValue = getBaseLog(citedCount, maxCount);
	if (opacityValue < 0.2) {
    	// minimum opacity is 0.2
		opacityValue = 0.2;
    }
	return opacityValue;
}

function getBaseLog(x, y) {
	return Math.log(x) / Math.log(y);
}

function calculateParagMarkers() {
	let markersToUpdate = [];
	
	// read
	let paragEndElements = document.querySelectorAll('[data-viibes-end]');
	let paragEndElementsMap = new Map();
	for (let i=0; i<paragEndElements.length; i++) {
		paragEndElementsMap[paragEndElements[i].dataset.viibesEnd] = paragEndElements[i];
	}
			
    let viibesStarts = document.querySelectorAll('[data-viibes-start]');
	for (let i=0; i<viibesStarts.length; i++) {
		let start = viibesStarts[i];
		let marker = start.querySelector('.viibes-marker');
		if (marker != null) {
			const viibesId = start.dataset['viibesStart'];
			let end = paragEndElementsMap[viibesId];
			if (end == null) {
		    	end = $("footer.bootstrap")[0];
		    }
			
			let markerToUpdate = {};
			markerToUpdate['marker'] = marker; 
			markerToUpdate['height'] = computeParagMarkerHeight(start, end);
        	markersToUpdate.push(markerToUpdate);
        }
	}
	
	// write
	for (let i=0; i<markersToUpdate.length; i++) {
		markersToUpdate[i]['marker'].style.height = markersToUpdate[i]['height'];
	}
}

function computeParagMarkerHeight(start, end) {
    if (end == null) {
    	end = $("footer.bootstrap")[0];
    }
    const top = start.getBoundingClientRect().top;
    const bottom = end.getBoundingClientRect().top;
    const height = bottom - top;
    
    return 'calc(-8px + ' + height + 'px)';
}

function calculateScrollMarkers() {
	let markersToUpdate = [];
	
	// read
	let paragElements = document.querySelectorAll("[data-viibes-parag]");
	let paragElementsMap = new Map();
	for (let i=0; i<paragElements.length; i++) {
		paragElementsMap[paragElements[i].dataset.viibesParag] = paragElements[i];
	}
	
	let scrollMarkers = document.querySelectorAll('div.scroll-marker span');
	for (let i=0; i<scrollMarkers.length; i++) {
		let scrollMarker = scrollMarkers[i];
		
		let paragNum = scrollMarker.dataset['scrollParag'];
		let paragMarker = paragElementsMap[paragNum];
		let viibesMarkerChild = paragMarker.querySelector(".viibes-marker");
		
		let scrollMarkerChildHeightAndPos = computeScrollMarkerHeightAndPos(paragMarker.parentElement.offsetTop, viibesMarkerChild);
		
		let markerToUpdate = {};
		markerToUpdate['marker'] = scrollMarker;
		markerToUpdate['scrollMarkerChildTop'] = scrollMarkerChildHeightAndPos['top'];
		markerToUpdate['scrollMarkerChildHeight'] = scrollMarkerChildHeightAndPos['height'];
		
		markersToUpdate.push(markerToUpdate);
	}
	
	// write
	for (let i=0; i<markersToUpdate.length; i++) {
		markersToUpdate[i]['marker'].style.top = markersToUpdate[i]['scrollMarkerChildTop'];
		markersToUpdate[i]['marker'].style.height = markersToUpdate[i]['scrollMarkerChildHeight'];
	}
}

function computeScrollMarkerHeightAndPos(spanTop, viibesMarkerChild) {
	let containerHeight = $("div#wrap").outerHeight(true);
	let headerHeight = $("div#canliiHeader").outerHeight(true);
	let footerHeight = $("footer").outerHeight(true);
	
	let fullPageHeight = containerHeight + headerHeight + footerHeight;
	let viewportHeight = document.documentElement.clientHeight;
	
	let markerTop = (viewportHeight * spanTop / fullPageHeight) + 8;
	let markerHeight = viewportHeight * (viibesMarkerChild.offsetHeight + 8) / fullPageHeight;
	
	return {top: markerTop + "px", height: markerHeight + "px"}
}

function sign(x) {
	// Math.sign is unsupported in IE11
	return ((x > 0) - (x < 0)) || +x;
}

function makeUnselectable(node) {
    if (node.nodeType == 1) {
        node.setAttribute("unselectable", "on");
    }
    var child = node.firstChild;
    while (child) {
        makeUnselectable(child);
        child = child.nextSibling;
    }
}

function rgba2hex(orig) {
	var a, isPercent,
      rgb = orig.replace(/\s/g, '').match(/^rgba?\((\d+),(\d+),(\d+),?([^,\s)]+)?/i),
      alpha = (rgb && rgb[4] || "").trim(),
      hex = rgb ? 
      (rgb[1] | 1 << 8).toString(16).slice(1) +
      (rgb[2] | 1 << 8).toString(16).slice(1) +
      (rgb[3] | 1 << 8).toString(16).slice(1) : orig;
        if (alpha !== "") {
          a = alpha;
        } else {
          a = 01;
        }

        a = Math.round(a * 100) / 100;
          var alpha = Math.round(a * 255);
          var hexAlpha = (alpha + 0x10000).toString(16).substr(-2).toUpperCase();
          hex = hex + hexAlpha;

	return "#" + hex;
}
