var skipTabHistory = false;

$(document).ready(function() {
	if (typeof Tipped != "undefined") {
		Tipped.setDefaultSkin('light');
	}
	
	// judgment and legislation tabs
    $('ul.nav-tabs a[data-toggle="tab"]').on('shown.bs.tab', function (e) { 
    	// this way we can have multiple tabs content to prevent bootstrap styles on document
    	var secondaryTab = $(this).attr('data-secondary');
		if (secondaryTab != undefined) {
			var otherTabs = secondaryTab.split(',');
			for(i= 0; i<otherTabs.length;i++) {
		    	nav = $('<ul class="nav d-none" id="tmpNav"></ul>');
		    	nav.append('<li class="nav-item"><a href="#" data-toggle="tab" data-target="' + otherTabs[i] + '">nav</a></li>"');
		    	nav.find('a').tab('show');
			}
		}
    	
		// store the currently selected tab in the hash value
		if (skipTabHistory == false) {
			var hash = (window.location.hash === "#unfavourable" || window.location.hash === "#discussing")
			&& e.target.hash === "#citing" ? window.location.hash : e.target.hash;
	    	if(history.pushState) {
	            history.pushState(null, null, hash);
	        } else {
	            window.location.hash = hash; //Polyfill for old browsers
	        }
        } else {
			skipTabHistory = false;
		}

		if(hash === "#citing") {
			getTreatmentTypesCounts();
			$('.treatment-list a[href="#citing"]').click();
		}

    	// disable highlight if not on the document tab
    	var tabId = $(this).attr("id");
    	if (tabId === "document-tab") {
    		$("#hiBar").fadeIn(200);
    		$(".scroll-marker").fadeIn(200);
    	} else {
    		$("#hiBar").fadeOut(200);
    		$(".scroll-marker").fadeOut(200);
    	}
    });

	$('.treatment-list a').click(function(){
		onTreatmentTabItemClick($(this))
	});

    // switch to the currently selected tab when loading the page
	if ($.isFunction($.fn.tab)) {
		loadCurrentTab();
	}
	
	// switch to the currently selected tab on browser back/forward
	$(window).on('popstate', function(e) {
		skipTabHistory = true;
		loadCurrentTab();
	});

    $('select#navArbitratorSelector, select#navYearsSelector, select#navMonthsSelector').on('change', function() {
    	if (this.value != null && this.value != "") {
    		window.location.href = this.value;
    	}
	});
	
	$("#basicItemsFilter, #doctrineItemsFilter").on("keyup", function() {
	    var value = normalizeString($(this).val());
	    
	    let toFilter = $("#legislationsContainer div.filterable, tr.tribunalRow, #decisionsListing div.row, #decisionsListing tr, #doctrineContainer div.filterable, #doctrineContainer tr.filterable");
	    let matchCount = 0;
	    
	    toFilter.each(function() {
	    	var normalizedText = normalizeString($(this).text());
		    var otherValues = $(this).attr("othervalues");
		    if (otherValues != undefined) {
		    	var normalizedOtherValues = normalizeString(otherValues);
		    }
	    	var match = (normalizedText.indexOf(value) > -1) || 
	    				(normalizedOtherValues != undefined && normalizedOtherValues.indexOf(value) > -1);
	    	
	    	if (match) {
				matchCount++;
			}			
	    	
	        $(this).toggle(match);
	    });
	    
	    if (matchCount == 0) {
			$(this).next("p.noResultsMessage").show();
		} else {
			$(this).next("p.noResultsMessage").hide();
		}
	});
	
	fixSmartphoneDisplay();

	$("div#languageSwitch a.canlii").on("click", function(e) {
		let element = $(e.currentTarget);
		let cookieValue = element[0].dataset['lang'];
		setCookie('userLocale', cookieValue, 365);
	});

	$(".logos-slider").on("keypress", function(e) {
		if (e.keyCode === 13) {
			$("div#logos").carousel($(this).data("slide-to"));
		}
	});

	$("#toggleAudio").on("click", function(e) {
		toggleAudioCaptcha();
	});

	$("#toggleAudio").on("keypress", function(e) {
		if (e.keyCode === 13) {
			toggleAudioCaptcha();
		}
	});

	loadSurvey();
	loadTheme();
});

function loadCurrentTab() {
	if(window.location.hash === "#unfavourable") {
		$('ul.nav-tabs a[href="#citing"]').tab('show');
		getTreatmentTypesCounts();
		$('.treatment-list a[href="#unfavourable"]').click();
	} else if(window.location.hash === "#discussing") {
		$('ul.nav-tabs a[href="#citing"]').tab('show');
		getTreatmentTypesCounts();
		$('.treatment-list a[href="#discussing"]').click();
	} else if (window.location.hash === "") {
		// hash will be empty if we come from another page
		$('ul.nav-tabs a').first().tab('show');
	} else {
		$('ul.nav-tabs a[href="' + window.location.hash + '"]').tab('show');
	}
}

