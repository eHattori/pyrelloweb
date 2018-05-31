/*
* jQuery togglepanel
*
* Copyright (c) 2013 Carlos Roberto Gomes Junior
* http://carlosroberto.name/
* 
* Licensed under a Creative Commons Attribution 3.0 License
* http://creativecommons.org/licenses/by-sa/3.0/
*
* Version: 0.0.1
*/
(function($) {
    var defaults = {
        buttonSelector: '[data-togglepanel-button]',
        contentSelector: '[data-togglepanel-content]'
    };
    
    function TogglePanel (el, options) {

        if ( options ) {
            this.settings = $.extend(defaults, options);            
        } else {
            this.settings = defaults;
        }

        this.el = el;
        this.panelButton = $(this.settings.buttonSelector, el);
        this.panelContent = $(this.settings.contentSelector, el);
        this.panelButton.on('click', $.proxy(this, 'toggle'));
        this.panelGroup = $('[data-togglepanel-group="'+this.el.data('togglepanel-group')+'"]').not(this.el);
        
        if ( this.el.hasClass('disabled') || !this.el.hasClass('active') ) {
            this.panelContent.hide();
        } else if ( this.el.hasClass('active') ) {
            this.panelContent.show();
        }
    }
    
    TogglePanel.prototype = {
        _hideOthers: function() {
            this.panelGroup.togglepanel('hide');
        },

        show: function() {
            var that = this;
            
            this._hideOthers();

            that.el.trigger('beforeShow.togglepanel', [ that.panelButton, that.panelContent, that.panelGroup ]);
            this.panelContent.slideDown(function() {
                that.el.trigger('show.togglepanel', [ that.panelButton, that.panelContent, that.panelGroup ]);
                that.el.trigger('toggle.togglepanel', [ that.panelButton, that.panelContent, that.panelGroup ]);
            });
            this.el.removeClass('disabled');
            this.el.addClass('active');
        },

        hide: function() {
            var that = this;
            that.el.trigger('beforeHide.togglepanel', [ that.panelButton, that.panelContent, that.panelGroup ]);
            this.panelContent.slideUp(function() {
                that.el.trigger('hide.togglepanel', [ that.panelButton, that.panelContent, that.panelGroup ]);
                that.el.trigger('toggle.togglepanel', [ that.panelButton, that.panelContent, that.panelGroup ]);
            });
            this.el.addClass('disabled');
            this.el.removeClass('active');
        },

        toggle: function( event ) {
            if ( event ) {
                event.preventDefault();
            }
            var that = this;
            if ( this.el.hasClass('disabled') || !this.el.hasClass('active') ) {
                this.show();
            } else {
                this.hide();
            }
        }
    };
    
    $.fn.togglepanel = function( method ) {
        var args = arguments;

        return this.each(function() {

            if ( !$.data(this, 'TogglePanel') ) {
                $.data(this, 'TogglePanel', new TogglePanel($(this), method));
                return;
            }
            
            var api = $.data(this, 'TogglePanel');
            
            if ( typeof method === 'string' && method.charAt(0) !== '_' && api[ method ] ) {
                api[ method ].apply( api, Array.prototype.slice.call( args, 1 ) );
            } else {
                $.error( 'Method ' +  method + ' does not exist on jQuery.TogglePanel' );
            }
        });
    };
})(jQuery);

$(function() {
    $('[data-togglepanel]').togglepanel();
});