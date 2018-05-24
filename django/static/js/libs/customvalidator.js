function FormValidator(form, rules, options) {
    this.form = form;
    this.settings = $.extend({
        // focusCleanup: true,
        rules: rules,

        highlight: function(element, errorClass, validClass) {
            $(element).addClass('error-field');
            $(element).parents('.form-row').addClass(errorClass).removeClass(validClass);
        },

        unhighlight: function(element, errorClass, validClass) {
            $(element).removeClass('error-field');
            $(element).parents('.form-row').removeClass(errorClass).addClass(validClass);
        },

        errorPlacement: function(error, element) {
            element.nextAll('.error-message').remove();
            element.after('<div class="error-message c-red">'+error.html()+'</div>');
        },

        success: function(label, input) {
            $(input).nextAll('.error-message').remove();
        },

        invalidHandler: function() {
            setTimeout(function(){
                $('[data-bl="true"]').buttonloading('disable');
            }, 300);
        },

        submitHandler: function() {
            // form.submit();
        }
    }, options);

    this.validator = this.form.validate(this.settings);
}

FormValidator.prototype = {

};
