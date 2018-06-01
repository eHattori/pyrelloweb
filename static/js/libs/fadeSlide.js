var FadeSlide = function(options) {
    var that = this;
    
    var defaults = {
        duration: 4000
    }

    this.options = $.extend(defaults, options);
    that.autoInterval = null;
    that.autoTime = this.options.duration;
    that.itens = this.options.itens;
    that.index = 0;

    that.itens.css({'z-index' : 1, 'opacity' : 0});
    that.itens.eq(this.index).css({ 'z-index' : 2, 'opacity' :1 });

    that.goToIndex(0);
    that.auto();
};

FadeSlide.prototype = {

    goToIndex:function(index, complete) {
        var that = this;
        if ( index != 0 && index ==  that.index ) {
            return;
        }

        clearInterval(that.autoInterval);

        that.itens.eq(index).css({'z-index':3});
        that.itens.eq(index).stop().animate({'opacity': 1}, 600, function(){
            that.itens.not( that.itens.eq(index) ).css({ 'z-index' : 1, 'opacity' : 0 });
            that.itens.eq(index).css({'z-index':2});
            that.index = index;
            that.auto();
            if ( complete && typeof complete ) {
                complete.call(this);
            }
        });
    },

    getNextIndex:function(){
        var that = this;
        return that.index+1 >= that.itens.length ? 0 : that.index+1;
    },

    auto: function() {
        var that = this;
        clearInterval(that.autoInterval);
        that.autoInterval = setTimeout(function(){
            var index = that.getNextIndex();
            that.goToIndex(index);
        }, that.autoTime);
    }

};