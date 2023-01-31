var TooltipUtils = {

	createTooltip : function(element, tooltipContent, options) {
		var options = options || {};
		var defaults = {
			afterUpdate : function(content, element) {
				$(content).addClass("bootstrap");
			}
		};
		var opt = _.extend(defaults, options);
		Tipped.create(element, tooltipContent, opt);
	},

	createTip : function(elementToTip) {
		this.createTooltip(elementToTip, "/getLegislationTipContent.do", {
              position: 'topleft',
              showOn: 'click',
              hideOn: 'click-outside',
              closeButton: true,
			  ajax: {
			  	type: 'post',
			  	data: { section: $(elementToTip).attr("section"),
						subsection: $(elementToTip).attr("subsection"),
						alinea: $(elementToTip).attr("alinea"),
						origin: origin,
						linkToOtherLangWithoutSection: linkToOtherLangWithoutSection,
						citationText: citationText,
						lang: lang}
			  }
        });

		Tipped.show(elementToTip);
		lastTippedElement = elementToTip;
	},
	
	displayCitationTextarea : function(citationTextContainerId) {
		// jquery does not support retrieving an element by id with special characters (like dots), so we use straight javascript
		var citationElement = document.getElementById(citationTextContainerId);
		$(citationElement).toggle(); 
		if (!isSmartphone()) {
			this.ajustContainerHeight(citationTextContainerId);
		}
		Tipped.refresh(lastTippedElement); 
		$(citationElement).select();
	},

	ajustContainerHeight : function(id, maxHeight) {
	   var text = id && id.style ? id : document.getElementById(id);
	   if (!text)
	      return;

	   /* Accounts for rows being deleted, pixel value may need adjusting */
	   if (text.clientHeight == text.scrollHeight) {
	      text.style.height = "30px";
	   }

	   var adjustedHeight = text.clientHeight;
	   if (!maxHeight || maxHeight > adjustedHeight) {
	      adjustedHeight = Math.max(text.scrollHeight, adjustedHeight);
	      if (maxHeight)
	         adjustedHeight = Math.min(maxHeight, adjustedHeight);
	      if (adjustedHeight > text.clientHeight)
	         text.style.height = adjustedHeight + "px";
	   }
	},
	
	createHelpTooltip : function(elem, templateSelector, containerSelector) {
		let template = document.querySelector(templateSelector);
		let content = template.innerHTML;
		// need to trigger this manually since the bootstrap tooltips close if the mouse goes inside the content
		$(elem).tooltip({
			trigger: 'manual',
			//animation: false,
			placement : 'bottom',
			html: true,
			title: content,
			container: $(containerSelector).first()
		}).on('mouseenter', function () {
		    var _this = this;
		    $(this).tooltip('show');
		    $('.tooltip').on('mouseleave', function () {
		        $(_this).tooltip('hide');
		    });
		}).on('mouseleave', function () {
		    var _this = this;
		    setTimeout(function () {
		        if (!$('.tooltip:hover').length) {
		            $(_this).tooltip('hide');
		        }
		    }, 50);
		}).on('keypress', function (event) {
			if (event.keyCode === 13) {
				var _this = this;
				$(_this).tooltip('toggle');
			}
		});
	}

};

