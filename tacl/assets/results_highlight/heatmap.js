var n = 10;
var xr = 0;
var xg = 0;
var xb = 255;
var yr = 255;
var yg = 0;
var yb = 0;
var max = $("input").length;

function recalculateHeat (textname, change) {
    $("span[data-texts~='" + textname.replace('\\', '\\\\') + "']").each(function () {
        $(this).attr("data-count", function () {
            return parseInt($(this).attr("data-count")) + change;
        });
        val = parseInt($(this).attr("data-count"));
        if (val == 0) {
            clr = 'rgb(0,0,0)';
        } else {
            pos = parseInt((Math.round((val/max)*n)).toFixed(0));
            red = parseInt((xr + ((pos * (yr - xr)) / (n-1))).toFixed(0));
            green = parseInt((xg + ((pos * (yg - xg)) / (n-1))).toFixed(0));
            blue = parseInt((xb + ((pos * (yb - xb)) / (n-1))).toFixed(0));
            clr = 'rgb(' + red + ',' + green + ',' + blue + ')';
        }
        $(this).css({color:clr});
    });
}

$(document).ready(function () {
    $("input").on("click", function (event) {
        var $textname = $(this).val();
        var $change;
        if ($(this).prop('checked')) {
            $change = 1;
        } else {
            $change = -1;
        }
        recalculateHeat($textname, $change);
    });
});
