var canliiCustomNavBar = {
    /**
     * Sera appelé une fois lorsque le surligneur sera prêt à afficher la barre.
     *
     * options: un objet identique à l'argument "options" qui est passé à la fonction d'initialisation du surligneur.
     * highlighter: un objet permettant à la barre d'interagir avec le surligneur (voir plus bas.)
     */
    init: function(options, highlighter) {
    	var highlightMatch = options.highlightMatch;
    
		for (var i=0; i<options.terms.length; i++) {
			if (options.terms[i].isPresentInDocument == true || !highlightMatch) {
				_highlight.atLeastOneTerm = true;
				break;
			}
		}
	
		var hasHeader = options.hasHeader;
		var pdfMode = options.pdfMode;
		var pdfFirstPage = options.pdfFirstPage || 1;
		var pdfTotalPages = options.pdfTotalPages || 0;
		
		var highlightbarPageLabel = "Page";
		var highlightbarOf = lang === "fr" ? "de" : "of";
		var highlightbarEditTip = lang === "fr" ? "Modifier votre requête pour ce document." : "Change your query for the current document.";
		var highlightbarPreviousTip = lang === "fr" ? "Occurence précédente" : "Previous appearance";
		var highlightbarNextTip = lang === "fr" ? "Occurence suivante" : "Next appearance";
		var hiPlaceholder = lang === "fr" ? "Trouver dans le document" : "Find in document";
		var highlightbarSearchTip = lang === "fr" ? "Rechercher dans le document" : "Search within the document";
		var highlightbarCancelTip = lang === "fr" ? "Annuler la modification" : "Cancel";
		
    	var hiBar = 
			'<div id="hiBar" class="bootstrap display-flex ' + (hasHeader == false ? 'framed' : '') + '">' +
            	'<div id="hiBar-body" class="display-flex">' +
            		'<div id="hiBar-page-widget" class="control-text ' + (pdfMode == true ? 'display-flex' : 'display-none') + '">' +
            			'<span id="hiBar-page-widget-label">' + highlightbarPageLabel + '</span>' +
            			'<input id="hiBar-page-widget-page-number-input" class="form-control form-control-sm" type="text" value="' + pdfFirstPage + '">' +
            			'<span>&nbsp;</span>' +
            		'</div>' +
            		'<div id="hiBar-highlight-widget-search" class="display-flex">' +
            			'<div id="hiBar-highlight-widget-search-terms-edit" class="' + (_highlight.atLeastOneTerm == false ? 'display-flex' : 'display-none') + '">' +
            				'<input id="hiBar-highlight-widget-search-terms-edit-input" class="form-control form-control-sm" type="text" aria-label="' + hiPlaceholder + '" placeholder="' + hiPlaceholder + '">' +
            				'<button id="hiBar-highlight-widget-search-terms-edit-ok" title="' + highlightbarSearchTip + '"><i class="fas fa-search widget-btn px-2"></i></button>' +
            				'<button id="hiBar-highlight-widget-search-terms-edit-cancel" ' + (_highlight.atLeastOneTerm == false ? 'class="display-none"' : '') + ' title="' + highlightbarCancelTip + '"><i class="fas fa-times widget-btn"></i></button>' +
            			'</div>' +
            			'<div id="hiBar-highlight-widget-search-terms-container" class="' + (_highlight.atLeastOneTerm == false ? 'display-none' : 'display-flex') + '">' +
            				'<div id="hiBar-highlight-widget-search-terms" class="display-flex"></div>' +
            				'<div id="hiBar-highlight-widget-counts" class="control-text display-flex">' +
            					'<span id="highlight-count">0</span>' +
            					'<span>&nbsp;</span>' +
            					'<span>' + highlightbarOf + '</span>' +
            					'<span>&nbsp;</span>' +
            					'<span id="highlight-total-count">0</span>' +
            				'</div>' +
            				'<div id="hiBar-highlight-widget-search-controls" class="display-flex">' +
            					'<button id="hiBar-highlight-widget-prev" title="' + highlightbarPreviousTip + '"><i class="fas fa-arrow-up widget-btn"></i></button>' +
            					'<button id="hiBar-highlight-widget-next" title="' + highlightbarNextTip + '"><i class="fas fa-arrow-down widget-btn"></i></button>' +
            					'<button id="hiBar-highlight-widget-edit" title="' + highlightbarEditTip + '"><i class="fas fa-edit widget-btn"></i></button>' +
            				'</div>' +
            			'</div>' +
            		'</div>' +
            	'</div>' +
            '</div>';

		highlighter.setActiveTerms(options.terms);
		_highlight.activeTerms = options.terms;
		
		if (hasHeader == true) {
			$("#headerContent").append($(hiBar));
		} else {
			// this means we are on the search page
			_highlight.scrollDocument = parent.document;
			_highlight.scrollWindow = parent.window;

			var highlightBar = $("#hiBar", _highlight.scrollDocument);
			if (highlightBar == null || highlightBar.length == 0) {
				$("#hiBarContainer", _highlight.scrollDocument).append(hiBar);
			} else {
				highlightBar[0].outerHTML = hiBar;
			}
		}
		
		_highlight.createTermsCheckboxes(options.terms, highlightMatch, highlighter);
		
		$("#hiBar-highlight-widget-prev", _highlight.scrollDocument).click(highlighter.scrollPrevious);
		$("#hiBar-highlight-widget-next", _highlight.scrollDocument).click(highlighter.scrollNext);
		$("#hiBar-highlight-widget-edit", _highlight.scrollDocument).click(_highlight.editHighlight);
		$("#hiBar-highlight-widget-search-terms-edit-cancel", _highlight.scrollDocument).click(_highlight.cancelEditHighlight);
		$("#hiBar-highlight-widget-search-terms-edit-ok", _highlight.scrollDocument).click(function () {
            _highlight.submitNewHighlight();
        });
		$("#hiBar-highlight-widget-search-terms-edit-input", _highlight.scrollDocument).on("keyup", _highlight.handleKeyPressed);
		$("#hiBar-page-widget-page-number-input", _highlight.scrollDocument).keyup(function(e) {
            if (e.keyCode === 13) {
                _highlight.scrollToPage(hasHeader, pdfFirstPage, pdfTotalPages);
            }
        });

		if (pdfMode == true) {
			$(_highlight.scrollWindow).scroll(function() {
			    _highlight.updatePageInput(pdfFirstPage);
			});
		}
		
		let highlightbarMissingTermTip = lang === "fr" ? "Ce terme n'a pas été trouvé dans ce document, Cependant, les termes de votre requête se trouvent très fréquemment dans les documents qui citent ce document, ce qui est considéré par le moteur de recherche comme un indice clair de pertinence."
			 : "This term could not be found in the current document. However, your query appears disproportionally often in documents citing this document, which is considered by the search engine a strong indication of relevance.";
		$(".solexMissingTermIcon").tooltip({
			placement : 'bottom',
			trigger : 'hover',
			html: true,
			title: highlightbarMissingTermTip,
			container: $(".solexMissingTermIcon").closest('.bootstrap')
		});
	},

    /**
     * Appelé par le surligneur pour indiquer quel terme est présentement sélectionné (ex: 1 of 128). Cette fonction
     * sera appelée:
     *  1. Immédiatement après l'initialisation;
     *  2. Lorsque l'usager scroll la page manuellement et que le terme sélectionné change;
     *  3. Après un appel à callback.scrollNext/scrollPrevious;
     *  3. Lorsque l'usager active ou désactive certains termes (normalement après un appel à highlighter.setActiveTerms).
     *
     * currentTermIndex: l'index du terme/phrase présentement sélectionné (0 à l'initialisation, indexé à 1)
     * termCount: le nombre de termes/phrases surlignés sur la page.
     */
    setCurrentTermIndex: function(currentTermIndex, termCount) {
		//TODO: update only if there is at least one term
		$("#highlight-count", _highlight.scrollDocument).text(currentTermIndex);
		$("#highlight-total-count", _highlight.scrollDocument).text(termCount);
	}
}

