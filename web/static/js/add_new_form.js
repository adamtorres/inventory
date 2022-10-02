var form_name = "set this to the overall name of the form fields.  i.e. line_items, items, etc.";
var after_add_focus_suffix = "set this from page as it will likely be different for each use.";
var line_item_position_id = "line_item_position";
var formset_container_id = "set this to the id of the table or list that contains the forms.  No #";
function add_new_form(focus_suffix="") {
    empty_obj = $(`#${formset_container_id}`).find('#empty-form').clone()
    empty_obj.attr('id', null)

    total_forms = $(`#id_${form_name}-TOTAL_FORMS`)

    total_forms_value = parseInt(total_forms.val())
    focus_after_add_id = "";
    empty_obj.find('input, label, select, textarea, div, ul').each(function() {
        to_edit_attributes = ['id', 'name', 'for', 'aria-labelledby']
        if ((this.type === 'number') && (this.id.endsWith(`-${line_item_position_id}`))) {
            this.value = total_forms_value + 1;
        }
        for(var i in to_edit_attributes){
            attribute = to_edit_attributes[i]

            old_value = $(this).attr(attribute)
            if(old_value){
                new_value = old_value.replace(/__prefix__/g, total_forms_value)
                $(this).attr(attribute, new_value)
            }
            if (focus_suffix !== "") {
                if (this.id.endsWith(focus_suffix)){
                    focus_after_add_id = this.id;
                }
            }
        }
    })

    total_forms.val(total_forms_value + 1)
    empty_obj.removeClass('empty-form');
    empty_obj.show()
    /* TODO: make work with list and table "> tbody:last-child" for table */
    $(`#${formset_container_id}`).append(empty_obj);
    if ((focus_suffix !== "") && (focus_after_add_id)) {
        document.getElementById(focus_after_add_id).focus()
    }
}

$('.add-new-form').click(function(e) {
    e.preventDefault();
    add_new_form(after_add_focus_suffix);
});
