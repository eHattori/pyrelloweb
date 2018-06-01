/*
* jQuery ShowMore
* http://carlosrberto.github.com/jquery-showmore/
*
* Copyright (c) 2014 Carlos Roberto Gomes Junior
* http://carlosroberto.name/
*
* Licensed under the MIT License
* http://opensource.org/licenses/MIT
*
* Version: 0.1
*/


(function($) {
    var defaults, pluginName, ShowMore;

    defaults = {
        target: 'li',
        offset: 3,
        btnMore: null
    };

    pluginName = 'showmore';

    ShowMore = function(el, options) {
        if ( options ) {
            this.settings = $.extend(defaults, options);
        } else {
            this.settings = defaults;
        }

        this.el = $(el);
        this.targets = this.el.find(this.settings.target);
        this.targets.slice(this.settings.offset, this.targets.length).hide();
        this.sliceCounter = this.settings.offset;

        if (this.sliceCounter >= this.targets.length) {
            this.settings.btnMore.off('click.'+pluginName);
            this.settings.btnMore.fadeOut();
        }

        this._initEvents();
    };

    ShowMore.prototype = {
        _initEvents: function() {
            var btn  = this.settings.btnMore;
            btn.on('click.'+pluginName, $.proxy(function(event){
                event.preventDefault();
                this._slice();
            }, this));
        },

        _slice: function() {
            var btn  = this.settings.btnMore;
            this.sliceCounter += this.settings.offset;
            if (this.sliceCounter >= this.targets.length) {
                this.sliceCounter = this.targets.length;
                btn.off('click.'+pluginName);
                btn.fadeOut();
            }
            this.targets.slice(0, this.sliceCounter).show();
        },

        destroy: function() {
            this.el.off('.'+pluginName);
            $.removeData(this.el, pluginName);
        }
    };


    $.fn[pluginName] = function( method ) {
        var args = arguments;

        return this.each(function() {

            if ( !$.data(this, pluginName) ) {
                $.data(this, pluginName, new ShowMore(this, method));
                return;
            }

            var api = $.data(this, pluginName);

            if ( typeof method === 'string' && method.charAt(0) !== '_' && api[ method ] ) {
                api[ method ].apply( api, Array.prototype.slice.call( args, 1 ) );
            } else {
                $.error( 'Method ' +  method + ' does not exist on jQuery.'+pluginName );
            }
        });
    };
})(jQuery);
