var ImageLoader = function(images) {
    this.images = $.makeArray(images);
};

ImageLoader.prototype = {
    preloadImage: function(img, complete) {
        var src = img.attr('data-src');
        if ( src ) {
            img.on('load', function(){
                img.removeAttr('data-src');
                if ( typeof complete === 'function' ) {
                    complete();
                }
            });
            img.attr('src', src);
        } else {
            if ( typeof complete === 'function' ) {
                complete();
            }
        }
    },

    removeItem: function( item ) {
        this.images.splice($.inArray(item, this.images), 1);
    },

    preloadImages: function(complete) {
        var that = this;
        if( this.images.length ) {
            this.preloadImage($(this.images[0]), function(){
                that.removeItem(that.images[0]);
                that.preloadImages(complete);
            });
        } else {
            if ( typeof complete === 'function' ) {
                complete();
            }
        }
    }
};