function onTreatmentTabItemClick(item) {
	var dataTarget = item.attr('data-target');
	var tab = $('#' + dataTarget);
	if(dataTarget === "citingContent") {
		getCitedByTabContent(tab);
	}
	else if(dataTarget === "discussingContent") {
		getDiscussedByTabContent(tab);
	}
	else if(dataTarget === "criticizingContent") {
		getCriticizedByTabContent(tab);
	}

	$('.treatment-list a').removeClass('font-weight-bold')
	$('.treatment-list a[data-target=' + item.attr("data-target") + ']').addClass('font-weight-bold')
}

function toggleAudioCaptcha() {
	$('#captchaTag').toggle();
	$('#audioCaptchaTag').toggle();
	if ($('#audioCaptchaTag').css("display") == "none") {
		$('#captchaResponse').focus();
	} else {
		$('#audioCaptchaTag').focus();
	}
}

function loadSurvey() {
	$("a#surveyModalToggler").on("keypress", function(e) {
		if (e.keyCode === 13) {
			$("#surveyModal").modal();
		}
	});
	
	$("div#surveyModal button.rater").on("click", function(e) {
		selectSurveyStar(e);
	});
	
	$("div#surveyModal button.rater").on("keypress", function(e) {
		if (e.keyCode === 13) {
			selectSurveyStar(e);
		}
	});
	
	$("div#surveyModal button#surveyDoNotShowAgain").on("click", function(e) {
		setCookie('stopSurvey', true, 365);
	});
	
	$("div#surveyModal button#surveySubmit").on("click", function(e) {
		var selectedRating = $("div#surveyModal i.fa-star.rate-selected");
		if (selectedRating == null || selectedRating.length == 0) {
			$("div#surveyModal span#ratingWarning").show();
		} else {
			$("div#surveyModal span#ratingWarning").hide();
			
			var rating = selectedRating.attr("id").split("-").pop();
			sendSurvey(rating);
			
			$('div#surveyModal').modal('hide');
			
			setCookie('stopSurvey', true, 365);
		}
	});
	
	$("div#surveyModal").on("hidden.bs.modal", function (e) {
		// reset values
		$("div#surveyModal i.fa-star").each(function () {
			$(this).removeClass("rate-selected");
			$(this).css("color", "#d7eb00");
		});
		$("div#surveyModal textarea#surveyMessage").val("");
	});
	
	/*if (!isTouchDevice()) {
		// display the survey once every max requests
		var min = 1;
		var max = 200;
		var random = Math.floor(Math.random() * (+max - +min)) + +min;
		if (random == 100) {
			var surveyCookie = readCookie("stopSurvey");
			if (surveyCookie == null || surveyCookie != 'true') {
				$('div#surveyModal').modal('show');
			}
		}
	}*/
}

function selectSurveyStar(e) {
	var element = $(e.currentTarget);
	var rateValue = element.children().first().attr("id").split("-").pop();
	for (var i=1; i<=5; i++) {
		if (i <= rateValue) {
			$("i#rate-" + i).css("color", "#ebb000");
			$("i#rate-" + i).css("border-bottom-style", "solid");
			$("i#rate-" + i).css("border-bottom-width", "2px");
			$("i#rate-" + i).css("padding-bottom", "2px");
		} else {
			$("i#rate-" + i).css("color", "#d7eb00");
			$("i#rate-" + i).css("border-bottom-width", "0");
		}
		
		if (i == rateValue) {
			$("i#rate-" + i).addClass("rate-selected");
		} else {
			$("i#rate-" + i).removeClass("rate-selected");
		}
	}
}

function loadTheme() {
	if (isIe()) {
		document.querySelector("#darkModeCb").disabled = true;
		$("#darkOption").tooltip({
			placement : 'right',
			title: getUnsupportedBrowserString()
		});
	}

	if (isDarkMode()) {
		let darkModeCb = document.querySelector("#darkModeCb");
		
		// may be null if we are inside an iframe without the canlii footer
		if (darkModeCb != null) {
			darkModeCb.checked = true;
		}
		
		if (typeof Tipped != "undefined") {
			Tipped.setDefaultSkin('dark');
		}
	}

	$("input#darkModeCb").on("click", function(e) {
		toggleDarkMode(e);
	});
}

function toggleDarkMode(e) {
	let elementInLegislationPagesOnly = $("div.canliidocumentcontent");

	if (!isDarkMode()) {
		addDarkStylesheet();
		
		if (typeof Tipped != "undefined") {
			Tipped.setDefaultSkin('dark');

			// need to re-create all tipped, so their style can be updated
			recreateAllScrollMarkerTips(elementInLegislationPagesOnly != null);
			addFootnotesTooltips();
		}
		
		setCookie('canliiTheme', "dark", 365);
	} else {
		removeDarkStylesheet();
		
		if (typeof Tipped != "undefined") {
			Tipped.setDefaultSkin('light');

			// need to re-create all tipped, so their style can be updated
			recreateAllScrollMarkerTips(elementInLegislationPagesOnly != null);
			addFootnotesTooltips();
		}
		
		setCookie('canliiTheme', "default", 365);
	}
	// keep open
	e.stopPropagation();
}
