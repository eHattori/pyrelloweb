(function($) {
    var EasyTabs = function(el) {
        this.el = el;
        this.tabsNav = $('[data-easytabs-nav]', this.el);
        this.navItens = $('[data-easytabs-nav-item]', this.el);
        this.tabsPanel = $('[data-easytabs-panel]', this.el);
        this.panelItens = $('[data-easytabs-panel-item]', this.el);

        this.navItens.eq(0).addClass('active');
        this.panelItens.eq(0).addClass('active');

        this.panelItens.not(this.panelItens.eq(0)).hide();

        this.navItens.on('click', $.proxy(this, 'showTabHandler'));
    }

    EasyTabs.prototype = {
        showTabHandler: function( event ) {
            event.preventDefault();
            var el, index;
            el = $(event.currentTarget);
            index = this.navItens.index(el);

            this.navItens.removeClass('active');
            el.addClass('active');

            this.panelItens.not(this.panelItens.eq(index)).hide();
            this.panelItens.eq(index).show();
        }
    }

    $(function() {
        $('[data-easytabs]').each(function() {
            new EasyTabs( $(this) );
        });
    });
})(jQuery);