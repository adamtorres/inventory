function is_date_field(possible_a_date_field){
    if (possible_a_date_field.includes('date')) {
        return true;
    }
    if (['created', 'modified'].includes(possible_a_date_field)) {
        return true;
    }
    return false
}
function is_date_value(possibly_a_date_value) {
    // Specifically made to test if a string is a date string.  Not meant to be a generic date function.
    if (!(typeof(possibly_a_date_value) === typeof("string"))) {
        return false;
    }
    // if (!(['-', '/'].some(date_sep_char => possibly_a_date.includes(date_sep_char)))){
    //     return false;
    // }
    return (!isNaN(Date.parse(possibly_a_date_value)));
}
function format_date_str(full_date_str) {
    // Given a date string as provided by Django/Postgresql, convert it to American M/D/Y.
    // "2022-02-09T01:36:04.239259-07:00" to "2/9/2022"
    let d = new Date(full_date_str);
    return `${d.getMonth()+1}/${d.getDate()}/${d.getFullYear()}`;
}
