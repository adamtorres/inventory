var form_name = "set this to the overall name of the form fields.  i.e. line_items, items, etc.";
var after_add_focus_suffix = "set this from page as it will likely be different for each use.";
var line_item_position_id = "line_item_position";
var formset_container_id = "set this to the id of the table or list that contains the forms.  No #";
var copy_from_previous = "list of fields to copy from previous form";

function add_new_form(focus_suffix="") {
    let formset_container = $(`#${formset_container_id}`);
    let empty_obj = formset_container.find('#empty-form').clone();
    empty_obj.attr('id', null);

    let total_forms = $(`#id_${form_name}-TOTAL_FORMS`);

    let total_forms_value = parseInt(total_forms.val());
    empty_obj.attr('data-form-number', total_forms_value);
    let focus_after_add_id = "";
    empty_obj.find('input, label, select, textarea, div, ul').each(function() {
        let to_edit_attributes = ['id', 'name', 'for', 'aria-labelledby']
        if ((this.type === 'number') && (this.id.endsWith(`-${line_item_position_id}`))) {
            this.value = total_forms_value + 1;
        }
        for(let i in to_edit_attributes){
            let attribute = to_edit_attributes[i]

            let old_value = $(this).attr(attribute)
            if(old_value){
                let new_value = old_value.replace(/__prefix__/g, total_forms_value)
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
    formset_container.append(empty_obj);
    if (total_forms_value > 0) {
        console.log(`Copy fields from previous form. ${copy_from_previous}`);
        let prev_form_num = total_forms_value - 1;
        for(let i in copy_from_previous){
            let field = copy_from_previous[i];
            let prev_key = `id_${form_name}-${prev_form_num}-${field}`;
            let cur_key = `id_${form_name}-${total_forms_value}-${field}`;
            let prev_field = $(`#${prev_key}`);
            let cur_field = $(`#${cur_key}`);
            console.log(prev_field);
            console.log(cur_field);
            console.log(`Copy ${field} / ${prev_key} / '${prev_field.val()}' to '${cur_key}'`);
            cur_field.val(prev_field.val());
        }
    }

    if ((focus_suffix !== "") && (focus_after_add_id)) {
        document.getElementById(focus_after_add_id).focus()
    }
    $('html, body').stop().animate({'scrollTop':$(`#${focus_after_add_id}`).offset().top}, 100);
}

$('.add-new-form').click(function(e) {
    e.preventDefault();
    add_new_form(after_add_focus_suffix);
});
