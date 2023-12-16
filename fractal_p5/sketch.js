function drawCircle(x, y, radius) {
  ellipse(x, y, radius, radius);
 
  if( radius > 1 ) {
    radius *= map(mouseX, 0, width, 0.2, 0.9);
    drawCircle(x, y, radius);
  }
}
 
function setup() {
  createCanvas(600,600);
}
 
function draw() {
  background(220);
  translate(width/2, height/2);
  drawCircle(0,0,500);
  
}