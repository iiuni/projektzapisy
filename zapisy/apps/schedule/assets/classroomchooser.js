import "jquery";
const $ = jQuery;

var scroll = function(id) {
    $('html, body').animate({
        scrollTop: $(id).offset().top
    }, 0);
};

const reservationData = JSON.parse($("#reservation-data")[0].innerHTML);



function relMouseCoords(evt) {
    var rect = this.getBoundingClientRect();
    return {
        x:evt.clientX - rect.left,
        y:evt.clientY - rect.top
    };
}
HTMLCanvasElement.prototype.relMouseCoords = relMouseCoords;

var chosenbutton = new Image();
chosenbutton.src = reservationData.imageChoose;


var AjaxWrapper = function () {
    this.makeURL = function (date) {
        var s = date.split('-');
        return '/classrooms/terms/' + s[0] + '/' + s[1] + '/' + s[2] + '/';
    };
    this.cache = {};
};

AjaxWrapper.prototype.getJson = function (date, callback) {

    if (this.cache.hasOwnProperty(date)) {
        callback.call(this.cache[date], this.cache[date]);
        return;
    }

    var url = this.makeURL(date),
            that = this;
    var r = new XMLHttpRequest();

    r.open("GET", url, true);
    r.onreadystatechange = function () {
        if (r.readyState != 4 || r.status != 200) return; //error
        that.cache[date] = JSON.parse(r.responseText);
        callback.call(that.cache[date], that.cache[date]);

    };
    r.send('');
};


var ReservationView = function () {


    var container = document.getElementById('addTermForm');
    var canvas = document.getElementById('can');

    var Ajax = new AjaxWrapper();
    var rooms = new ClassroomsList();

    var changeType = function () {
        var type = document.getElementById('id_type'),
                subject = document.getElementById('form_course'),
                visible = document.getElementById('form_visible'),
                title = document.getElementById('form_title'),
                message = document.getElementById('sendmessage_visible'),
                onchange = function () {
                    switch (type.value) {
                        case '0':
                        case '1':
                            $(subject).show();
                            $(title).hide();
                            $(visible).hide();
                            $('#id_course').attr('required', true);
                            $('#id_title').attr('required', false);
                            break;

                        case '2':
                            $(subject).hide();
                            $(title).show();
                            $(visible).show();
                            $('#id_course').attr('required', false);
                            $('#id_title').attr('required', true);
                            break;
                    }
                }
                ;
        if (type) {
            type.addEventListener('change', onchange, true);
            onchange();
        }
    };

    canvas.addEventListener('click', function(event) {
        rooms.click(event, function(item) {
            $('#inputplace').val('')
            $('#hiddenroom').val(item.id);
            $('#location').val('Sala ' + item.title);
            scroll('#location');
        });
    }, true);

    $('#term').change(function (event) {
        if (!($(this).val() === '')) {
            loadTerms($('#term').val());
        }
    });

    var loadTerms = function (value) {
        Ajax.getJson(value, function (data) {
            rooms.load(data);
            rooms.setLines($('#begin').val(), $('#end').val());
            rooms.draw();
        });
    };

    $('.timepicker').change(function () {
        rooms.setLines($('#begin').val(), $('#end').val());
        rooms.draw();
    });


    $('#filteroccupated').change(function () {
        rooms.draw();

    });

    changeType();
};