var _highlight = {
	scrollDocument: document,
	scrollWindow: window,
    atLeastOneTerm: false,
    originalSearchText: "",
    activeTerms: [],

	editHighlight: function() {
		$.ajax({
	        url: "/search/parseSearchUrlHash",
	        data: {
	            hash: $.deparam.querystring().searchUrlHash
	        },
	        timeout: 2000,
	        success: function(data) {
	            var queries = [];
	
	            var texts = data.text;
	            if (texts) {
	                for (var i = 0; i < texts.length; i++) {
	                    queries.push(texts[i]);
	                }
	            }
	
	            var noteups = data.noteups;
	            if (noteups) {
	                for (var i = 0; i < noteups.length; i++) {
	                    queries.push('"' + noteups[i].display + '"');
	                }
	            }
	
	            $("#hiBar", _highlight.scrollDocument).find("#hiBar-highlight-widget-search-terms-edit-input", _highlight.scrollDocument).val(queries.join(" "));
	            _highlight.displayNone($("#hiBar", _highlight.scrollDocument).find("#hiBar-highlight-widget-search-terms-container", _highlight.scrollDocument));
	            _highlight.displayFlex($("#hiBar", _highlight.scrollDocument).find("#hiBar-highlight-widget-search-terms-edit", _highlight.scrollDocument));
	
	            _highlight.originalSearchText = queries.join(" ");
	            
	            $("#hiBar-highlight-widget-search-terms-edit-input", _highlight.scrollDocument).off("keyup");
	            $("#hiBar-highlight-widget-search-terms-edit-input", _highlight.scrollDocument).focus();
	            
	            setTimeout(function () {
					// need to give some time, so the keyup from the focus is not triggered
					$("#hiBar-highlight-widget-search-terms-edit-input", _highlight.scrollDocument).on("keyup", _highlight.handleKeyPressed);
				}, 500);
	        },
	        error: function() {
	            _highlight.displayFlex($("#hiBar", _highlight.scrollDocument).find("#hiBar-highlight-widget-search-terms-container", _highlight.scrollDocument));
	            _highlight.displayNone($("#hiBar", _highlight.scrollDocument).find("#hiBar-highlight-widget-search-terms-edit", _highlight.scrollDocument));
	        }
	    });
	},
	
	submitNewHighlight: function() {
	    if (_highlight.originalSearchText === $("#hiBar-highlight-widget-search-terms-edit-input", _highlight.scrollDocument).val()) {
	        if (_highlight.atLeastOneTerm == true) {
				_highlight.displayFlex($("#hiBar", _highlight.scrollDocument).find("#hiBar-highlight-widget-search-terms-container", _highlight.scrollDocument));
		        _highlight.displayNone($("#hiBar", _highlight.scrollDocument).find("#hiBar-highlight-widget-search-terms-edit", _highlight.scrollDocument));
			}
	        return;
	    }
	
	    $("#hiBar-highlight-widget-search-terms-edit-input", _highlight.scrollDocument).prop('disabled', true);
	    $.ajax({
	        url: "/search/getSearchUrlHash",
	        data: {
	            query: $("#hiBar-highlight-widget-search-terms-edit-input", _highlight.scrollDocument).val()
	        },
	        timeout: 2000,
	        success: function(data) {
	            var offset = $(document).scrollTop();
	            var url = $.param.querystring(window.location.href, {searchUrlHash: data, offset: offset});
	            window.location.href = url;
	        },
	        error: function() {
	            $("#hiBar-highlight-widget-search-terms-edit-input", _highlight.scrollDocument).prop('disabled', false);
	            _highlight.displayFlex($("#hiBar", _highlight.scrollDocument).find("#hiBar-highlight-widget-search-terms-container", _highlight.scrollDocument));
	            _highlight.displayNone($("#hiBar", _highlight.scrollDocument).find("#hiBar-highlight-widget-search-terms-edit", _highlight.scrollDocument));
	        }
	    });
	},
	
	cancelEditHighlight: function() {
		_highlight.displayFlex($("#hiBar", _highlight.scrollDocument).find("#hiBar-highlight-widget-search-terms-container", _highlight.scrollDocument));
	    _highlight.displayNone($("#hiBar", _highlight.scrollDocument).find("#hiBar-highlight-widget-search-terms-edit", _highlight.scrollDocument));
	},
	
	handleKeyPressed: function(e) {
		if (e.which === 13) {
            _highlight.submitNewHighlight();
        } else if (e.which === 27) {
            _highlight.cancelEditHighlight();
        }
	},
	
	createTermsCheckboxes: function(terms, highlightMatch, highlighter) {
		$.each(terms, function(i, term) {
	        if (!term.isPresentInDocument && highlightMatch) {
	            return true;
	        }
	
			let labelDomElement = null;
			if (term.isPresentInDocument) {
				// default label
				let termId = term.cssClass.substring(term.cssClass.indexOf('T') + 1);
				
		        labelDomElement = $(
		            "<label id='solexTerm" + termId + "' " +
		                   "class='lexumSolrTermLabel lexumSolrTermInBar " + term.cssClass + "' " +
		                   "for='lexumSolrCheck" + termId + "' >" +
		            "<input id='lexumSolrCheck" + termId + "' " +
		                    "type='checkbox' " +
		                    "termid='" + termId + "' termindex='" + i + "' /> " + term.label +
		            "</label>");
		            
		        var checkedInput = $(labelDomElement).find("input");
		        // check the box if highlight is ON
		        if (_highlight.activeTerms[i]) {
		            checkedInput.prop("checked", true);
		        }
		        else {
		            labelDomElement.addClass("solexNohl");
		        }
		
		        // Handle checkbox change listener (check uncheck)
		        $(checkedInput).on("change", function() {
		            _highlight.labelChanged(checkedInput, highlighter);
		        });
	        
	        	// could not find a way to disable stopwords by default, so we trigger a change manually
		        if (term.isStopWord) {
		        	labelDomElement.addClass("solexNohl");
					checkedInput.prop("checked", false).change();
				}
			} else {
				// missing term label without input
				labelDomElement = $(
	            "<label class='lexumSolrTermLabel lexumSolrTermInBar solexMissingTerm'>" + term.label +
	                   "<sup><span><i aria-hidden='true' class='fas fa-question-circle solexMissingTermIcon'></i></span></sup>" +
	            "</label>");
			}
	
	        $("#hiBar-highlight-widget-search-terms", _highlight.scrollDocument).append(labelDomElement);
	    });
	},
	
	labelChanged: function (checkedInput, highlighter) {
		let termId = checkedInput.attr("termid");
		let termIndex = checkedInput.attr("termindex");
		
		var active = _highlight.isChecked(checkedInput);
	    _highlight.activeTerms[termIndex] = active;
		var label = $("#solexTerm"+termId, _highlight.scrollDocument);
		var termsInDocument = $(".solexT"+termId);
		if (active) {
			label.removeClass("solexNohl");
			termsInDocument.removeClass("solexNohl");
		}
		else {
			label.addClass("solexNohl");
			termsInDocument.addClass("solexNohl");
		}
	
	    highlighter.setActiveTerms(_highlight.activeTerms);
	},
	
	isChecked: function(checkbox) {
		if (checkbox === undefined) {
	        // The term is not in the document
	        return false;
	    }
	    return checkbox.is(":checked");
	},
	
	displayFlex: function(element) {
		element.addClass("display-flex");
    	element.removeClass("display-none");
	},
	
	displayNone: function(element) {
		element.removeClass("display-flex");
    	element.addClass("display-none");
	},
	
	scrollToPage: function(hasHeader, firstPage, totalPages) {
		let firstDataPageValue = $(".pdf-viewer-page").first().data("page"); // can start at 0 or 1
		let hiBarPageInput = $("#hiBar-page-widget-page-number-input", _highlight.scrollDocument);
        let targetPage = hiBarPageInput.val();

		let dataPageToScroll = null;
        if (!targetPage || targetPage < firstPage) {
			targetPage = firstPage;
            dataPageToScroll = firstDataPageValue;
        }
        else if (targetPage > firstPage + totalPages) {
			targetPage = firstPage + totalPages -1;
            dataPageToScroll = firstDataPageValue + totalPages - 1;
        } else {
			dataPageToScroll = targetPage - firstPage + firstDataPageValue;
		}

        hiBarPageInput.val(targetPage);
		
		let elementToScroll = $(".pdf-viewer-page[data-page=" +  dataPageToScroll + "]");
		if (elementToScroll != null && elementToScroll.length > 0) {
			let scrollPos = elementToScroll.offset().top;
			if (hasHeader == true) {
				scrollPos = scrollPos - $("#canliiHeader").height();
			} else {
				scrollPos = scrollPos + $("#searchDocumentFrame", _highlight.scrollDocument).offset().top - $("#canliiHeader", _highlight.scrollDocument).height() - $("#framedTopBar", _highlight.scrollDocument).outerHeight(true);
			}
			
			$("html, body", _highlight.scrollDocument).animate({ scrollTop: scrollPos }, 'slow');
		}
	},
	
	updatePageInput: function(firstPage) {
		let textLayers = $(".pdf-viewer-page:above-the-middle");

        if (textLayers && textLayers[0]) {
            let pageNumber = parseInt(textLayers[0].getAttribute("data-page"));
			let firstDataPageValue = $(".pdf-viewer-page").first().data("page"); // can start at 0 or 1
			let potentialNextPage = pageNumber + firstPage - firstDataPageValue;
			if (potentialNextPage >= firstPage) {
				$("#hiBar-page-widget-page-number-input", _highlight.scrollDocument).val(potentialNextPage);
			}
        }
	}
};
