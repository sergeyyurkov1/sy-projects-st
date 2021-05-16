/*
Based on https://codepen.io/Grilly86/details/bwAoKq and Daniel Shiffman (https://twitter.com/shiffman)
*/

var canvasDiv = document.getElementById("blobsHome");

var canvasWidth = 300;
var canvasHeight = 300;

var r = (canvasWidth < canvasHeight) ? canvasWidth/4 : canvasHeight/4;

var x_off = 1000,y_off = 1000,z_off = 1000;
var vertices_amount = 200;

var px_offset = r/2;    // amplitude
var NOISE_SCALE = 100;  // the higher the softer

var Z_SPEED = .007;     // noise change per frame

var X_SPEED = 0;
var Y_SPEED = 0;

var prevTime;
var color;

function setup() {
var canvas = createCanvas(canvasWidth, canvasHeight);
canvas.parent("blobsHome")
frameRate(60);

drawingContext.shadowOffsetX = 0;
drawingContext.shadowOffsetY = 20;
drawingContext.shadowBlur = 20;
drawingContext.shadowColor = 'black';
}

function draw() {
colorMode(HSB);

color = (frameCount % 360);

// draw shape:
push();
translate(width/2, height/2);

// background(255);
background("#f5f7f3");
noStroke();
fill(color, 50, 255);

beginShape();
for (var a = 0; a < TWO_PI; a += TWO_PI / vertices_amount) {
    var x = r * sin(a);
    var y = r * cos(a);
    
    var new_x = x + (
                noise(
        ((x_off+x)/NOISE_SCALE),
        ((y_off+y)/NOISE_SCALE),
            z_off) * px_offset * sin(a));
    
    var new_y = y + (
                noise(
        ((x_off+x)/NOISE_SCALE),
        ((y_off+y)/NOISE_SCALE),
            z_off) * px_offset * cos(a))
    vertex(new_x,new_y);
}
endShape();

pop();

// update NOISE offsets
z_off += Z_SPEED;
x_off += X_SPEED;
y_off += Y_SPEED;

};

// Only for Streamlit
// Imports external JS library
var element = document.getElementById("blobsHome");
var ext_script = document.createElement('script');
ext_script.src = 'https://cdn.jsdelivr.net/npm/p5@1.3.1/lib/p5.min.js';
element.parentNode.insertBefore(ext_script, element);