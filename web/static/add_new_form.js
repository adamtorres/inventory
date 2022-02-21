function add_new_form() {

    empty_obj = $('#empty-row').clone()
    empty_obj.attr('id', null)

    total_forms = $('#id_items-TOTAL_FORMS')

    total_forms_value = parseInt(total_forms.val())
    logit(`total_forms_value = ${total_forms_value}.`)

    empty_obj.find('input, label, select, textarea, div, ul').each(function(){
        to_edit_attributes = ['id', 'name', 'for', 'aria-labelledby']

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
    $('#formset-table > tbody:last-child').append(empty_obj);
}

$('.add-new-form').click(function(e) {
    logit("add-new-form.click!")
    e.preventDefault();
    logit("add-new-form.click! prevented default")
    add_new_form();
    logit("add-new-form.click! added form")
});
