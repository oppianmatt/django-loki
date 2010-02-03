function saveconfig(type, bot, form_name) {
    $.post('/ajax/config/' + type + '/save/' + bot + '/', $("form#" + form_name).serialize(), function(data, textStatus) {
	   if(textStatus == 'success') {
	       $("div#" + type + "s div#new" + type).empty();
	       var new_config = $('<div/>').load('/ajax/config/' + type + '/load/' + data + '/');
	       new_config.insertBefore($("div#" + type + "s div#new" + type));
	   } else {
	       alert(data);
	   };
    });
};
function deleteconfig(type, id) {
    var id_name = type + '_id';
    $.post('/ajax/config/' + type + '/delete/', { configid: id }, function(data, textStatus) {
	   if(textStatus == 'success') {
	       $("div#" + type + "s div#" + type + id).remove();
	   } else {
	       alert(data);
	   };
    });
};
function toggleconfig(type, action, id) {
    if ($("#" + type + "_display" + id).is(":visible")) {
	$("#" + type + "_display" + id).slideUp(500);
    }
    if ($("#" + type + "_edit" + id).is(":visible")) {
	$("#" + type + "_edit" + id).slideUp(500);
    }
    if ($("#" + type + "_delete" + id).is(":visible")) {
	$("#" + type + "_delete" + id).slideUp(500);
    }
    $("#" + type + "_" + action + id).slideDown(500);
};
