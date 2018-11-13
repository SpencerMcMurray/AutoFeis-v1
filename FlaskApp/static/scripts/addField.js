function startAgeIn(name) {
    var select = "<select name='" + name + "StartAge[]'>";
    for(i=0; i < 100; i++) {
        iStr = i.toString();
        select += "<option value='" + iStr + "'>" + iStr + "</option>";
    }
    select += "</select>";
    return select;
}

function endAgeIn(name) {
    var select = "<select name='" + name + "EndAge[]'>";
    for(i=0; i < 100; i++) {
        iStr = i.toString();
        select += "<option value='" + iStr + "'>" + iStr + "</option>";
    }
    select += "</select>";
    return select;
}

function genderIn(name) {
    var select = "<select name='" + name + "Gender[]'>";
    select += "<option value='all'>All</option>";
    if(name == "FG") {
        select += "<option value='mixed'>Mixed Only</option>";
    }
    select += "<option value='female'>Female Only</option>";
    select += "<option value='male'>Male Only</option>";
    select += "</select>";
    return select;
}

function levelIn(name) {
    var select = "<select name='" + name + "Level[]'>";
    select += "<option value='All'>All Levels</option>";
    select += "<option value='Championship'>All Championship Levels</option>";
    select += "<option value='Open Championship'>Open Championship</option>";
    select += "<option value='Preliminary Championship'>Preliminary Championship</option>";
    select += "<option value='Grades'>Grades Levels</option>";
    select += "<option value='Non-Dancer'>Non-Dancer</option>";
    select += "</select>";
    return select;
}

var nameFG = "FG";
var nameTR = "TR";
var nameTNN = "TNN";

$(document).ready(function() {
    $('#addFG').click(function() {
        alert("Add FG clicked");
        $('#FG tr:last').after('<tr><td>' + startAgeIn(nameFG) + '</td><td>' + endAgeIn(nameFG) + '</td><td>' + genderIn(nameFG) + '</td></tr>');
    });

    $('#addTR').click(function() {
        alert("Add TR clicked");
        $('#TR tr:last').after('<tr><td>' + levelIn(nameTR) + '</td><td>' + startAgeIn(nameTR) + '</td><td>' + endAgeIn(nameTR) + '</td><td>' + genderIn(nameTR) + '</td></tr>');
    });

    $('#addTNN').click(function() {
        alert("Add TNN clicked");
        $('#TNN tr:last').after('<tr><td>' + startAgeIn(nameTNN) + '</td><td>' + endAgeIn(nameTNN) + '</td></tr>');
    });
});