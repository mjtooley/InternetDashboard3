// Based on LeafletPlayback slider

/**
 * Initializes the slider with the input options
 * and callback
 *
 * @param options
 * @param callback
 */
function Slider(options, callback) {
    this.options = options;
    this.callback = callback;
    this.initialize();
}

Slider.prototype = {
    initialize: function () {
        this._callbacksList = [];
        if (this.callback) {
            this.addCallback(this.callback);
        }
        this._startTime = Date.parse(this.options.startTime);
        this._endTime = Date.parse(this.options.endTime);
        this._originalSpeed = this.options.speed;
        this._speed = this._originalSpeed;
        this._tickLen = this.options.tickLen;
        this._cursor = this._startTime;
        this._transitionTime = this._tickLen / this._speed;
    },

    /**
     * Returns the input Unix date as a date string
     *
     * @param date
     * @returns string
     */
    DateStr: function (date) {
        return new Date(date).toDateString();
    },

    /**
     * Returns the time of the input Unix date as a string
     *
     * @param time
     * @returns string
     */
    TimeStr: function (time) {
        var d = new Date(time);
        var h = d.getHours();
        var m = d.getMinutes();
        var s = d.getSeconds();
        var tms = time / 1000;
        var dec = (tms - Math.floor(tms)).toFixed(2).slice(1);
        var mer = "AM";
        if (h > 11) {
            h %= 12;
            mer = "PM";
        }
        if (h === 0) h = 12;
        if (m < 10) m = "0" + m;
        if (s < 10) s = "0" + s;
        return h + ":" + m + ":" + s + dec + " " + mer;
    },

    /**
     * Called while the slider is playing. Updates the calendar and
     * time and moves the cursor.
     */
    _tick: function (self) {
        if (self._cursor > self._endTime) {
            self._cursor = self._startTime;
        }
        var date = new Date(self.getTime());
        $("#calendar").datepicker("setDate", date);
        $("#timepicker").timepicker("setTime", date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds());
        self._cursor += self._tickLen;
    },

    /**
     * Called each time the cursor is moved
     *
     * @param cursor
     */
    _callbacks: function (cursor) {
        $("#cursor-date").html(slider.DateStr(cursor));
        $("#cursor-time").html(slider.TimeStr(cursor));
        $("#time-slider").slider("value", cursor);
        var callbacks = this._callbacksList;
        for (var i = 0; i < callbacks.length; i++) {
            callbacks[i](cursor);
        }
    },

    addCallback: function (fn) {
        this._callbacksList.push(fn);
    },

    start: function () {
        if (this._intervalID) {
            return;
        }
        this._intervalID = window.setInterval(this._tick, this._transitionTime, this);
    },

    stop: function () {
        if (!this._intervalID) {
            return;
        }
        clearInterval(this._intervalID);
        this._intervalID = null;
    },

    getSpeed: function () {
        return this._speed / this._originalSpeed;
    },

    isPlaying: function () {
        return this._intervalID ? true : false;
    },

    setSpeed: function (speed) {
        this._speed = speed * this._originalSpeed;
        this._transitionTime = this._tickLen / this._speed;
        if (this._intervalID) {
            this.stop();
            this.start();
        }
    },

    /**
     * Sets the cursor to the input value and passes that value to the
     * callback functions
     *
     * @param ms
     */
    setCursor: function (ms) {
        var time = parseInt(ms);
        if (!time) {
            return;
        }
        this._cursor = time;
        this._callbacks(this._cursor);
    },

    getTime: function () {
        return this._cursor;
    },

    getStartTime: function () {
        return this._startTime;
    },

    getEndTime: function () {
        return this._endTime;
    },

    getTickLen: function () {
        return this._tickLen;
    }
};

/**
 * Initializes the SliderControls and associates them with the
 * input slider
 *
 * @param slider
 */
function SliderControls(slider){
    this.initialize(slider);
}