var Classroom = function (ctx, item) {
            var config = {
                        width:400,
                        height:30,
                        corner:10,
                        boxheight:65,
                        x1:120,
                        y1:30,
                        y1a:30,
                        calculate:function () {
                            /*
                             a******b
                             e        g
                             *        *
                             f        h
                             c******d

                             for example b-g is rounded corner
                             a - (x1, y1)
                             b - (x2, y1)
                             c - (x2, y2)
                             d - (x2, y2)
                             e - (x1corner, y1corner)
                             f - (x1corner, y2corner)
                             g - (x2corner, y1corner)
                             h - (x2corner, y2corner)

                             */
                            this.x2 = this.x1 + this.width;
                            this.y2 = this.y1 + this.height;
                            this.x1corner = this.x1 - this.corner;
                            this.x2corner = this.x2 + this.corner;
                            this.y1corner = this.y1 + this.corner;
                            this.y2corner = this.y2 - this.corner;
                            this.strokeStyle = ctx.strokeStyle;
                            this.evenHours = ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'];
                            var that = this;

                            var getPixel = function (hour) {
                                /*
                                 Find pixel location for time (clock).
                                 Eg. 8:00 - it's begining of axe, 22:00 - end,
                                 15:00 - it's center.
                                 */
                                var cellSize = that.width / (that.evenHours.length - 1);
                                var time = hour.split(":"),
                                        hours = (parseInt(time[0]) - 8) * cellSize / 2,
                                        minutes = Math.floor(( parseInt(time[1]) / 60 ) * cellSize) / 2;
                                return hours + minutes;
                            };
                            this.terms = [];
                            for (var key in item.terms) {
                                if (item.terms.hasOwnProperty(key)) {
                                    var event = item.terms[key];


                                    let begin = getPixel(event.begin) + this.x1;
                                    let end = getPixel(event.end) + this.x1;
                                    this.terms.push({'begin':begin, 'end':end});
                                }
                            }

                            return this;
                        },
                        init:function () {
                            this.calculate();
                            delete this.init;
                            return this;
                        }
                    }.init(),

                    cellSize = config.width / (config.evenHours.length - 1),

                    drawButton = function () {

                        if ( reservationData.canManageEvents || is_free()) {
                            ctx.drawImage(chosenbutton, config.x1 - 100, config.y1 + 1);
                        }
                    },

                    drawTitle = function () {
                        ctx.beginPath();
                        var save = ctx.font;
                        ctx.strokeStyle = config.strokeStyle;
                        ctx.font = '20px Calibri';
                        ctx.fillText(item.title + ' pojemność: ' + item.capacity + ', ' + item.type, config.x2corner + 10, config.y1 + 3 * config.height / 4);
                        ctx.stroke();
                        ctx.font = save;

                    },

                    drawBorder = function () {
                        /*
                         Draw borders
                         */
                        var c = config,
                                save = ctx.strokeStyle;
                        ctx.beginPath();
                        ctx.moveTo(c.x1, c.y1);
                        ctx.lineTo(c.x2, c.y1);
                        ctx.quadraticCurveTo(c.x2corner, c.y1, c.x2corner, c.y1corner);
                        ctx.lineTo(c.x2corner, c.y2corner);
                        ctx.quadraticCurveTo(c.x2corner, c.y2, c.x2, c.y2);
                        ctx.lineTo(c.x1, c.y2);
                        ctx.quadraticCurveTo(c.x1corner, c.y2, c.x1corner, c.y2corner);
                        ctx.lineTo(c.x1corner, c.y1corner);
                        ctx.quadraticCurveTo(c.x1corner, c.y1, c.x1, c.y1);
                        ctx.stroke();

                        ctx.strokeStyle = save;
                    },

                    drawHours = function () {
                        var saveStroke = ctx.strokeStyle,
                                saveAlign = ctx.textAlign,
                                saveFont = ctx.font;
                        ctx.beginPath();
                        ctx.strokeStyle = "#787878";
                        ctx.textAlign = "left";
                        ctx.font = '12px Calibri';

                        for (var i = 0; i < config.evenHours.length; ++i) {
                            var x = config.x1 + i * cellSize;
                            ctx.moveTo(x, config.y1);
                            ctx.lineTo(x, config.y2);
                            ctx.fillText(config.evenHours[i], x - 14, config.y2 + 12);

                        }
                        ctx.stroke();
                        ctx.strokeStyle = saveStroke;
                        ctx.textAlign = saveAlign;
                        ctx.font = saveFont;
                    },


                    drawEvents = function () {
                        var saveStyle = ctx.fillStyle;
                        for (var key in config.terms) {
                            if (config.terms.hasOwnProperty(key)) {
                                var event = config.terms[key];
                                ctx.beginPath();
                                ctx.fillStyle = "#b0c2f7";
                                ctx.globalAlpha = 0.5; // Half opacity
                                ctx.fillRect(event.begin, config.y1, event.end - event.begin, config.height);
                                ctx.stroke();
                                ctx.globalAlpha = 1;
                            }
                        }
                        ctx.fillStyle = saveStyle;
                    },

                    draw = function (index) {

                        config.y1 = config.y1a + index * config.boxheight;
                        config.calculate();
                        drawButton();
                        drawTitle();
                        drawBorder();
                        drawHours();
                        drawEvents();
                    },

                    getPixel = function (hour) {
                        /*
                         Find pixel location for time (clock).
                         Eg. 8:00 - it's begining of axe, 22:00 - end,
                         15:00 - it's center.
                         */

                        var time = hour.split(":"),
                                hours = (parseInt(time[0]) - 8) * cellSize / 2,
                                minutes = Math.floor(( parseInt(time[1]) / 60 ) * cellSize) / 2;
                        return hours + minutes;
                    },

                    click = function (event, cordinates, callback) {
                        if (!reservationData.canManageEvents && !is_free()) return;
                        if ((cordinates.x >= config.x1 - 100) && (cordinates.x < config.x1 - 20)
                                && (cordinates.y >= config.y1 + 1) && ( cordinates.y < config.y1 + 32)) {
                            callback.call(item, item);
                        }
                    },
                    lpixel, rpixel,
                    setLimit = function (left, right) {
                        lpixel = left;
                        rpixel = right;
                    },

                    is_free = function (force) {
                        if (!rpixel || !lpixel) {
                            return false;
                        }
                        for (var key in config.terms) {
                            if (config.terms.hasOwnProperty(key)) {
                                var pitem = config.terms[key];
                                if (!(lpixel >= pitem.end || rpixel <= pitem.begin ))
                                {
                                    return false;
                                }
                            }
                        }
                        return true;
                    }
                    ;

            return {
                draw:draw,
                getPixel:function (item) {
                    return getPixel(item) + config.x1;
                },
                shouldBeShow:function (l, r) {
                    setLimit(getPixel(l) + config.x1, getPixel(r) + config.x1);
                    return is_free(true);
                },
                setLimit:setLimit,
                click:click
            }
        },
        ClassroomsList = function () {

            var that = this,
                    init = function () {
                        that.canvas = document.getElementById("can");
                        that.ctx = document.getElementById("can").getContext("2d");
                    },

                    click = function (event, callback) {
                        var cords = that.canvas.relMouseCoords(event);
                        var nr = Math.floor(cords.y / 65);
                        classrooms[ toDraw[nr] ].click(event, cords, callback);
                    },

                    classrooms = [],
                    clearClassrooms = function () {
                        classrooms = [];
                    },
                    createClassroom = function (data) {
                        for (var classroom in data) {

                            if (data.hasOwnProperty(classroom)) {
                                classrooms.push(new Classroom(that.ctx, data[classroom]));
                            }
                        }
                    },

                    lineFrom, lineTo,
                    setLines = function (from, to) {
                        lineFrom = from;
                        lineTo = to;
                    },

                    redraw = function () {

                    },
                    toDraw,
                    draw = function () {
                        var index = 0;
                        toDraw = [];

                        for (var classroom in classrooms) {
                            if (classrooms.hasOwnProperty(classroom) && (shouldBeShow(classrooms[classroom]) || $('#filteroccupated').prop('checked') )) {
                                toDraw[index] = classroom;
                                index++;
                            }
                        }
                        that.canvas.height = 65 * (index + .5);

                        index = 0;
                        var lPixel, rPixel;
                        for (var c in toDraw) {
                            if (toDraw.hasOwnProperty(c)) {
                                if (index === 0) {
                                    if (lineFrom) {
                                        lPixel = classrooms[toDraw[c]].getPixel(lineFrom);

                                    }
                                    if (lineTo) {
                                        rPixel = classrooms[toDraw[c]].getPixel(lineTo);
                                    }
                                }
                                classrooms[toDraw[c]].setLimit(lPixel, rPixel);
                                classrooms[toDraw[c]].draw(index++);
                            }
                        }

                        if (lPixel) {
                            that.ctx.strokeStyle = "red";
                            that.ctx.beginPath();
                            that.ctx.moveTo(lPixel, 0);
                            that.ctx.lineTo(lPixel, that.canvas.height);
                            that.ctx.stroke();
                        }

                        if (rPixel) {
                            that.ctx.strokeStyle = "red";
                            that.ctx.beginPath();
                            that.ctx.moveTo(rPixel, 0);
                            that.ctx.lineTo(rPixel, that.canvas.height);
                            that.ctx.stroke();
                        }
                    },

                    shouldBeShow = function (classroom) {
                        var r = classroom.shouldBeShow(lineFrom, lineTo);
                        return r;
                    },
                    load = function (data) {
                        clearClassrooms();
                        createClassroom(data);
                    }
                    ;

            init();

            return {
                'draw':draw,
                'load':load,
                'setLines':setLines,
                'redraw':redraw,
                'click':click
            };

        },


        cleanAddTermForm = function () {
        },


        init = function () {
            addterm();
        };

$(document).ready(() => {
    ReservationView();
    $('#term').change();
});
