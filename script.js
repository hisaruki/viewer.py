(function () {
    var gt = 0;
    var moving = null;
    var resize = function () {
        var y = $(window).height();
        $("img").css("display", "inline-flex");
        var x = $("[data-first]").width();
        x = Math.ceil(x);
        $("img.dummy").css("width", x + "px");
        if (moving) {
            clearInterval(moving);
            moving = null;
        }
        focus($("img").eq(gt));
    }

    var speed = 10;

    var get_gt_as_is = function(){
        var lefts = []
        $("img").each(function(){
            var left = $(this)[0].getBoundingClientRect().left;
            left = Math.ceil(left);
            left = Math.abs(left)
            lefts.push(left);
        });
        return lefts.indexOf(Math.min.apply(null, lefts));
    }

    var focus = function (obj, linear) {
        if (moving) {
            clearInterval(moving);
            moving = null;
        }
        var left = obj[0].getBoundingClientRect().left;
        left = Math.ceil(left);
        var target = 0;
        if ($("#centering").hasClass("active")) {
            target = Math.ceil($(window).width() / 2);
        }

        var go = -1;
        if (left > target) {
            go = go * -1;
        }

        moving = setInterval(function () {
            x = $("article").css("right");
            x = x.replace("px", "") - 0
            left = obj[0].getBoundingClientRect().left
            left = Math.ceil(left);
            distance = Math.abs(target - left);

            if (distance > 16 && !linear) {
                go = go / Math.abs(go);
                go *= distance / 16;
            } else {
                go = go / Math.abs(go);
            }
            if (linear > 0) {
                gt = get_gt_as_is();
            }
            $("#gt").text(gt + 1);
            $("article").css("right", x + go);
            if (!distance) {
                clearInterval(moving);
                moving = null;
            }
        }, speed);
        $("#gt").text(gt + 1);
    }

    $("#tp").text($("img").length);

    $(window).on("resize load", function () {
        resize();
    });
    $("img").eq(0).attr("data-first", 1);
    resize();

    var slideshow = -1;
    setInterval(function () {
        if (slideshow > 0 && !moving) {
            if (gt == $("img").length - 1) {
                focus($("img").eq(0), false);
            } else {
                focus($("img").eq($("img").length - 1), true);
            }
        }
    }, 100);

    var autopage = -1;
    var apseq = 1;
    setInterval(function () {
        if (autopage > 0 && !moving) {
            apseq++;
            if( (apseq / speed) == Math.ceil(apseq / speed) ){
                gt += 1;
                if (gt >= $("img").length) {
                    gt = 0;
                }
                focus($("img").eq(gt));
            }
        }
    }, 100);


    $("#speed").on("click", function () {
        speed = speed / 2;
        if(speed > 1){
            speed = Math.ceil(speed);
        }else{
            speed = 30;
        }
        $("var", this).text(Math.ceil(speed));
        $("span", this).text("x" + (10 / speed));
        if (slideshow > 0 && moving) {
            clearInterval(moving);
            moving = null;
        }
    });

    $("#centering").on("click", function () {
        $(this).toggleClass("active");
        focus($("img").eq(gt));
    })

    $("#flex-direction").on("click", function () {
        var options = [
            "row-reverse",
            "row",
            "column",
            "column-reverse"
        ];
        var v = $(this).text();
        var i = options.indexOf(v);
        if(i+1 < options.length){
            v = options[i+1];
        }else{
            v = options[0];
        }
        $(this).text(v);
        $("article").css("flex-direction", v)
        focus($("img").eq(gt));
    })

    $(document).on("keypress", function (e) {
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
            if (autopage > 0 && moving) {
                clearInterval(moving);
                moving = null;
            }
            autopage = autopage * -1;
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
        //j
        if (e.which == 106) {
            gt += 1;
            if (gt >= $("img").length) {
                gt = 0;
            }
            focus($("img").eq(gt));
        }
        //k
        if (e.which == 107) {
            gt -= 1;
            if (gt < 0) {
                gt = $("img").length - 1;
            }
            focus($("img").eq(gt));
        }
        //h
        if (e.which == 104) {
        }
        //l
        if (e.which == 108) {
        }


    });


})();