SliderControls.prototype = {
    initialize: function(slider) {
        this._setup(slider);
        return document.createElement("div");
    },

    /**
     * Sets up the SliderControls to work with the input slider
     *
     * @param slider
     */
    _setup: function(slider) {
        var self = this;
        $("#play-pause").click(function() {
            var playPauseIcon = $("#play-pause-icon");
            if (slider.isPlaying() === false) {
                slider.start();
                playPauseIcon.removeClass("fa-play");
                playPauseIcon.addClass("fa-pause");
            } else {
                slider.stop();
                playPauseIcon.removeClass("fa-pause");
                playPauseIcon.addClass("fa-play");
            }
        });

        var startTime = slider.getStartTime();
        $("#cursor-date").html(slider.DateStr(startTime));
        $("#cursor-time").html(slider.TimeStr(startTime));

        $("#time-slider").slider({
            min: slider.getStartTime(),
            max: slider.getEndTime(),
            step: slider.getTickLen(),
            value: slider.getTime(),
            slide: function(event, ui) {
                var date = new Date(ui.value);
                $("#calendar").datepicker("setDate", date);
                $("#timepicker").timepicker("setTime", date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds());
            }
        });

        $("#speed-slider").slider({
            min: -9,
            max: 9,
            step: .1,
            value: self._speedToSliderVal(slider.getSpeed()),
            orientation: "vertical",
            slide: function( event, ui ) {
                var speed = self._sliderValToSpeed(parseFloat(ui.value));
                slider.setSpeed(speed);
                $(".speed").html(speed).val(speed);
            }
        });

        $("#speed-input").on("keyup", function(e) {
            var speed = parseFloat($("#speed-input").val());
            if (!speed) { return; }
            slider.setSpeed(speed);
            $("#speed-slider").slider("value", self._speedToSliderVal(speed));
            $("#speed-icon-val").html(speed);
            if (e.keyCode === 13) {
                $(".speed-menu").dropdown("toggle");
            }
        });

        $("#calendar").datepicker({
            changeMonth: true,
            changeYear: true,
            minDate: new Date(slider.getStartTime()),
            maxDate: new Date(slider.getEndTime()),
            altField: "#date-input",
            altFormat: "mm/dd/yy",
            defaultDate: new Date(slider.getStartTime()),
            onSelect: function(d) { // New calendar date selected
                var date = new Date(d);
                var time = $("#timepicker").data("timepicker");
                var ts = self._combineDateAndTime(date, time);
                slider.setCursor(ts);
                $("#time-slider").slider("value", ts);
            }
        });

        $("#date-input").on("change", function() { // New calendar date input
            $("#calendar").datepicker("setDate", $("#date-input").val());
            var date = new Date($("#calendar").datepicker("getDate"));
            var time = $("#timepicker").data("timepicker");
            var ts = self._combineDateAndTime(date, time);
            slider.setCursor(ts);
            $("#time-slider").slider("value", ts);
        });

        $(".dropdown-menu").on("click", function(e) {
            e.stopPropagation();
        });

        $("#timepicker").timepicker({
            showSeconds: true
        });

        $("#timepicker").timepicker().on("changeTime.timepicker", function(e) { // Time is changed or new time is input
            var date = $("#calendar").datepicker("getDate");
            var time = e.time;
            var ts = self._combineDateAndTime(date, time);
            slider.setCursor(ts);
            $("#time-slider").slider("value", ts);
        });
    },

    _speedToSliderVal: function(speed) {
        if (speed < 1) {
            return -10 + speed * 10;
        }
        return speed - 1;
    },

    _sliderValToSpeed: function(val) {
        if (val < 0) {
            return parseFloat((1+val/10).toFixed(2));
        }
        return val + 1;
    },

    /**
     * Combines the input date and time
     *
     * @param date
     * @param time
     * @returns Unix date
     */
    _combineDateAndTime: function(date, time) {
        var yr = date.getFullYear();
        var mo = date.getMonth();
        var dy = date.getDate();
        var hr = time.hour;
        if (time.meridian === "PM" && hr !== 12) {
            hr += 12;
        }
        if (time.meridian === "AM" && hr == 12) {
            hr = 0;
        }
        var min = time.minute;
        var sec = time.second;
        return new Date(yr, mo, dy, hr, min, sec).getTime();
    }
};