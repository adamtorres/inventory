// id of the element to dump log entries.
var log_element_id = "on-page-log";
var log_element = undefined;

function logit(stuff, clear=false) {
    if (log_element === undefined) {
        log_element = $(`#${log_element_id}`);
    }
    if (clear) {
        log_element.empty();
    }
    log_element.prepend(stuff + "\n");
}
