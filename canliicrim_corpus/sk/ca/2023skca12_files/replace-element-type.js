/**
 * Created by bujancav on 10/10/14.
 *
 * @see http://stackoverflow.com/questions/8584098/how-to-change-an-element-type-using-jquery
 */

(function($) {
    $.fn.replaceElementType = function(newType) {
        var attrs = {};

        $.each(this[0].attributes, function(idx, attr) {
            attrs[attr.nodeName] = attr.value;
        });

        this.replaceWith(function() {
            return $("<" + newType + "/>", attrs).append($(this).contents());
        });
    };

    $.fn.replaceMultipleElementType = function(newType) {
        var newElements = [];

        $(this).each(function() {
            var attrs = {};

            $.each(this.attributes, function(idx, attr) {
                attrs[attr.nodeName] = attr.value;
            });

            var newElement = $("<" + newType + "/>", attrs).append($(this).contents());

            $(this).replaceWith(newElement);

            newElements.push(newElement);
        });

        return $(newElements);
    };
})(jQuery);