function setup() {
  createCanvas(400, 400);
  angleMode(DEGREES); // Defina o modo de ângulo para graus
}

function draw() {
  background(220);
  translate(width / 2, height / 2); // Mova a origem para o centro do canvas
  rotate(-90); // Gire para que o ângulo 0 seja na parte superior

  

  let agora = new Date();
  let horas = agora.getHours();
  let minutos = agora.getMinutes();
  let segundos = agora.getSeconds();

  // Desenhe o ponteiro de horas
  let anguloHoras = map(horas % 12, 0, 12, 0, 360) + map(minutos, 0, 60, 0, 30);
  stroke(255, 0, 0);
  strokeWeight(8);
  line(0, 0, 100 * cos(anguloHoras), 100 * sin(anguloHoras));

  // Desenhe o ponteiro de minutos
  let anguloMinutos = map(minutos, 0, 60, 0, 360);
  stroke(0, 0, 255);
  strokeWeight(4);
  line(0, 0, 120 * cos(anguloMinutos), 120 * sin(anguloMinutos));

  // Desenhe o ponteiro de segundos
  let anguloSegundos = map(segundos, 0, 60, 0, 360);
  stroke(0, 255, 0);
  strokeWeight(2);
  line(0, 0, 140 * cos(anguloSegundos), 140 * sin(anguloSegundos));

  // Desenhe o círculo central
  fill(0);
  noStroke();
  ellipse(0, 0, 10, 10);

  noFill();
  stroke(0);
  ellipse(0, 0, 300, 300);
}
