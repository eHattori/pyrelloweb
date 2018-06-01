/*
* jQuery loadingbutton
*
* Copyright (c) 2013 Carlos Roberto Gomes Junior
* http://carlosroberto.name/
*
* Licensed under a Creative Commons Attribution 3.0 License
* http://creativecommons.org/licenses/by-sa/3.0/
*
* Version: 1.0.0
*/

(function($) {
    var defaults = {
        imageLoader: window.__STATIC_URL__ ? window.__STATIC_URL__ + 'v2/img/common/loader_button.gif' : ''
    };

    function ButtonLoading (button, options) {
        if ( options ) {
            this.settings = $.extend({}, defaults, options);
        } else {
            this.settings = defaults;
        }
        this.button = $(button);
        this.wrapper = $('<span class="button-loading-wrapper"></span>');
        this.image = $('<img class="button-loading-image" src="'+this.settings.imageLoader+'" alt="">');

        this._preloadLoader();
        this._wrap();
        this._events();
    }

    ButtonLoading.prototype = {
        _events: function() {
            $('body').on('click.buttonloading', '.button-loading-enable', function( event ){
                event.preventDefault();
            });
            this.button.on('click.buttonloading', $.proxy(this.enable, this));
        },

        _preloadLoader: function() {
            var img = new Image();
            img.src = this.settings.imageLoader;
        },

        _wrap: function() {
            this.button.addClass('button-loading');
            this.button.wrapInner(this.wrapper);
            this.button.find('.button-loading-wrapper').after(this.image);
        },

        enable: function() {
            setTimeout($.proxy(function(){
                this.button.addClass('button-loading-enable');
                if ( this.button.is('button') || this.button.is('input') ) {
                    this.button.attr('disabled', 'disabled');
                }
            }, this), 10);
        },

        disable: function() {
            setTimeout($.proxy(function() {
                this.button.removeClass('button-loading-enable');
                if ( this.button.is('button') || this.button.is('input') ) {
                    this.button.removeAttr('disabled', 'disabled');
                }
            },this), 50);
        }
    };

    $.fn.buttonloading = function( method ) {
        var args = arguments;

        return this.each(function() {

            if ( !$.data(this, 'ButtonLoading') ) {
                $.data(this, 'ButtonLoading', new ButtonLoading(this, method));
                return;
            }

            var api = $.data(this, 'ButtonLoading');

            if ( typeof method === 'string' && method.charAt(0) !== '_' && api[ method ] ) {
                api[ method ].apply( api, Array.prototype.slice.call( args, 1 ) );
            } else {
                $.error( 'Method ' +  method + ' does not exist on jQuery.ButtonLoading' );
            }
        });
    };
})(jQuery);
