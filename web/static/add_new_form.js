


$('.add-new-form').click(function(e) {
    e.preventDefault()

    empty_obj = $('#empty-row').clone()
    empty_obj.attr('id', null)

    total_forms = $('#id_items-TOTAL_FORMS')

    total_forms_value = parseInt(total_forms.val())

    empty_obj.find('input, label, select, textarea').each(function(){
        to_edit_attributes = ['id', 'name', 'for']

        for(var i in to_edit_attributes){
            attribute = to_edit_attributes[i]

            old_value = $(this).attr(attribute)
            if(old_value){
                new_value = old_value.replace(/__prefix__/g, total_forms_value)
                $(this).attr(attribute, new_value)
            }

        }
    })

    total_forms.val(total_forms_value + 1)

    empty_obj.show()
    empty_obj.insertAfter($('#empty-row'))
});
