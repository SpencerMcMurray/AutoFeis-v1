INSIDE = 10;
CAN_CONNECT = 100;
MAX_LINE_WEIGHT = 200;
FONT_MULTIPLIER = 12;
SUBFONT_DIFF_FACTOR = 8/2;
TITLE_FONT_SIZE = 96;
OFFSCREEN_OFFSET = 10;

MAX_CONN = 5;
VEL_MAX = 1;
VEL_MIN = 0.5;
ACC_MAX = 0.01;
ACC_MIN = 0.001;
SIZE_MIN = 1;
SIZE_MAX = 2;
STROKE_MIN = 150;

BACKGROUND = 50;

function setup() {
	fontOswald = loadFont('../static/fonts/Oswald-Regular.ttf');
    var canvas = createCanvas(document.getElementById('sketch').clientWidth, document.getElementById('sketch').clientHeight);
    canvas.style('display', 'block');
    canvas.parent('sketch');
	NUM_DOTS = (width / 20);
	dots = [];
	for(i = 0; i < NUM_DOTS; i++) {
		dots[i] = new Dot();
	}
}

function draw() {
  	background(BACKGROUND);
	for(i = 0; i < dots.length; i++) {
		dots[i].render();
		dots[i].update();
		if(dots[i].isOffScreen()) {
			dots[i] = new Dot();
		}
		// Updates all connections for the dot at idx, makes sure not to connect to itself
		for(j = 0; j < dots.length; j++) {
			if(j !== i) {
				dots[i].connect(dots[j]);
			}
		}
	}
	// Font size adjusts with screen size
	fontSize = Math.floor(Math.log(width)/Math.log(10)) * FONT_MULTIPLIER;
	stroke(MAX_LINE_WEIGHT + BACKGROUND);
	fill(MAX_LINE_WEIGHT + BACKGROUND);
	textSize(fontSize * SUBFONT_DIFF_FACTOR);
	textFont(fontOswald);
	textAlign(CENTER);
	text('AutoFeis', width / 2, height / 2);
	textSize(fontSize);
	text('The New Way To Tabulate', width / 2, height / 1.75);
}

function windowResized() {
	resizeCanvas(document.getElementById('sketch').clientWidth, document.getElementById('sketch').clientHeight);
}

// Gets a random number in range(-M, M), avoiding range(-m, m)
function randomAvoidZero(m, M) {
	nums = [random(-M, m), random(m, M)];
	return nums[round(random(1))];
}

// Squishes n between 0 and MAX_LINE_WEIGHT; Dependent on the background
function squish(n) {
	return ((BACKGROUND - MAX_LINE_WEIGHT) * n / CAN_CONNECT) + MAX_LINE_WEIGHT
}

// Dot object
function Dot() {
	this.pos = createVector(random(INSIDE, width - INSIDE), random(INSIDE, height - INSIDE));
	this.size = random(SIZE_MIN, SIZE_MAX);
	this.vel = createVector(randomAvoidZero(VEL_MIN, VEL_MAX), randomAvoidZero(VEL_MIN, VEL_MAX));
	this.acc = createVector(randomAvoidZero(ACC_MIN, ACC_MAX), randomAvoidZero(ACC_MIN, ACC_MAX));
	this.stroke = random(STROKE_MIN, 255);

	this.connect = function(dot) {
		dif = createVector(this.pos.x - dot.pos.x, this.pos.y - dot.pos.y);
		mag = dif.mag();
		if(mag < CAN_CONNECT) {
			stroke(squish(mag));
			line(this.pos.x, this.pos.y, dot.pos.x, dot.pos.y);
		}
	};

	this.render = function() {
		fill(this.stroke);
		stroke(this.stroke);
		ellipse(this.pos.x, this.pos.y, this.size, this.size);
	};

	this.boost = function() {
		this.vel.add(this.acc);
	};

	this.update = function() {
		if(this.vel.mag() < 1){
			this.boost();
		}
		this.pos.add(this.vel);
	};

	this.isOffScreen = function() {
		return (this.pos.x > OFFSCREEN_OFFSET + width + this.size / 2 || this.pos.y > OFFSCREEN_OFFSET + height +
				this.size / 2 || OFFSCREEN_OFFSET + this.pos.x + this.size / 2 < 0 || OFFSCREEN_OFFSET + this.pos.y +
				this.size / 2 < 0);
	};
}