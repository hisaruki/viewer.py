(function () {
    var gt = 0;
    $("#gt").text(gt + 1);
    var autoslide = -1;
    var hori = true;
    var moving = null;
    var resize = function () {
        if (hori) {
            $("#main img").css("width", "inherit");
            $("#main img").css("height", $(window).height() + "px");
            $("#main").css("left", "inherit");
        } else {
            var w = $(window).width();
            if($("#sub").is(":visible")){
                w -= $("#sub").width();
            }
            $("#main img").css("width", w + "px");
            $("#main img").css("height", "inherit");
            $("#main").css("right", "inherit");
            $("#main").css("left", 0);
        }
        if (moving) {
            clearInterval(moving);
            moving = null;
        }
    }

    var speed = 10;

    var get_gt_as_is = function () {
        var rects = []
        $("#main img").each(function () {
            var rect = $(this)[0].getBoundingClientRect()
            if (hori) {
                rect = Math.ceil(rect.left);
            } else {
                rect = Math.ceil(rect.top);
            }
            rect = Math.ceil(rect);
            rect = Math.abs(rect)
            rects.push(rect);
        });
        return rects.indexOf(Math.min.apply(null, rects));
    }

    var focus = function (obj, linear) {
        if (moving) {
            clearInterval(moving);
            moving = null;
        }

        var rect = obj[0].getBoundingClientRect()
        if (hori) {
            rect = Math.ceil(rect.left);
        } else {
            rect = Math.ceil(rect.top);
        }

        var target = 0;
        //var target = $(window).width() - obj.width();
        if ($("#centering").hasClass("active")) {
            if (hori) {
                target = Math.ceil($(window).width() / 2);
            } else {
                target = Math.ceil($(window).height() / 2);
            }
        }

        var go = -1;
        if (!hori) {
            go = go * -1;
        }
        if (rect > target) {
            go = go * -1;
        }

        distance = Math.abs(target - rect);
        var myspeed = speed;
        if (!linear) {
            myspeed = 5;
        }

        moving = setInterval(function () {
            if (hori) {
                x = $("#main").css("right");
            } else {
                x = $("#main").css("top");
            }
            x = x.replace("px", "") - 0

            var rect = obj[0].getBoundingClientRect()
            if (hori) {
                rect = Math.ceil(rect.left);
            } else {
                rect = Math.ceil(rect.top);
            }

            distance = Math.abs(target - rect);

            if (distance > 16 && !linear) {
                go = go / Math.abs(go);
                go *= distance / 16;
            } else {
                go = go / Math.abs(go);
            }
            if (hori) {
                $("#main").css("right", x + go);
            } else {
                $("#main").css("top", x + go);
            }
            if (!distance) {
                clearInterval(moving);
                moving = null;
            }
        }, myspeed);

        $("#gt").text(gt + 1);
    }

    $("#tp").text($("#main img").length);

    $(window).on("resize load", function () {
        resize();
        focus($("#main img").eq(gt));
    });
    $("#main img").eq(0).attr("data-first", 1);
    resize();
    focus($("#main img").eq(gt));

    var slideshow = -1;
    setInterval(function () {
        if (slideshow > 0) {
            if (!moving) {
                if (gt == $("#main img").length - 1) {
                    focus($("#main img").eq(0), $("#between").hasClass("active"));
                } else {
                    focus($("#main img").eq($("#main img").length - 1), true);
                }
            }
            gt = get_gt_as_is();
            $("#gt").text(gt + 1);
        }
    }, 100);

    var autopage = -1;
    var apseq = 1;
    var skipped = 1;
    setInterval(function () {
        if (autopage > 0 && !moving) {
            apseq++;
            if ((apseq / speed) == Math.ceil(apseq / speed)) {
                gt += 1;
                if (gt >= $("#main img").length && $("#loop").hasClass("active")) {
                    gt = 0;
                }
                focus($("#main img").eq(gt));
            }
        }
        if (autoslide == 1 && skipped % (speed * 10) == 0){
            gt += 1;
            if (gt >= $("#main img").length && $("#loop").hasClass("active")) {
                gt = 0;
            }
            focus($("#main img").eq(gt));
            skipped = 1;
        }
        skipped++;
    }, 100);


    var change_speed = function (mode) {
        if (mode == "button") {
            speed = speed / 2;
            if (speed > 1) {
                speed = Math.ceil(speed);
            } else {
                speed = 40;
            }
        } else {
            if (mode > 0) {
                speed = Math.ceil(speed / 2);
            } else {
                speed = Math.ceil(speed * 2);
                if (speed > 40) {
                    speed = 40;
                }
            }
        }
        $("#speed var").text(Math.ceil(speed));
        $("#speed span").text("x" + (10 / speed));
        if (slideshow > 0 && moving) {
            clearInterval(moving);
            moving = null;
            slideshow = 1;
        }
    }

    $("#save").on("click", function () {
        var link = document.createElement('a');
        link.href = window.URL.createObjectURL(new Blob(['<html>' + $("html").html() + "</html>"]));
        link.download = filename + ".html";
        link.click();
    });


    $("#main img").on("click", function () {
        var img = '<img src="' + $(this).attr("src") + '">';
        $("#sub").show();
        $("#sub").empty();
        $("#sub").append($(img));
        resize();
    });

    $("#sub").on("click", function () {
        $(this).hide();
        resize();
    });

    $("#speed").on("click", function () {
        change_speed("button");
    });

    $("#centering, #between, #loop").on("click", function () {
        $(this).toggleClass("active");
        focus($("#main img").eq(gt));
    })

    $("#flex-direction").on("click", function () {
        $("#main").css("right", "0px");
        $("#main").css("top", "0px");
        var options = [
            "row-reverse",
            "row",
            "column",
            "column-reverse"
        ];
        var v = $(this).text();
        var i = options.indexOf(v);
        if (i + 1 < options.length) {
            i++;
        } else {
            i = 0;
        }
        v = options[i];

        if (i == 2 || i == 3) {
            hori = false;
        } else {
            hori = true;
        }

        $(this).text(v);
        $("#main").css("flex-direction", v)
        resize();
        focus($("#main img").eq(gt));
    })

    $("img").on("mouseup", function (e) {
        if (e.which == 2) {
            $(this).remove();
        }
    });


    $(document).on("keydown", function (e) {
        //right
        if (e.which == 37) {
            gt += 1;
            if (gt >= $("#main img").length) {
                gt = 0;
            }
            focus($("#main img").eq(gt));
        }
        //left
        if (e.which == 39) {
            gt -= 1;
            if (gt < 0) {
                gt = $("#main img").length - 1;
            }
            focus($("#main img").eq(gt));
        }
        //up
        if (e.which == 38) {
            gt -= 2;
            if (gt < 0) {
                gt = $("#main img").length - 1;
            }
            focus($("#main img").eq(gt));
        }
        //down
        if (e.which == 40) {
            gt += 2;
            if (gt >= $("#main img").length) {
                gt = 0;
            }
            focus($("#main img").eq(gt));
        }
    });

    $(document).on("keypress", function (e) {
        //1-9
        if (49 <= e.which && e.which <= 57) {
            var per = e.which - 49;
            gt = Math.ceil($("#main img").length / 9 * per);
            focus($("#main img").eq(gt));
        }


        //space
        if (e.which == 32) {
            if (slideshow > 0 && moving) {
                clearInterval(moving);
                moving = null;
            }
            slideshow = slideshow * -1;
        }

        //r
        if (e.which == 114) {
            /*
            if (autopage > 0 && moving) {
                clearInterval(moving);
                moving = null;
            }
            autopage = autopage * -1;
            */
        }

        //num
        if (49 <= e.which && e.which <= 57) {
        }
        //plus
        if (e.which == 43) {
        }
        //substruct
        if (e.which == 45) {
        }

        //j, d
        if (e.which == 106 || e.which == 97) {
            gt += 1;
            if (gt >= $("#main img").length) {
                gt = 0;
            }
            focus($("#main img").eq(gt));
        }
        //k, a
        if (e.which == 107 || e.which == 100) {
            gt -= 1;
            if (gt < 0) {
                gt = $("#main img").length - 1;
            }
            focus($("#main img").eq(gt));
        }

        //w
        if (e.which == 119) {
            gt -= 2;
            if (gt < 0) {
                gt = $("#main img").length - 1;
            }
            focus($("#main img").eq(gt));
        }
        //s
        if (e.which == 115) {
            gt += 2;
            if (gt >= $("#main img").length) {
                gt = 0;
            }
            focus($("#main img").eq(gt));
        }


        //h
        if (e.which == 104) {
        }
        //l
        if (e.which == 108) {
        }

        //plus
        if (e.which == 43) {
            change_speed(1);
        }
        //substruct
        if (e.which == 45) {
            change_speed(-1);
        }

        //enter
        if (e.which == 13) {
            autoslide *= -1;
        }

    });
})();