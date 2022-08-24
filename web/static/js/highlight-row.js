let highlight_container_id = "id-of-container";  // no leading #

// Add the needed style to head.
$("<style>").prop("type", "text/css").html(".selected-row {background-color: yellow;}").appendTo("head");

function is_row_or_div(row) {
    return (row.is("tr") ? "td" : "div");
}
function clear_highlight() {
    let table_body = $(`#${highlight_container_id}`);
    table_body.find(".filtered-item-top").each(function() {
        let row = $(this);
        let child_tag = is_row_or_div(row);
        row.find(child_tag).each(function() {
            let cell = $(this);
            cell.removeClass('selected-row');
        });
        row.removeClass('selected-row');
    });
}
function highlight_row(_row) {
    clear_highlight();
    let row = $(_row);
    let child_tag = is_row_or_div(row);
    row.find(child_tag).each(function() {
        let cell = $(this);
        cell.addClass('selected-row');
    });
    row.addClass('selected-row');
}
function is_highlighted(row) {
    return row.hasClass('selected-row');
}
function get_highlighted_row() {
    let table_body = $(`#${highlight_container_id}`);
    let selected_row = null;
    table_body.find(".filtered-item-top").each(function() {
        let row = $(this);
        if (is_highlighted(row)) {
            selected_row = row;
        }
    });
    return selected_row;
}
